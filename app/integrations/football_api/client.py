import httpx

from app.config import settings


class FootballAPIClient:
    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self):
        self.headers = {
            "x-apisports-key": settings.football_api_key,
        }

    def get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        response = httpx.get(
            f"{self.BASE_URL}/{endpoint}",
            headers=self.headers,
            params=params,
            timeout=10.0,
        )

        response.raise_for_status()

        return response.json()