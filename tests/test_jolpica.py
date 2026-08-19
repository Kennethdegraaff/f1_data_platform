import pytest
import respx
from httpx import Response

from f1_data.jolpica import JolpicaAPIError, JolpicaClient


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

def test_get_results(respx_mock):
    payload = {
        "MRData": {
            "RaceTable": {
                "season": "2026",
                "round": "1",
                "Races": [
                    {
                        "season": "2026",
                        "round": "1",
                        "raceName": "Australian Grand Prix",
                        "Circuit": {
                            "circuitId": "albert_park",
                        },
                        "Results": [
                            {
                                "number": "63",
                                "position": "1",
                                "positionText": "1",
                                "points": "25",
                                "Driver": {
                                    "driverId": "russell",
                                },
                                "Constructor": {
                                    "constructorId": "mercedes",
                                },
                                "grid": "1",
                                "laps": "58",
                                "status": "Finished",
                            }
                        ],
                    }
                ]
            }
        }
    }

    respx_mock.get(
        "https://api.jolpi.ca/ergast/f1/2026/1/results.json"
    ).mock(return_value=Response(200, json=payload))

    client = JolpicaClient()

    results = client.get_results(2026, 1)

    assert len(results) == 1
    assert results[0].driver_id == "russell"
    assert results[0].constructor_id == "mercedes"
    assert results[0].position == 1
    assert results[0].points == 25

def test_get_results_retries_after_429(respx_mock):
    url = "https://api.jolpi.ca/ergast/f1/2026/1/results.json"

    responses = [
        Response(429),
        Response(200, json={
            "MRData": {
                "RaceTable": {
                    "season": "2026",
                    "round": "1",
                    "Races": [],
                }
            }
        }),
    ]

    route = respx_mock.get(url).mock(
        side_effect=responses
    )

    client = JolpicaClient()

    results = client.get_results(2026, 1)

    assert route.call_count == 2
    assert results == []

def test_get_results_fails_after_three_429s(respx_mock):
    url = "https://api.jolpi.ca/ergast/f1/2026/1/results.json"

    respx_mock.get(url).mock(
        side_effect=[
            Response(429),
            Response(429),
            Response(429),
        ]
    )

    client = JolpicaClient()

    with pytest.raises(JolpicaAPIError, match="Too many requests"):
        client.get_results(2026, 1)