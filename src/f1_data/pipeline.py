from datetime import UTC, datetime
from pathlib import Path

from f1_data.jolpica import JolpicaAPIError, JolpicaClient
from f1_data.models import Race
from f1_data.storage import write_parquet
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
) -> list[Race]:
    races = client.get_races(season)
    drivers = client.get_drivers(season)
    constructors = client.get_constructors(season)

    write_parquet(
        races_to_records(races),
        Path(f"data/processed/{season}/races.parquet"),
    )

    write_parquet(
        drivers_to_records(drivers),
        Path(f"data/processed/{season}/drivers.parquet"),
    )

    write_parquet(
        constructors_to_records(constructors),
        Path(f"data/processed/{season}/constructors.parquet"),
    )

    return races


def process_race_results(
    client: JolpicaClient,
    races: list[Race],
    season: int,
    results_path: Path,
) -> None:
    for race in races:
        try:
            print(f"Processing round {race.round}: {race.name}")

            if race.date > datetime.now(UTC).date():
                print("  ○ Race has not happened yet")
                continue

            result_path = results_path / f"round={race.round}.parquet"

            if result_path.exists():
                print("  ○ Results already exist, skipping")
                continue

            results = client.get_results(season, race.round)

            if not results:
                print("  ○ No results available yet")
                continue

            records = results_to_records(results)

            write_parquet(
                records,
                result_path,
            )

            print(f"  ✓ Written {len(records)} results")

        except JolpicaAPIError as exc:
            print(f"  ✗ Failed round {race.round}: {exc}")

def run_pipeline() -> None:
    client = JolpicaClient()

    results_path = Path(f"data/processed/{SEASON}/results")

    races = process_reference_data(client, SEASON)

    process_race_results(
        client,
        races,
        SEASON,
        results_path,
    )