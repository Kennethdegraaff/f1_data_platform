from datetime import UTC, datetime
from pathlib import Path

from f1_data.catalog import (
    add_constructor_standings_partition,
    add_driver_standings_partition,
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

SEASON = 2026


def process_reference_data(
    client: JolpicaClient,
    season: int,
    bucket: str,
) -> list[Race]:
    races = client.get_races(season)
    drivers = client.get_drivers(season)
    constructors = client.get_constructors(season)

    write_parquet(
        races_to_records(races),
        Path(f"data_collected/{season}/races/races.parquet"),
        bucket=bucket,
    )

    write_parquet(
        drivers_to_records(drivers),
        Path(f"data_collected/{season}/drivers/drivers.parquet"),
        bucket=bucket,
    )

    write_parquet(
        constructors_to_records(constructors),
        Path(f"data_collected/{season}/constructors/constructors.parquet"),
        bucket=bucket,
    )

    return races


def process_race_results(
    client: JolpicaClient,
    races: list[Race],
    season: int,
    results_prefix: Path,
    bucket: str,
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
                / "results.parquet"
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
) -> None:
    for race in races:
        try:
            print(f"Processing sprint for round {race.round}: {race.name}")

            if race.date > datetime.now(UTC).date():
                print("  ○ Race has not happened yet")
                continue

            sprint_key = sprint_prefix / f"round={race.round}" / "sprint.parquet"

            if parquet_exists(sprint_key, bucket):
                print(
                    f"  ○ Sprint already exists at {sprint_key}, "
                    "ensuring Glue partition"
                )
                add_sprint_partition(
                    season=season,
                    round_number=race.round,
                    bucket=bucket,
                )
                continue

            sprint_results = client.get_sprint_results(season, race.round)

            if not sprint_results:
                print("  ○ No sprint results for this round")
                continue

            records = sprint_results_to_records(sprint_results)
            write_parquet(records, sprint_key, bucket=bucket)
            add_sprint_partition(
                season=season,
                round_number=race.round,
                bucket=bucket,
            )
            print(f"  ✓ Written {len(records)} sprint results")

        except JolpicaAPIError as exc:
            print(f"  ✗ Failed sprint for round {race.round}: {exc}")


def process_driver_standings(
    client: JolpicaClient,
    season: int,
    standings_prefix: Path,
    bucket: str,
) -> None:
    try:
        standings = client.get_driver_standings(season)

        if not standings:
            print("No driver standings available yet")
            return

        round_number = standings[0].round
        standings_key = (
            standings_prefix
            / f"season={season}"
            / f"round={round_number}"
            / "driver_standings.parquet"
        )

        if parquet_exists(standings_key, bucket):
            print(
                f"Driver standings for round {round_number} already exist, "
                "ensuring Glue partition"
            )
            add_driver_standings_partition(season, round_number, bucket)
            return

        write_parquet(
            driver_standings_to_records(standings),
            standings_key,
            bucket=bucket,
        )
        add_driver_standings_partition(season, round_number, bucket)
        print(
            f"✓ Written {len(standings)} driver standings for round "
            f"{round_number}"
        )

    except JolpicaAPIError as exc:
        print(f"  ✗ Failed driver standings: {exc}")


def process_constructor_standings(
    client: JolpicaClient,
    season: int,
    standings_prefix: Path,
    bucket: str,
) -> None:
    try:
        standings = client.get_constructor_standings(season)

        if not standings:
            print("No constructor standings available yet")
            return

        round_number = standings[0].round
        standings_key = (
            standings_prefix
            / f"season={season}"
            / f"round={round_number}"
            / "constructor_standings.parquet"
        )

        if parquet_exists(standings_key, bucket):
            print(
                f"Constructor standings for round {round_number} already exist, "
                "ensuring Glue partition"
            )
            add_constructor_standings_partition(season, round_number, bucket)
            return

        write_parquet(
            constructor_standings_to_records(standings),
            standings_key,
            bucket=bucket,
        )
        add_constructor_standings_partition(season, round_number, bucket)
        print(
            f"✓ Written {len(standings)} constructor standings for round "
            f"{round_number}"
        )

    except JolpicaAPIError as exc:
        print(f"  ✗ Failed constructor standings: {exc}")


def run_pipeline(bucket: str) -> None:
    client = JolpicaClient()

    results_prefix = Path(f"data_collected/{SEASON}/results")
    sprint_prefix = Path(f"data_collected/{SEASON}/sprint")
    driver_standings_prefix = Path("data_collected/driver_standings")
    constructor_standings_prefix = Path("data_collected/constructor_standings")

    races = process_reference_data(
        client,
        SEASON,
        bucket=bucket,
    )

    process_race_results(
        client,
        races,
        SEASON,
        results_prefix,
        bucket=bucket,
    )

    process_sprint_results(
        client,
        races,
        SEASON,
        sprint_prefix,
        bucket=bucket,
    )

    process_driver_standings(
        client,
        SEASON,
        driver_standings_prefix,
        bucket=bucket,
    )

    process_constructor_standings(
        client,
        SEASON,
        constructor_standings_prefix,
        bucket=bucket,
    )
