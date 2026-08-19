from datetime import date

from f1_data.models import Circuit, Race, Result
from f1_data.transformers import races_to_records, results_to_records


def test_races_to_records():
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

    records = races_to_records([race])

    assert len(records) == 1

    record = records[0]

    assert record["season"] == 2026
    assert record["round"] == 1
    assert record["race_name"] == "Australian Grand Prix"
    assert record["country"] == "Australia"

def test_results_to_records():
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
        points=25.0,
        grid=1,
        laps=58,
        status="Finished",
        time_millis=4986801,
        time="1:23:06.801",
        fastest_lap_rank=6,
        fastest_lap=21,
        fastest_lap_time="1:22.670",
    )

    records = results_to_records([result])

    assert len(records) == 1

    record = records[0]

    assert record["season"] == 2026
    assert record["round"] == 1
    assert record["race_name"] == "Australian Grand Prix"
    assert record["driver_id"] == "russell"
    assert record["constructor_id"] == "mercedes"
    assert record["position"] == 1
    assert record["points"] == 25.0
    assert record["status"] == "Finished"
    assert record["fastest_lap"] == 21