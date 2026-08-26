from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import Mock, patch

from f1_data.jolpica import JolpicaAPIError
from f1_data.models import (
    Circuit,
    Constructor,
    ConstructorStanding,
    Driver,
    DriverStanding,
    Race,
    Result,
)
from f1_data.pipeline import (
    process_constructor_standings,
    process_driver_standings,
    process_race_results,
    process_sprint_results,
)


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

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=True),
        patch("f1_data.pipeline.add_results_partition") as mock_partition,
    ):
        process_race_results(
            client,
            [race],
            2026,
            Path("data_collected/2026/results"),
            bucket="f1-data-platform",
        )

    client.get_results.assert_not_called()
    mock_partition.assert_called_once_with(
        season=2026,
        round_number=1,
        bucket="f1-data-platform",
    )


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


def test_sprint_without_results_is_skipped() -> None:
    client = Mock()
    client.get_sprint_results.return_value = []
    race = Race(
        season=2026,
        round=2,
        name="Chinese Grand Prix",
        date=date(2026, 3, 15),
        circuit=Circuit(
            id="shanghai",
            name="Shanghai International Circuit",
            city="Shanghai",
            country="China",
            latitude=31.3389,
            longitude=121.22,
        ),
    )

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=False),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch("f1_data.pipeline.add_sprint_partition") as mock_partition,
    ):
        process_sprint_results(
            client,
            [race],
            2026,
            Path("data_collected/2026/sprint"),
            bucket="f1-data-platform",
        )

    client.get_sprint_results.assert_called_once_with(2026, 2)
    mock_write.assert_not_called()
    mock_partition.assert_not_called()


def test_new_sprint_results_are_processed() -> None:
    client = Mock()
    client.get_sprint_results.return_value = [
        Result(
            season=2026,
            round=2,
            race_name="Chinese Grand Prix",
            circuit_id="shanghai",
            driver_id="russell",
            constructor_id="mercedes",
            number="63",
            position=1,
            position_text="1",
            points=8,
            grid=1,
            laps=19,
            status="Finished",
        )
    ]
    race = Race(
        season=2026,
        round=2,
        name="Chinese Grand Prix",
        date=date(2026, 3, 15),
        circuit=Circuit(
            id="shanghai",
            name="Shanghai International Circuit",
            city="Shanghai",
            country="China",
            latitude=31.3389,
            longitude=121.22,
        ),
    )

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=False),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch("f1_data.pipeline.add_sprint_partition") as mock_partition,
    ):
        process_sprint_results(
            client,
            [race],
            2026,
            Path("data_collected/2026/sprint"),
            bucket="f1-data-platform",
        )

    mock_write.assert_called_once()
    assert mock_write.call_args.args[1] == Path(
        "data_collected/2026/sprint/round=2/sprint.parquet"
    )
    mock_partition.assert_called_once_with(
        season=2026,
        round_number=2,
        bucket="f1-data-platform",
    )


def test_existing_sprint_results_are_skipped() -> None:
    client = Mock()
    race = Race(
        season=2026,
        round=2,
        name="Chinese Grand Prix",
        date=date(2026, 3, 15),
        circuit=Circuit(
            id="shanghai",
            name="Shanghai International Circuit",
            city="Shanghai",
            country="China",
            latitude=31.3389,
            longitude=121.22,
        ),
    )

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=True),
        patch("f1_data.pipeline.add_sprint_partition") as mock_partition,
    ):
        process_sprint_results(
            client,
            [race],
            2026,
            Path("data_collected/2026/sprint"),
            bucket="f1-data-platform",
        )

    client.get_sprint_results.assert_not_called()
    mock_partition.assert_called_once_with(
        season=2026,
        round_number=2,
        bucket="f1-data-platform",
    )


