from f1_data.models import (
    Circuit,
    Constructor,
    Driver,
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
    races = data["MRData"]["RaceTable"]["Races"]

    results = []

    for race in races:
        for result in race["Results"]:
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