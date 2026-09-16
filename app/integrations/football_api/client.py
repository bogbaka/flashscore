import httpx

from app.config import settings


class FootballAPIError(Exception):
    """Raised when the football provider returns an error."""


class FootballAPIClient:
    def __init__(self):
        self.base_url = settings.football_api_base_url.rstrip("/")
        self.headers = {
            "x-apisports-key": settings.football_api_key,
        }
        self.timeout = settings.football_api_timeout

    def get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = httpx.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )

        except httpx.TimeoutException as error:
            raise FootballAPIError(
                "Football provider request timed out."
            ) from error

        except httpx.RequestError as error:
            raise FootballAPIError(
                "Unable to connect to football provider."
            ) from error

        if response.status_code >= 400:
            raise FootballAPIError(
                "Football provider returned "
                f"HTTP {response.status_code}."
            )

        try:
            data = response.json()
        except ValueError as error:
            raise FootballAPIError(
                "Football provider returned invalid JSON."
            ) from error

        errors = data.get("errors")

        if errors:
            raise FootballAPIError(
                f"Football provider error: {errors}"
            )

        return data