def test_driver_standings_are_stored_as_new_round_snapshot() -> None:
    client = Mock()
    client.get_driver_standings.return_value = [
        DriverStanding(
            season=2026,
            round=12,
            position=1,
            position_text="1",
            points=242,
            wins=6,
            driver=Driver(
                id="antonelli",
                first_name="Andrea Kimi",
                last_name="Antonelli",
            ),
            constructors=[
                Constructor(id="mercedes", name="Mercedes", nationality="German")
            ],
        )
    ]

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=False),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_driver_standings_partition"
        ) as mock_partition,
    ):
        process_driver_standings(
            client,
            2026,
            Path("data_collected/driver_standings"),
            bucket="f1-data-platform",
        )

    assert mock_write.call_args.args[1] == Path(
        "data_collected/driver_standings/season=2026/round=12/"
        "driver_standings.parquet"
    )
    mock_partition.assert_called_once_with(2026, 12, "f1-data-platform")


def test_existing_constructor_standings_snapshot_registers_partition() -> None:
    client = Mock()
    client.get_constructor_standings.return_value = [
        ConstructorStanding(
            season=2026,
            round=12,
            position=1,
            position_text="1",
            points=425,
            wins=8,
            constructor=Constructor(
                id="mercedes",
                name="Mercedes",
                nationality="German",
            ),
        )
    ]

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=True),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_constructor_standings_partition"
        ) as mock_partition,
    ):
        process_constructor_standings(
            client,
            2026,
            Path("data_collected/constructor_standings"),
            bucket="f1-data-platform",
        )

    mock_write.assert_not_called()
    mock_partition.assert_called_once_with(2026, 12, "f1-data-platform")


def test_existing_driver_standings_snapshot_registers_partition() -> None:
    client = Mock()
    client.get_driver_standings.return_value = [
        DriverStanding(
            season=2026,
            round=12,
            position=1,
            position_text="1",
            points=242,
            wins=6,
            driver=Driver(
                id="antonelli",
                first_name="Andrea Kimi",
                last_name="Antonelli",
            ),
            constructors=[
                Constructor(id="mercedes", name="Mercedes", nationality="German")
            ],
        )
    ]

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=True),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_driver_standings_partition"
        ) as mock_partition,
    ):
        process_driver_standings(
            client,
            2026,
            Path("data_collected/driver_standings"),
            bucket="f1-data-platform",
        )

    mock_write.assert_not_called()
    mock_partition.assert_called_once_with(2026, 12, "f1-data-platform")


def test_driver_standings_jolpica_error_is_logged(capsys) -> None:
    client = Mock()
    client.get_driver_standings.side_effect = JolpicaAPIError("temporary error")

    process_driver_standings(
        client,
        2026,
        Path("data_collected/driver_standings"),
        bucket="f1-data-platform",
    )

    assert "✗ Failed driver standings: temporary error" in capsys.readouterr().out


def test_constructor_standings_jolpica_error_is_logged(capsys) -> None:
    client = Mock()
    client.get_constructor_standings.side_effect = JolpicaAPIError("temporary error")

    process_constructor_standings(
        client,
        2026,
        Path("data_collected/constructor_standings"),
        bucket="f1-data-platform",
    )

    assert (
        "✗ Failed constructor standings: temporary error"
        in capsys.readouterr().out
    )


def test_constructor_standings_are_stored_as_new_round_snapshot() -> None:
    client = Mock()
    client.get_constructor_standings.return_value = [
        ConstructorStanding(
            season=2026,
            round=12,
            position=1,
            position_text="1",
            points=425,
            wins=8,
            constructor=Constructor(
                id="mercedes",
                name="Mercedes",
                nationality="German",
            ),
        )
    ]

    with (
        patch("f1_data.pipeline.parquet_exists", return_value=False),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_constructor_standings_partition"
        ) as mock_partition,
    ):
        process_constructor_standings(
            client,
            2026,
            Path("data_collected/constructor_standings"),
            bucket="f1-data-platform",
        )

    assert mock_write.call_args.args[1] == Path(
        "data_collected/constructor_standings/season=2026/round=12/"
        "constructor_standings.parquet"
    )
    mock_partition.assert_called_once_with(2026, 12, "f1-data-platform")
