from datetime import UTC, datetime
from pathlib import Path

from f1_data.jolpica import JolpicaAPIError, JolpicaClient
from f1_data.models import Race
from f1_data.storage import parquet_exists, write_parquet
from f1_data.transformers import (
    constructors_to_records,
    drivers_to_records,
    races_to_records,
    results_to_records,
)

SEASON = 2026

def process_reference_data(
    client: JolpicaClient,
    season: int,
    bucket: str | None = None,
) -> list[Race]:
    races = client.get_races(season)
    drivers = client.get_drivers(season)
    constructors = client.get_constructors(season)

    write_parquet(
        races_to_records(races),
        Path(f"processed/{season}/races.parquet"),
        bucket=bucket,
    )

    write_parquet(
        drivers_to_records(drivers),
        Path(f"processed/{season}/drivers.parquet"),
        bucket=bucket,
    )

    write_parquet(
        constructors_to_records(constructors),
        Path(f"processed/{season}/constructors.parquet"),
        bucket=bucket,
    )

    return races

def process_race_results(
    client: JolpicaClient,
    races: list[Race],
    season: int,
    results_prefix: Path,
    bucket: str | None = None,
) -> None:
    for race in races:
        try:
            print(f"Processing round {race.round}: {race.name}")

            if race.date > datetime.now(UTC).date():
                print("  ○ Race has not happened yet")
                continue

            result_key = results_prefix / f"round={race.round}.parquet"

            if parquet_exists(result_key, bucket):
                print("  ○ Results already exist, skipping")
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

            print(f"  ✓ Written {len(records)} results")

        except JolpicaAPIError as exc:
            print(f"  ✗ Failed round {race.round}: {exc}")

def run_pipeline(bucket: str | None = None) -> None:
    client = JolpicaClient()

    results_prefix = Path(f"processed/{SEASON}/results")

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