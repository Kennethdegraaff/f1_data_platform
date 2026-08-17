import time

import httpx

from f1_data.models import Constructor, Driver, Race, Result
from f1_data.parsers import (
    parse_constructors,
    parse_drivers,
    parse_races,
    parse_results,
)


class JolpicaAPIError(Exception):
    """Raised when the Jolpica API request fails."""


class JolpicaClient:
    BASE_URL = "https://api.jolpi.ca/ergast/f1"

    def __init__(self) -> None:
        self.client = httpx.Client()

    def _get(self, url: str) -> dict:
        for attempt in range(3):
            response = self.client.get(url)

            if response.status_code == 429:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue

                raise JolpicaAPIError(
                    f"Too many requests for {url} after 3 attempts"
                )

            if response.status_code >= 500 and attempt < 2:
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            return response.json()

        raise JolpicaAPIError(f"Request failed for {url}")

    def get_races(self, season: int) -> list[Race]:
        url = f"{self.BASE_URL}/{season}.json"
        data = self._get(url)

        return parse_races(data)

    def get_drivers(self, season: int) -> list[Driver]:
        url = f"{self.BASE_URL}/{season}/drivers.json"
        data = self._get(url)

        return parse_drivers(data)

    def get_constructors(self, season: int) -> list[Constructor]:
        url = f"{self.BASE_URL}/{season}/constructors.json"
        data = self._get(url)

        return parse_constructors(data)

    def get_results(self, season: int, round: int) -> list[Result]:
        url = f"{self.BASE_URL}/{season}/{round}/results.json"
        data = self._get(url)

        return parse_results(data)