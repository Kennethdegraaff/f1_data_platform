from datetime import date

from f1_data.models import Circuit, Race
from f1_data.transformers import races_to_records


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