from datetime import date, timedelta

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


def test_budget_does_not_consume_reserved_requests():
    budget = APIBudgetService(
        daily_limit=10,
        reserved_requests=3,
    )

    for _ in range(7):
        budget.record_request()

    assert budget.requests_used == 7
    assert budget.requests_remaining == 0
    assert budget.usable_limit == 7
    assert budget.can_make_request() is False


def test_budget_resets_when_day_changes():
    budget = APIBudgetService(
        daily_limit=10,
        reserved_requests=2,
    )

    budget.record_request()
    budget.record_request()
    budget.record_request()

    assert budget.requests_used == 3
    assert budget.requests_remaining == 5

    budget._request_date = date.today() - timedelta(days=1)

    assert budget.requests_used == 0
    assert budget.requests_remaining == 8
    assert budget.can_make_request() is True


def test_budget_can_make_request_until_usable_limit():
    budget = APIBudgetService(
        daily_limit=3,
        reserved_requests=1,
    )

    assert budget.can_make_request() is True

    budget.record_request()

    assert budget.can_make_request() is True

    budget.record_request()

    assert budget.can_make_request() is False


def test_budget_rejects_invalid_daily_limit():
    with pytest.raises(ValueError):
        APIBudgetService(daily_limit=0)


def test_budget_rejects_negative_daily_limit():
    with pytest.raises(ValueError):
        APIBudgetService(daily_limit=-1)


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


def test_budget_rejects_reserved_requests_above_limit():
    with pytest.raises(ValueError):
        APIBudgetService(
            daily_limit=100,
            reserved_requests=101,
        )