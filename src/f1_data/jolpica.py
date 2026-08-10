import httpx

from f1_data.models import Race
from f1_data.parsers import parse_races


class JolpicaClient:
    BASE_URL = "https://api.jolpi.ca/ergast/f1"

    def __init__(self) -> None:
        self.client = httpx.Client()

    def get_races(self, season: int) -> list[Race]:
        response = self.client.get(f"{self.BASE_URL}/{season}.json")
        response.raise_for_status()

        return parse_races(response.json())