import httpx
import pytest

from app.integrations.football_api.client import (
    FootballAPIClient,
    FootballAPIError,
)
from app.services.api_budget import APIBudgetService


def make_client(
    handler,
    budget=None,
):
    client = FootballAPIClient(
        budget=budget
    )

    client.client.close()

    client.client = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers=client.headers,
        timeout=client.timeout,
    )

    return client


def test_get_returns_successful_response():
    def handler(request):
        assert request.url.path == "/fixtures"
        assert request.url.params["league"] == "39"
        assert request.url.params["season"] == "2024"

        return httpx.Response(
            200,
            json={
                "get": "fixtures",
                "results": [],
                "errors": {},
            },
        )

    budget = APIBudgetService(
        daily_limit=10,
        reserved_requests=2,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        result = client.get(
            "/fixtures",
            params={
                "league": 39,
                "season": 2024,
            },
        )

        assert result["get"] == "fixtures"
        assert result["results"] == []
        assert budget.requests_used == 1
        assert budget.requests_remaining == 7

    finally:
        client.close()


def test_get_builds_url_without_duplicate_slashes():
    def handler(request):
        assert str(request.url) == (
            "https://v3.football.api-sports.io/"
            "fixtures?league=39"
        )

        return httpx.Response(
            200,
            json={
                "results": [],
                "errors": {},
            },
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        client.get(
            "/fixtures",
            params={"league": 39},
        )
    finally:
        client.close()


def test_get_sends_api_key_header():
    def handler(request):
        assert (
            request.headers["x-apisports-key"]
            == client.headers["x-apisports-key"]
        )

        return httpx.Response(
            200,
            json={
                "results": [],
                "errors": {},
            },
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        client.get("/fixtures")
    finally:
        client.close()


def test_get_raises_when_budget_is_exhausted():
    budget = APIBudgetService(
        daily_limit=5,
        reserved_requests=1,
    )

    for _ in range(4):
        budget.record_request()

    def handler(request):
        raise AssertionError(
            "HTTP request should not be made "
            "when the budget is exhausted."
        )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        with pytest.raises(
            FootballAPIError,
            match="Daily football API budget has been reached",
        ):
            client.get("/fixtures")

        assert budget.requests_used == 4
        assert budget.requests_remaining == 0

    finally:
        client.close()


def test_get_records_budget_before_request():
    def handler(request):
        raise httpx.ConnectError(
            "connection failed"
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        with pytest.raises(
            FootballAPIError,
            match="Unable to connect to football provider",
        ):
            client.get("/fixtures")

        assert budget.requests_used == 1

    finally:
        client.close()


def test_get_converts_timeout_error():
    def handler(request):
        raise httpx.ReadTimeout(
            "request timed out"
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        with pytest.raises(
            FootballAPIError,
            match="Football provider request timed out",
        ):
            client.get("/fixtures")

    finally:
        client.close()


def test_get_converts_http_status_error():
    def handler(request):
        return httpx.Response(
            429,
            json={
                "message": "Too many requests",
            },
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        with pytest.raises(
            FootballAPIError,
            match="HTTP 429",
        ):
            client.get("/fixtures")

    finally:
        client.close()


def test_get_converts_server_error():
    def handler(request):
        return httpx.Response(
            500,
            json={
                "message": "Internal server error",
            },
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        with pytest.raises(
            FootballAPIError,
            match="HTTP 500",
        ):
            client.get("/fixtures")

    finally:
        client.close()


def test_get_converts_connection_error():
    def handler(request):
        raise httpx.ConnectError(
            "connection refused"
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        with pytest.raises(
            FootballAPIError,
            match="Unable to connect to football provider",
        ):
            client.get("/fixtures")

    finally:
        client.close()


def test_get_rejects_invalid_json():
    def handler(request):
        return httpx.Response(
            200,
            content=b"not-json",
            headers={
                "content-type": "application/json",
            },
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        with pytest.raises(
            FootballAPIError,
            match="Football provider returned invalid JSON",
        ):
            client.get("/fixtures")

    finally:
        client.close()


def test_get_rejects_provider_errors():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "results": [],
                "errors": {
                    "token": "Invalid API key",
                },
            },
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        with pytest.raises(
            FootballAPIError,
            match="Football provider error",
        ):
            client.get("/fixtures")

    finally:
        client.close()


def test_get_accepts_empty_provider_errors():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "fixture": {
                            "id": 123,
                        }
                    }
                ],
                "errors": {},
            },
        )

    budget = APIBudgetService(
        daily_limit=10,
    )

    client = make_client(
        handler,
        budget=budget,
    )

    try:
        result = client.get("/fixtures")

        assert result["results"][0]["fixture"]["id"] == 123

    finally:
        client.close()


def test_close_closes_http_client():
    budget = APIBudgetService(
        daily_limit=10,
    )

    client = FootballAPIClient(
        budget=budget
    )

    assert client.client.is_closed is False

    client.close()

    assert client.client.is_closed is True