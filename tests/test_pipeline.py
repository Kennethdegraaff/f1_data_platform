from datetime import date
from pathlib import Path
from unittest.mock import Mock

from f1_data.models import Circuit, Race, Result
from f1_data.pipeline import process_race_results


def test_existing_results_are_skipped(tmp_path: Path) -> None:
    client = Mock()

    race = Race(
        season=2026,
        round=1,
        name="Australian Grand Prix",
        date=date(2026, 3, 8),
        circuit=Circuit(
            id="albert_park",
            name="Albert Park Grand Prix Circuit",
            city="Melbourne",
            country="Australia",
            latitude=-37.8497,
            longitude=144.968,
        ),
    )

    results_path = tmp_path / "results"
    results_path.mkdir()

    result_path = results_path / "round=1.parquet"
    result_path.touch()

    process_race_results(
        client,
        [race],
        2026,
        results_path,
    )

    client.get_results.assert_not_called()

def test_new_results_are_processed(tmp_path: Path) -> None:
    client = Mock()

    race = Race(
        season=2026,
        round=1,
        name="Australian Grand Prix",
        date=date(2026, 3, 8),
        circuit=Circuit(
            id="albert_park",
            name="Albert Park Grand Prix Circuit",
            city="Melbourne",
            country="Australia",
            latitude=-37.8497,
            longitude=144.968,
        ),
    )

    result = Result(
        season=2026,
        round=1,
        race_name="Australian Grand Prix",
        circuit_id="albert_park",
        driver_id="russell",
        constructor_id="mercedes",
        number="63",
        position=1,
        position_text="1",
        points=25,
        grid=1,
        laps=58,
        status="Finished",
    )

    client.get_results.return_value = [result]

    results_path = tmp_path / "results"
    results_path.mkdir()

    result_path = results_path / "round=1.parquet"

    process_race_results(
        client,
        [race],
        2026,
        results_path,
    )

    client.get_results.assert_called_once_with(2026, 1)

    assert result_path.exists()

def test_future_races_are_skipped(tmp_path: Path) -> None:
    client = Mock()

    race = Race(
        season=2026,
        round=12,
        name="Dutch Grand Prix",
        date=date(2026, 8, 23),
        circuit=Circuit(
            id="zandvoort",
            name="Circuit Park Zandvoort",
            city="Zandvoort",
            country="Netherlands",
            latitude=52.3888,
            longitude=4.5409,
        ),
    )

    results_path = tmp_path / "results"
    results_path.mkdir()

    process_race_results(
        client,
        [race],
        2026,
        results_path,
    )

    client.get_results.assert_not_called()

    result_path = results_path / "round=12.parquet"
    assert not result_path.exists()