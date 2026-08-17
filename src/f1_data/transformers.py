from f1_data.models import Constructor, Driver, Race, Result


def races_to_records(races: list[Race]) -> list[dict]:
    return [
        {
            "season": race.season,
            "round": race.round,
            "race_name": race.name,
            "date": race.date,
            "circuit_id": race.circuit.id,
            "circuit_name": race.circuit.name,
            "city": race.circuit.city,
            "country": race.circuit.country,
            "latitude": race.circuit.latitude,
            "longitude": race.circuit.longitude,
        }
        for race in races
    ]

def drivers_to_records(drivers: list[Driver]) -> list[dict]:
    return [
        {
            "driver_id": driver.id,
            "permanent_number": driver.permanent_number,
            "code": driver.code,
            "first_name": driver.first_name,
            "last_name": driver.last_name,
            "date_of_birth": driver.date_of_birth,
            "nationality": driver.nationality,
        }
        for driver in drivers
    ]

def constructors_to_records(constructors: list[Constructor]) -> list[dict]:
    return [
        {
            "constructor_id": constructor.id,
            "name": constructor.name,
            "nationality": constructor.nationality,
        }
        for constructor in constructors
    ]

def results_to_records(results: list[Result]) -> list[dict]:
    return [
        {
            "season": result.season,
            "round": result.round,
            "race_name": result.race_name,
            "circuit_id": result.circuit_id,
            "driver_id": result.driver_id,
            "constructor_id": result.constructor_id,
            "number": result.number,
            "position": result.position,
            "position_text": result.position_text,
            "points": result.points,
            "grid": result.grid,
            "laps": result.laps,
            "status": result.status,
            "time_millis": result.time_millis,
            "time": result.time,
            "fastest_lap_rank": result.fastest_lap_rank,
            "fastest_lap": result.fastest_lap,
            "fastest_lap_time": result.fastest_lap_time,
        }
        for result in results
    ]