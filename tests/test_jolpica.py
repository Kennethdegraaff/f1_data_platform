import pytest
import respx
from httpx import Response

from f1_data.jolpica import JolpicaAPIError, JolpicaClient


@respx.mock
def test_get_races():
    route = respx.get(
        "https://api.jolpi.ca/ergast/f1/2026.json?limit=30&offset=0"
    ).mock(
        return_value=Response(
            200,
            json={
                "MRData": {
                    "limit": "100",
                    "offset": "0",
                    "total": "1",
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
                    },
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


@respx.mock
def test_get_drivers_handles_pagination():
    first_page = respx.get(
        "https://api.jolpi.ca/ergast/f1/2026/drivers.json?limit=30&offset=0"
    ).mock(
        return_value=Response(
            200,
            json={
                "MRData": {
                    "limit": "30",
                    "offset": "0",
                    "total": "32",
                    "DriverTable": {
                        "season": "2026",
                        "Drivers": [
                            {
                                "driverId": "russell",
                                "permanentNumber": "63",
                                "code": "RUS",
                                "givenName": "George",
                                "familyName": "Russell",
                                "dateOfBirth": "1998-02-15",
                                "nationality": "British",
                            }
                        ],
                    },
                }
            },
        )
    )

    second_page = respx.get(
        "https://api.jolpi.ca/ergast/f1/2026/drivers.json?limit=30&offset=30"
    ).mock(
        return_value=Response(
            200,
            json={
                "MRData": {
                    "limit": "30",
                    "offset": "30",
                    "total": "32",
                    "DriverTable": {
                        "season": "2026",
                        "Drivers": [
                            {
                                "driverId": "max_verstappen",
                                "permanentNumber": "3",
                                "code": "VER",
                                "givenName": "Max",
                                "familyName": "Verstappen",
                                "dateOfBirth": "1997-09-30",
                                "nationality": "Dutch",
                            }
                        ],
                    },
                }
            },
        )
    )

    client = JolpicaClient()

    drivers = client.get_drivers(2026)

    assert first_page.called
    assert second_page.called

    assert len(drivers) == 2

    driver_ids = [driver.id for driver in drivers]

    assert "russell" in driver_ids
    assert "max_verstappen" in driver_ids

    client = JolpicaClient()

def test_get_results(respx_mock):
    payload = {
        "MRData": {
            "limit": "100",
            "offset": "0",
            "total": "1",
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
                ],
            },
        }
    }

    respx_mock.get(
        "https://api.jolpi.ca/ergast/f1/2026/1/results.json?limit=30&offset=0"
    ).mock(return_value=Response(200, json=payload))

    client = JolpicaClient()

    results = client.get_results(2026, 1)

    assert len(results) == 1
    assert results[0].driver_id == "russell"
    assert results[0].constructor_id == "mercedes"
    assert results[0].position == 1
    assert results[0].points == 25


def test_get_results_retries_after_429(respx_mock):
    url = (
        "https://api.jolpi.ca/ergast/f1/2026/1/results.json"
        "?limit=30&offset=0"
    )

    responses = [
        Response(429),
        Response(
            200,
            json={
                "MRData": {
                    "limit": "100",
                    "offset": "0",
                    "total": "0",
                    "RaceTable": {
                        "season": "2026",
                        "round": "1",
                        "Races": [],
                    },
                }
            },
        ),
    ]

    route = respx_mock.get(url).mock(
        side_effect=responses
    )

    client = JolpicaClient()

    results = client.get_results(2026, 1)

    assert route.call_count == 2
    assert results == []


def test_get_results_fails_after_three_429s(respx_mock):
    url = (
        "https://api.jolpi.ca/ergast/f1/2026/1/results.json"
        "?limit=30&offset=0"
    )

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


def test_get_sprint_results_without_sprint(respx_mock):
    respx_mock.get(
        "https://api.jolpi.ca/ergast/f1/2026/1/sprint.json?limit=30&offset=0"
    ).mock(
        return_value=Response(
            200,
            json={
                "MRData": {
                    "limit": "30",
                    "offset": "0",
                    "total": "0",
                    "RaceTable": {"Races": []},
                }
            },
        )
    )

    assert JolpicaClient().get_sprint_results(2026, 1) == []


def test_get_standings_uses_season_endpoints(respx_mock):
    driver_url = (
        "https://api.jolpi.ca/ergast/f1/2026/driverstandings.json?"
        "limit=30&offset=0"
    )
    constructor_url = (
        "https://api.jolpi.ca/ergast/f1/2026/constructorstandings.json?"
        "limit=30&offset=0"
    )
    driver_payload = {
        "MRData": {
            "limit": "30",
            "offset": "0",
            "total": "1",
            "StandingsTable": {
                "StandingsLists": [
                    {
                        "season": "2026",
                        "round": "12",
                        "DriverStandings": [
                            {
                                "position": "1",
                                "positionText": "1",
                                "points": "242",
                                "wins": "6",
                                "Driver": {
                                    "driverId": "antonelli",
                                    "givenName": "Andrea Kimi",
                                    "familyName": "Antonelli",
                                },
                                "Constructors": [
                                    {
                                        "constructorId": "mercedes",
                                        "name": "Mercedes",
                                        "nationality": "German",
                                    }
                                ],
                            }
                        ],
                    }
                ]
            },
        }
    }
    constructor_payload = {
        "MRData": {
            "limit": "30",
            "offset": "0",
            "total": "1",
            "StandingsTable": {
                "StandingsLists": [
                    {
                        "season": "2026",
                        "round": "12",
                        "ConstructorStandings": [
                            {
                                "position": "1",
                                "positionText": "1",
                                "points": "425",
                                "wins": "8",
                                "Constructor": {
                                    "constructorId": "mercedes",
                                    "name": "Mercedes",
                                    "nationality": "German",
                                },
                            }
                        ],
                    }
                ]
            },
        }
    }
    respx_mock.get(driver_url).mock(return_value=Response(200, json=driver_payload))
    respx_mock.get(constructor_url).mock(
        return_value=Response(200, json=constructor_payload)
    )

    client = JolpicaClient()

    assert client.get_driver_standings(2026)[0].round == 12
    assert client.get_constructor_standings(2026)[0].round == 12
