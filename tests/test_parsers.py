from f1_data.parsers import parse_races


def test_parse_races():
    data = {
        "MRData": {
            "RaceTable": {
                "Races": [
                    {
                        "season": "2026",
                        "round": "1",
                        "raceName": "Australian Grand Prix",
                        "Circuit": {
                            "circuitId": "albert_park",
                            "circuitName": "Albert Park Grand Prix Circuit",
                            "Location": {
                                "locality": "Melbourne",
                                "country": "Australia",
                                "lat": "-37.8497",
                                "long": "144.968",
                            },
                        },
                        "date": "2026-03-08",
                    }
                ]
            }
        }
    }

    races = parse_races(data)

    assert len(races) == 1

    race = races[0]

    assert race.season == 2026
    assert race.round == 1
    assert race.name == "Australian Grand Prix"

    assert race.circuit.id == "albert_park"
    assert race.circuit.city == "Melbourne"
    assert race.circuit.country == "Australia"
    assert race.circuit.latitude == -37.8497
    assert race.circuit.longitude == 144.968