from f1_data.parsers import (
    parse_constructor_standings,
    parse_constructors,
    parse_driver_standings,
    parse_drivers,
    parse_races,
    parse_results,
    parse_sprint_results,
)


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

def test_parse_drivers():
    data = {
        "MRData": {
            "DriverTable": {
                "season": "2026",
                "Drivers": [
                    {
                        "driverId": "albon",
                        "permanentNumber": "23",
                        "code": "ALB",
                        "givenName": "Alexander",
                        "familyName": "Albon",
                        "dateOfBirth": "1996-03-23",
                        "nationality": "Thai",
                    },
                    {
                        "driverId": "paul_aron",
                        "givenName": "Paul",
                        "familyName": "Aron",
                    },
                ]
            }
        }
    }

    drivers = parse_drivers(data)

    assert len(drivers) == 2

    driver = drivers[0]

    assert driver.id == "albon"
    assert driver.permanent_number == "23"
    assert driver.code == "ALB"
    assert driver.first_name == "Alexander"
    assert driver.last_name == "Albon"
    assert driver.date_of_birth is not None
    assert driver.date_of_birth.isoformat() == "1996-03-23"
    assert driver.nationality == "Thai"

    driver_without_optional_fields = drivers[1]

    assert driver_without_optional_fields.id == "paul_aron"
    assert driver_without_optional_fields.first_name == "Paul"
    assert driver_without_optional_fields.last_name == "Aron"
    assert driver_without_optional_fields.permanent_number is None
    assert driver_without_optional_fields.code is None
    assert driver_without_optional_fields.date_of_birth is None
    assert driver_without_optional_fields.nationality is None

def test_parse_constructors():
    data = {
        "MRData": {
            "ConstructorTable": {
                "season": "2026",
                "Constructors": [
                    {
                        "constructorId": "ferrari",
                        "name": "Ferrari",
                        "nationality": "Italian",
                    },
                    {
                        "constructorId": "mclaren",
                        "name": "McLaren",
                        "nationality": "British",
                    },
                ]
            }
        }
    }

    constructors = parse_constructors(data)

    assert len(constructors) == 2

    constructor = constructors[0]

    assert constructor.id == "ferrari"
    assert constructor.name == "Ferrari"
    assert constructor.nationality == "Italian"

def test_parse_results():
    data = {
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
                                "Time": {
                                    "millis": "4986801",
                                    "time": "1:23:06.801",
                                },
                                "FastestLap": {
                                    "rank": "6",
                                    "lap": "21",
                                    "Time": {
                                        "time": "1:22.670",
                                    },
                                },
                            }
                        ],
                    }
                ]
            }
        }
    }

    results = parse_results(data)

    assert len(results) == 1

    result = results[0]

    assert result.season == 2026
    assert result.round == 1
    assert result.race_name == "Australian Grand Prix"
    assert result.circuit_id == "albert_park"

    assert result.driver_id == "russell"
    assert result.constructor_id == "mercedes"

    assert result.number == "63"
    assert result.position == 1
    assert result.position_text == "1"
    assert result.points == 25
    assert result.grid == 1
    assert result.laps == 58
    assert result.status == "Finished"

    assert result.time_millis == 4986801
    assert result.time == "1:23:06.801"

    assert result.fastest_lap_rank == 6
    assert result.fastest_lap == 21
    assert result.fastest_lap_time == "1:22.670"


def test_parse_sprint_results():
    data = {
        "MRData": {
            "RaceTable": {
                "Races": [
                    {
                        "season": "2026",
                        "round": "2",
                        "raceName": "Chinese Grand Prix",
                        "Circuit": {"circuitId": "shanghai"},
                        "SprintResults": [
                            {
                                "number": "63",
                                "position": "1",
                                "positionText": "1",
                                "points": "8",
                                "Driver": {"driverId": "russell"},
                                "Constructor": {"constructorId": "mercedes"},
                                "grid": "1",
                                "laps": "19",
                                "status": "Finished",
                            }
                        ],
                    }
                ]
            }
        }
    }

    results = parse_sprint_results(data)

    assert len(results) == 1
    assert results[0].round == 2
    assert results[0].points == 8


def test_parse_driver_standings():
    data = {
        "MRData": {
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
            }
        }
    }

    standings = parse_driver_standings(data)

    assert len(standings) == 1
    assert standings[0].season == 2026
    assert standings[0].round == 12
    assert standings[0].driver.id == "antonelli"
    assert standings[0].constructors[0].id == "mercedes"


def test_parse_constructor_standings():
    data = {
        "MRData": {
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
            }
        }
    }

    standings = parse_constructor_standings(data)

    assert len(standings) == 1
    assert standings[0].season == 2026
    assert standings[0].round == 12
    assert standings[0].constructor.id == "mercedes"
