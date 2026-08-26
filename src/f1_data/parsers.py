from f1_data.models import (
    Circuit,
    Constructor,
    ConstructorStanding,
    Driver,
    DriverStanding,
    Race,
    Result,
)


def parse_races(data: dict) -> list[Race]:
    races = data["MRData"]["RaceTable"]["Races"]

    return [
        Race(
            season=race["season"],
            round=race["round"],
            name=race["raceName"],
            date=race["date"],
            circuit=Circuit(
                id=race["Circuit"]["circuitId"],
                name=race["Circuit"]["circuitName"],
                city=race["Circuit"]["Location"]["locality"],
                country=race["Circuit"]["Location"]["country"],
                latitude=race["Circuit"]["Location"]["lat"],
                longitude=race["Circuit"]["Location"]["long"],
            ),
        )
        for race in races
    ]

def parse_drivers(data: dict) -> list[Driver]:
    drivers = data["MRData"]["DriverTable"]["Drivers"]

    return [
        Driver(
            id=driver["driverId"],
            permanent_number=driver.get("permanentNumber"),
            code=driver.get("code"),
            first_name=driver["givenName"],
            last_name=driver["familyName"],
            date_of_birth=driver.get("dateOfBirth"),
            nationality=driver.get("nationality"),
        )
        for driver in drivers
    ]

def parse_constructors(data: dict) -> list[Constructor]:
    constructors = data["MRData"]["ConstructorTable"]["Constructors"]

    return [
        Constructor(
            id=constructor["constructorId"],
            name=constructor["name"],
            nationality=constructor["nationality"],
        )
        for constructor in constructors
    ]

def parse_results(data: dict) -> list[Result]:
    return _parse_race_results(data, "Results")


def parse_sprint_results(data: dict) -> list[Result]:
    return _parse_race_results(data, "SprintResults")


def _parse_race_results(data: dict, result_key: str) -> list[Result]:
    races = data["MRData"]["RaceTable"]["Races"]

    results = []

    for race in races:
        for result in race[result_key]:
            time_data = result.get("Time")
            fastest_lap = result.get("FastestLap")

            results.append(
                Result(
                    season=int(race["season"]),
                    round=int(race["round"]),
                    race_name=race["raceName"],
                    circuit_id=race["Circuit"]["circuitId"],
                    driver_id=result["Driver"]["driverId"],
                    constructor_id=result["Constructor"]["constructorId"],
                    number=result["number"],
                    position=int(result["position"]),
                    position_text=result["positionText"],
                    points=float(result["points"]),
                    grid=int(result["grid"]),
                    laps=int(result["laps"]),
                    status=result["status"],
                    time_millis=(
                        int(time_data["millis"])
                        if time_data
                        else None
                    ),
                    time=(
                        time_data["time"]
                        if time_data
                        else None
                    ),
                    fastest_lap_rank=(
                        int(fastest_lap["rank"])
                        if fastest_lap
                        else None
                    ),
                    fastest_lap=(
                        int(fastest_lap["lap"])
                        if fastest_lap
                        else None
                    ),
                    fastest_lap_time=(
                        fastest_lap["Time"]["time"]
                        if fastest_lap
                        else None
                    ),
                )
            )

    return results


def parse_driver_standings(data: dict) -> list[DriverStanding]:
    standings_table = data["MRData"]["StandingsTable"]
    standings_lists = standings_table["StandingsLists"]

    if not standings_lists:
        return []

    standings_list = standings_lists[0]
    season = int(standings_list["season"])
    round_number = int(standings_list["round"])

    return [
        DriverStanding(
            season=season,
            round=round_number,
            position=(
                int(standing["position"])
                if standing.get("position") is not None
                else None
            ),
            position_text=standing["positionText"],
            points=float(standing["points"]),
            wins=int(standing["wins"]),
            driver=Driver(
                id=standing["Driver"]["driverId"],
                permanent_number=standing["Driver"].get("permanentNumber"),
                code=standing["Driver"].get("code"),
                first_name=standing["Driver"]["givenName"],
                last_name=standing["Driver"]["familyName"],
                date_of_birth=standing["Driver"].get("dateOfBirth"),
                nationality=standing["Driver"].get("nationality"),
            ),
            constructors=[
                Constructor(
                    id=constructor["constructorId"],
                    name=constructor["name"],
                    nationality=constructor["nationality"],
                )
                for constructor in standing["Constructors"]
            ],
        )
        for standing in standings_list["DriverStandings"]
    ]


def parse_constructor_standings(data: dict) -> list[ConstructorStanding]:
    standings_table = data["MRData"]["StandingsTable"]
    standings_lists = standings_table["StandingsLists"]

    if not standings_lists:
        return []

    standings_list = standings_lists[0]
    season = int(standings_list["season"])
    round_number = int(standings_list["round"])

    return [
        ConstructorStanding(
            season=season,
            round=round_number,
            position=(
                int(standing["position"])
                if standing.get("position") is not None
                else None
            ),
            position_text=standing["positionText"],
            points=float(standing["points"]),
            wins=int(standing["wins"]),
            constructor=Constructor(
                id=standing["Constructor"]["constructorId"],
                name=standing["Constructor"]["name"],
                nationality=standing["Constructor"]["nationality"],
            ),
        )
        for standing in standings_list["ConstructorStandings"]
    ]
