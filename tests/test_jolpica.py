import respx
from httpx import Response

from f1_data.jolpica import JolpicaClient


@respx.mock
def test_get_races():
    route = respx.get(
        "https://api.jolpi.ca/ergast/f1/2026.json"
    ).mock(
        return_value=Response(
            200,
            json={
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
            },
        )
    )

    client = JolpicaClient()

    races = client.get_races(2026)

    assert route.called
    assert len(races) == 1
    assert races[0].name == "Australian Grand Prix"
    assert races[0].season == 2026