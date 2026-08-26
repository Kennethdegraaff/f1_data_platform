import os
from datetime import UTC, datetime
from pathlib import Path

from f1_data.catalog import (
    add_constructor_standings_partition,
    add_driver_standings_partition,
    add_reference_partition,
    add_results_partition,
    add_sprint_partition,
)
from f1_data.jolpica import JolpicaAPIError, JolpicaClient
from f1_data.models import Race
from f1_data.storage import parquet_exists, write_parquet
from f1_data.transformers import (
    constructor_standings_to_records,
    constructors_to_records,
    driver_standings_to_records,
    drivers_to_records,
    races_to_records,
    results_to_records,
    sprint_results_to_records,
)


def resolve_season(season: int | None) -> int:
    return season if season is not None else datetime.now(UTC).year


def process_reference_data(
    client: JolpicaClient,
    season: int,
    bucket: str,
    database_name: str,
) -> list[Race]:
    races = client.get_races(season)
    drivers = client.get_drivers(season)
    constructors = client.get_constructors(season)

    write_parquet(
        races_to_records(races),
        Path(f"data_collected/races/season={season}/races.parquet"),
        bucket=bucket,
    )

    write_parquet(
        drivers_to_records(drivers),
        Path(f"data_collected/drivers/season={season}/drivers.parquet"),
        bucket=bucket,
    )

    write_parquet(
        constructors_to_records(constructors),
        Path(
            f"data_collected/constructors/"
            f"season={season}/constructors.parquet"
        ),
        bucket=bucket,
    )

    for dataset in ("races", "drivers", "constructors"):
        add_reference_partition(
            dataset,
            season,
            bucket,
            database_name,
        )

    return races


def process_race_results(
    client: JolpicaClient,
    races: list[Race],
    season: int,
    results_prefix: Path,
    bucket: str,
    database_name: str,
) -> None:
    for race in races:
        try:
            print(f"Processing round {race.round}: {race.name}")

            if race.date > datetime.now(UTC).date():
                print("  ○ Race has not happened yet")
                continue

            result_key = (
                results_prefix
                / f"round={race.round}"
                / "race_results.parquet"
            )

            print(f"Checking result key: {result_key}")

            if parquet_exists(result_key, bucket):
                print(
                    f"  ○ Results already exist at {result_key}, "
                    "ensuring Glue partition"
                )

                add_results_partition(
                    season=season,
                    round_number=race.round,
                    bucket=bucket,
                    database_name=database_name,
                )
                continue

            results = client.get_results(season, race.round)

            if not results:
                print("  ○ No results available yet")
                continue

            records = results_to_records(results)

            write_parquet(
                records,
                result_key,
                bucket=bucket,
            )

            add_results_partition(
                season=season,
                round_number=race.round,
                bucket=bucket,
                database_name=database_name,
            )

            print(f"  ✓ Written {len(records)} results")

        except JolpicaAPIError as exc:
            print(f"  ✗ Failed round {race.round}: {exc}")


def process_sprint_results(
    client: JolpicaClient,
    races: list[Race],
    season: int,
    sprint_prefix: Path,
    bucket: str,
    database_name: str,
) -> None:
    for race in races:
        try:
            print(
                f"Processing sprint for round "
                f"{race.round}: {race.name}"
            )

            if race.date > datetime.now(UTC).date():
                print("  ○ Race has not happened yet")
                continue

            sprint_key = (
                sprint_prefix
                / f"round={race.round}"
                / "sprint_results.parquet"
            )

            if parquet_exists(sprint_key, bucket):
                print(
                    f"  ○ Sprint already exists at {sprint_key}, "
                    "ensuring Glue partition"
                )

                add_sprint_partition(
                    season=season,
                    round_number=race.round,
                    bucket=bucket,
                    database_name=database_name,
                )
                continue

            sprint_results = client.get_sprint_results(
                season,
                race.round,
            )

            if not sprint_results:
                print("  ○ No sprint results for this round")
                continue

            records = sprint_results_to_records(sprint_results)

            write_parquet(
                records,
                sprint_key,
                bucket=bucket,
            )

            add_sprint_partition(
                season=season,
                round_number=race.round,
                bucket=bucket,
                database_name=database_name,
            )

            print(f"  ✓ Written {len(records)} sprint results")

        except JolpicaAPIError as exc:
            print(
                f"  ✗ Failed sprint for round {race.round}: {exc}"
            )


def process_driver_standings(
    client: JolpicaClient,
    races: list[Race],
    season: int,
    standings_prefix: Path,
    bucket: str,
    database_name: str,
) -> None:
    for race in races:
        try:
            if race.date > datetime.now(UTC).date():
                continue

            standings_key = (
                standings_prefix
                / f"season={season}"
                / f"round={race.round}"
                / "driver_standings.parquet"
            )

            if parquet_exists(standings_key, bucket):
                add_driver_standings_partition(
                    season,
                    race.round,
                    bucket,
                    database_name,
                )
                continue

            standings = client.get_driver_standings(
                season,
                race.round,
            )

            if not standings:
                continue

            records = driver_standings_to_records(standings)

            write_parquet(
                records,
                standings_key,
                bucket=bucket,
            )

            add_driver_standings_partition(
                season,
                race.round,
                bucket,
                database_name,
            )

        except JolpicaAPIError as exc:
            print(f"  ✗ Failed driver standings: {exc}")


def process_constructor_standings(
    client: JolpicaClient,
    races: list[Race],
    season: int,
    standings_prefix: Path,
    bucket: str,
    database_name: str,
) -> None:
    for race in races:
        try:
            if race.date > datetime.now(UTC).date():
                continue

            standings_key = (
                standings_prefix
                / f"season={season}"
                / f"round={race.round}"
                / "constructor_standings.parquet"
            )

            if parquet_exists(standings_key, bucket):
                add_constructor_standings_partition(
                    season,
                    race.round,
                    bucket,
                    database_name,
                )
                continue

            standings = client.get_constructor_standings(
                season,
                race.round,
            )

            if not standings:
                continue

            records = constructor_standings_to_records(standings)

            write_parquet(
                records,
                standings_key,
                bucket=bucket,
            )

            add_constructor_standings_partition(
                season,
                race.round,
                bucket,
                database_name,
            )

        except JolpicaAPIError as exc:
            print(f"  ✗ Failed constructor standings: {exc}")


def run_pipeline(
    bucket: str,
    season: int | None = None,
) -> None:
    resolved_season = resolve_season(season)

    database_name = os.environ["ATHENA_DATABASE_NAME"]

    client = JolpicaClient()

    results_prefix = Path(
        f"data_collected/race_results/"
        f"season={resolved_season}"
    )

    sprint_prefix = Path(
        f"data_collected/sprint_results/"
        f"season={resolved_season}"
    )

    driver_standings_prefix = Path(
        "data_collected/driver_standings"
    )

    constructor_standings_prefix = Path(
        "data_collected/constructor_standings"
    )

    races = process_reference_data(
        client,
        resolved_season,
        bucket=bucket,
        database_name=database_name,
    )

    process_race_results(
        client,
        races,
        resolved_season,
        results_prefix,
        bucket=bucket,
        database_name=database_name,
    )

    process_sprint_results(
        client,
        races,
        resolved_season,
        sprint_prefix,
        bucket=bucket,
        database_name=database_name,
    )

    process_driver_standings(
        client,
        races,
        resolved_season,
        driver_standings_prefix,
        bucket=bucket,
        database_name=database_name,
    )

    process_constructor_standings(
        client,
        races,
        resolved_season,
        constructor_standings_prefix,
        bucket=bucket,
        database_name=database_name,
    )