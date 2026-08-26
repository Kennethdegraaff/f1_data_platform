import time

import httpx

from f1_data.models import (
    Constructor,
    ConstructorStanding,
    Driver,
    DriverStanding,
    Race,
    Result,
)
from f1_data.parsers import (
    parse_constructor_standings,
    parse_constructors,
    parse_driver_standings,
    parse_drivers,
    parse_races,
    parse_results,
    parse_sprint_results,
)


class JolpicaAPIError(Exception):
    """Raised when the Jolpica API request fails."""


class JolpicaClient:
    BASE_URL = "https://api.jolpi.ca/ergast/f1"
    PAGE_SIZE = 30

    def __init__(self) -> None:
        self.client = httpx.Client()

    def _get(self, url: str) -> dict:
        offset = 0
        all_data: dict | None = None

        while True:
            separator = "&" if "?" in url else "?"

            page_url = (
                f"{url}"
                f"{separator}limit={self.PAGE_SIZE}"
                f"&offset={offset}"
            )

            data = self._get_page(page_url)

            if all_data is None:
                all_data = data
            else:
                self._merge_page(all_data, data)

            mrdata = data["MRData"]

            total = int(mrdata["total"])
            limit = int(mrdata["limit"])
            current_offset = int(mrdata["offset"])

            next_offset = current_offset + limit

            if next_offset >= total:
                break

            offset = next_offset

        return all_data

    def _get_page(self, url: str) -> dict:
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

    @staticmethod
    def _merge_page(target: dict, page: dict) -> None:
        target_mrdata = target["MRData"]
        page_mrdata = page["MRData"]

        for key, value in page_mrdata.items():
            if key in ("limit", "offset", "total"):
                continue

            if not isinstance(value, dict):
                continue

            target_section = target_mrdata.setdefault(key, {})

            for nested_key, nested_value in value.items():
                if not isinstance(nested_value, list):
                    continue

                target_section.setdefault(nested_key, [])
                target_section[nested_key].extend(nested_value)

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

    def get_sprint_results(self, season: int, round: int) -> list[Result]:
        url = f"{self.BASE_URL}/{season}/{round}/sprint.json"
        data = self._get(url)

        return parse_sprint_results(data)

    def get_driver_standings(
        self, season: int, round_number: int
    ) -> list[DriverStanding]:
        url = f"{self.BASE_URL}/{season}/{round_number}/driverstandings.json"
        data = self._get(url)

        return parse_driver_standings(data)

    def get_constructor_standings(
        self,
        season: int,
        round_number: int,
    ) -> list[ConstructorStanding]:
        url = (
            f"{self.BASE_URL}/{season}/{round_number}/"
            "constructorstandings.json"
        )
        data = self._get(url)

        return parse_constructor_standings(data)
