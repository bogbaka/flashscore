import pytest

from app.services.api_budget import APIBudgetService


def test_budget_starts_with_full_usable_limit():
    budget = APIBudgetService(
        daily_limit=100,
        reserved_requests=20,
    )

    assert budget.usable_limit == 80
    assert budget.requests_used == 0
    assert budget.requests_remaining == 80
    assert budget.can_make_request() is True


def test_budget_records_requests():
    budget = APIBudgetService(
        daily_limit=10,
        reserved_requests=2,
    )

    budget.record_request()
    budget.record_request()

    assert budget.requests_used == 2
    assert budget.requests_remaining == 6


def test_budget_stops_at_usable_limit():
    budget = APIBudgetService(
        daily_limit=5,
        reserved_requests=1,
    )

    for _ in range(4):
        budget.record_request()

    assert budget.requests_remaining == 0
    assert budget.can_make_request() is False

    with pytest.raises(RuntimeError):
        budget.record_request()


def test_budget_rejects_invalid_daily_limit():
    with pytest.raises(ValueError):
        APIBudgetService(daily_limit=0)


def test_budget_rejects_negative_reserved_requests():
    with pytest.raises(ValueError):
        APIBudgetService(
            daily_limit=100,
            reserved_requests=-1,
        )


def test_budget_rejects_reserved_requests_equal_to_limit():
    with pytest.raises(ValueError):
        APIBudgetService(
            daily_limit=100,
            reserved_requests=100,
        )