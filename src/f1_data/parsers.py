from f1_data.models import Circuit, Race


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