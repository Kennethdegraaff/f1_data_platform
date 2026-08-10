from f1_data.models import Race


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