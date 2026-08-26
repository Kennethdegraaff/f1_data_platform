from datetime import date
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
    process_reference_data,
    process_sprint_results,
    resolve_season,
)


BUCKET = "f1-data-platform"
DATABASE_NAME = "f1_data"


def make_race(
    round_number: int = 1,
    race_date: date = date(2026, 3, 8),
    name: str = "Australian Grand Prix",
) -> Race:
    return Race(
        season=2026,
        round=round_number,
        name=name,
        date=race_date,
        circuit=Circuit(
            id="albert_park",
            name="Albert Park Grand Prix Circuit",
            city="Melbourne",
            country="Australia",
            latitude=-37.8497,
            longitude=144.968,
        ),
    )


def test_resolve_season_with_explicit_season() -> None:
    assert resolve_season(2026) == 2026


def test_resolve_season_without_season() -> None:
    with patch("f1_data.pipeline.datetime") as mock_datetime:
        mock_datetime.now.return_value.year = 2026

        assert resolve_season(None) == 2026


def test_process_reference_data() -> None:
    client = Mock()

    races = [make_race()]
    drivers = [
        Driver(
            id="russell",
            first_name="George",
            last_name="Russell",
        )
    ]
    constructors = [
        Constructor(
            id="mercedes",
            name="Mercedes",
            nationality="German",
        )
    ]

    client.get_races.return_value = races
    client.get_drivers.return_value = drivers
    client.get_constructors.return_value = constructors

    with (
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_reference_partition"
        ) as mock_partition,
    ):
        result = process_reference_data(
            client,
            2026,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    assert result == races

    assert mock_write.call_count == 3
    assert mock_partition.call_count == 3

    client.get_races.assert_called_once_with(2026)
    client.get_drivers.assert_called_once_with(2026)
    client.get_constructors.assert_called_once_with(2026)


def test_process_reference_data_writes_expected_paths() -> None:
    client = Mock()

    client.get_races.return_value = [make_race()]
    client.get_drivers.return_value = []
    client.get_constructors.return_value = []

    with (
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch("f1_data.pipeline.add_reference_partition"),
    ):
        process_reference_data(
            client,
            2026,
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    paths = [
        call.args[1]
        for call in mock_write.call_args_list
    ]

    assert Path(
        "data_collected/races/season=2026/races.parquet"
    ) in paths

    assert Path(
        "data_collected/drivers/season=2026/drivers.parquet"
    ) in paths

    assert Path(
        "data_collected/constructors/"
        "season=2026/constructors.parquet"
    ) in paths


def test_new_results_are_processed() -> None:
    client = Mock()

    race = make_race()

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
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=False,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_results_partition"
        ) as mock_partition,
    ):
        process_race_results(
            client,
            [race],
            2026,
            Path("data_collected/race_results/season=2026"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_results.assert_called_once_with(2026, 1)

    mock_write.assert_called_once()

    assert mock_write.call_args.args[1] == Path(
        "data_collected/race_results/"
        "season=2026/round=1/race_results.parquet"
    )

    mock_partition.assert_called_once_with(
        season=2026,
        round_number=1,
        bucket=BUCKET,
        database_name=DATABASE_NAME,
    )


def test_existing_results_are_not_downloaded_again() -> None:
    client = Mock()

    race = make_race()

    with (
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=True,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_results_partition"
        ) as mock_partition,
    ):
        process_race_results(
            client,
            [race],
            2026,
            Path("data_collected/race_results/season=2026"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_results.assert_not_called()
    mock_write.assert_not_called()

    mock_partition.assert_called_once_with(
        season=2026,
        round_number=1,
        bucket=BUCKET,
        database_name=DATABASE_NAME,
    )


def test_future_race_results_are_skipped() -> None:
    client = Mock()

    future_race = make_race(
        race_date=date(2099, 1, 1)
    )

    with (
        patch("f1_data.pipeline.parquet_exists") as mock_exists,
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_results_partition"
        ) as mock_partition,
    ):
        process_race_results(
            client,
            [future_race],
            2026,
            Path("data_collected/race_results/season=2026"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_results.assert_not_called()
    mock_exists.assert_not_called()
    mock_write.assert_not_called()
    mock_partition.assert_not_called()


def test_jolpica_error_is_logged_for_results(capsys) -> None:
    client = Mock()

    race = make_race()

    client.get_results.side_effect = JolpicaAPIError(
        "temporary error"
    )

    with (
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=False,
        ),
        patch("f1_data.pipeline.add_results_partition"),
    ):
        process_race_results(
            client,
            [race],
            2026,
            Path("data_collected/race_results/season=2026"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    captured = capsys.readouterr()

    assert "Failed round 1" in captured.out
    assert "temporary error" in captured.out


def test_new_sprint_results_are_processed() -> None:
    client = Mock()

    race = make_race(
        round_number=2,
        name="Chinese Grand Prix",
        race_date=date(2026, 3, 15),
    )

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

    with (
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=False,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_sprint_partition"
        ) as mock_partition,
    ):
        process_sprint_results(
            client,
            [race],
            2026,
            Path("data_collected/sprint_results/season=2026"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_sprint_results.assert_called_once_with(
        2026,
        2,
    )

    mock_write.assert_called_once()

    assert mock_write.call_args.args[1] == Path(
        "data_collected/sprint_results/"
        "season=2026/round=2/sprint_results.parquet"
    )

    mock_partition.assert_called_once_with(
        season=2026,
        round_number=2,
        bucket=BUCKET,
        database_name=DATABASE_NAME,
    )


def test_existing_sprint_results_are_not_downloaded_again() -> None:
    client = Mock()

    race = make_race(round_number=2)

    with (
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=True,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_sprint_partition"
        ) as mock_partition,
    ):
        process_sprint_results(
            client,
            [race],
            2026,
            Path("data_collected/sprint_results/season=2026"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_sprint_results.assert_not_called()
    mock_write.assert_not_called()

    mock_partition.assert_called_once_with(
        season=2026,
        round_number=2,
        bucket=BUCKET,
        database_name=DATABASE_NAME,
    )


def test_no_sprint_results_are_skipped() -> None:
    client = Mock()

    race = make_race(round_number=2)

    client.get_sprint_results.return_value = []

    with (
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=False,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_sprint_partition"
        ) as mock_partition,
    ):
        process_sprint_results(
            client,
            [race],
            2026,
            Path("data_collected/sprint_results/season=2026"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    mock_write.assert_not_called()
    mock_partition.assert_not_called()


def test_new_driver_standings_are_stored_as_new_round_snapshot() -> None:
    client = Mock()

    race = make_race(round_number=12)

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
                Constructor(
                    id="mercedes",
                    name="Mercedes",
                    nationality="German",
                )
            ],
        )
    ]

    with (
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=False,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_driver_standings_partition"
        ) as mock_partition,
    ):
        process_driver_standings(
            client,
            [race],
            2026,
            Path("data_collected/driver_standings"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_driver_standings.assert_called_once_with(
        2026,
        12,
    )

    mock_write.assert_called_once()

    assert mock_write.call_args.args[1] == Path(
        "data_collected/driver_standings/"
        "season=2026/round=12/"
        "driver_standings.parquet"
    )

    mock_partition.assert_called_once_with(
        2026,
        12,
        BUCKET,
        DATABASE_NAME,
    )


def test_existing_driver_standings_snapshot_registers_partition() -> None:
    client = Mock()

    race = make_race(round_number=12)

    with (
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=True,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_driver_standings_partition"
        ) as mock_partition,
    ):
        process_driver_standings(
            client,
            [race],
            2026,
            Path("data_collected/driver_standings"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_driver_standings.assert_not_called()
    mock_write.assert_not_called()

    mock_partition.assert_called_once_with(
        2026,
        12,
        BUCKET,
        DATABASE_NAME,
    )


def test_driver_standings_jolpica_error_is_logged(capsys) -> None:
    client = Mock()

    race = make_race(round_number=12)

    client.get_driver_standings.side_effect = JolpicaAPIError(
        "temporary error"
    )

    with patch(
        "f1_data.pipeline.parquet_exists",
        return_value=False,
    ):
        process_driver_standings(
            client,
            [race],
            2026,
            Path("data_collected/driver_standings"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    captured = capsys.readouterr()

    assert "Failed driver standings" in captured.out
    assert "temporary error" in captured.out


def test_new_constructor_standings_are_stored_as_new_round_snapshot() -> None:
    client = Mock()

    race = make_race(round_number=12)

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
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=False,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_constructor_standings_partition"
        ) as mock_partition,
    ):
        process_constructor_standings(
            client,
            [race],
            2026,
            Path("data_collected/constructor_standings"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_constructor_standings.assert_called_once_with(
        2026,
        12,
    )

    mock_write.assert_called_once()

    assert mock_write.call_args.args[1] == Path(
        "data_collected/constructor_standings/"
        "season=2026/round=12/"
        "constructor_standings.parquet"
    )

    mock_partition.assert_called_once_with(
        2026,
        12,
        BUCKET,
        DATABASE_NAME,
    )


def test_existing_constructor_standings_snapshot_registers_partition() -> None:
    client = Mock()

    race = make_race(round_number=12)

    with (
        patch(
            "f1_data.pipeline.parquet_exists",
            return_value=True,
        ),
        patch("f1_data.pipeline.write_parquet") as mock_write,
        patch(
            "f1_data.pipeline.add_constructor_standings_partition"
        ) as mock_partition,
    ):
        process_constructor_standings(
            client,
            [race],
            2026,
            Path("data_collected/constructor_standings"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    client.get_constructor_standings.assert_not_called()
    mock_write.assert_not_called()

    mock_partition.assert_called_once_with(
        2026,
        12,
        BUCKET,
        DATABASE_NAME,
    )


def test_constructor_standings_jolpica_error_is_logged(capsys) -> None:
    client = Mock()

    race = make_race(round_number=12)

    client.get_constructor_standings.side_effect = JolpicaAPIError(
        "temporary error"
    )

    with patch(
        "f1_data.pipeline.parquet_exists",
        return_value=False,
    ):
        process_constructor_standings(
            client,
            [race],
            2026,
            Path("data_collected/constructor_standings"),
            bucket=BUCKET,
            database_name=DATABASE_NAME,
        )

    captured = capsys.readouterr()

    assert "Failed constructor standings" in captured.out
    assert "temporary error" in captured.out