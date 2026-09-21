import httpx

from app.config import settings
from app.services.api_budget import APIBudgetService


class FootballAPIError(Exception):
    """Raised when the football provider returns an error."""


class FootballAPIClient:
    def __init__(
        self,
        budget: APIBudgetService | None = None,
    ):
        self.base_url = settings.football_api_base_url.rstrip("/")
        self.headers = {
            "x-apisports-key": settings.football_api_key,
        }
        self.timeout = settings.football_api_timeout
        self.budget = budget or APIBudgetService(
            daily_limit=settings.football_api_daily_limit,
            reserved_requests=settings.football_api_reserved_requests,
        )

        self.client = httpx.Client(
            headers=self.headers,
            timeout=self.timeout,
        )

    def get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        if not self.budget.can_make_request():
            raise FootballAPIError(
                "Daily football API budget has been reached."
            )

        self.budget.record_request()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.client.get(
                url,
                params=params,
            )

            response.raise_for_status()

        except httpx.TimeoutException as error:
            raise FootballAPIError(
                "Football provider request timed out."
            ) from error

        except httpx.HTTPStatusError as error:
            raise FootballAPIError(
                "Football provider returned "
                f"HTTP {error.response.status_code}."
            ) from error

        except httpx.RequestError as error:
            raise FootballAPIError(
                "Unable to connect to football provider."
            ) from error

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

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()