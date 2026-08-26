from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import Mock, patch

from f1_data.models import Circuit, Race, Result
from f1_data.pipeline import process_race_results


def test_existing_results_are_skipped() -> None:
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

    with patch("f1_data.pipeline.parquet_exists", return_value=True):
        process_race_results(
            client,
            [race],
            2026,
            Path("data_collected/2026/results"),
            bucket="f1-data-platform",
        )

    client.get_results.assert_not_called()


def test_new_results_are_processed() -> None:
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

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=False),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch("f1_data.pipeline.add_results_partition") as mock_partition,
    ):
        process_race_results(
            client,
            [race],
            2026,
            Path("data_collected/2026/results"),
            bucket="f1-data-platform",
        )

    client.get_results.assert_called_once_with(2026, 1)

    mock_write.assert_called_once()

    call_args = mock_write.call_args

    assert call_args.args[1] == Path(
        "data_collected/2026/results/round=1/results.parquet"
    )
    assert call_args.kwargs["bucket"] == "f1-data-platform"

    mock_partition.assert_called_once_with(
        season=2026,
        round_number=1,
        bucket="f1-data-platform",
    )


def test_future_races_are_skipped() -> None:
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

    with patch(
        "f1_data.pipeline.datetime",
    ) as mock_datetime:
        mock_datetime.now.return_value = datetime(
            2026,
            8,
            22,
            tzinfo=UTC,
        )

        process_race_results(
            client,
            [race],
            2026,
            Path("data_collected/2026/results"),
            bucket="f1-data-platform",
        )

    client.get_results.assert_not_called()