from datetime import date


class APIBudgetService:
    def __init__(
        self,
        daily_limit: int,
        reserved_requests: int = 0,
    ):
        if daily_limit <= 0:
            raise ValueError(
                "Daily API limit must be greater than zero."
            )

        if reserved_requests < 0:
            raise ValueError(
                "Reserved requests cannot be negative."
            )

        if reserved_requests >= daily_limit:
            raise ValueError(
                "Reserved requests must be less than the daily limit."
            )

        self.daily_limit = daily_limit
        self.reserved_requests = reserved_requests

        self._request_date = date.today()
        self._requests_used = 0

    @property
    def usable_limit(self) -> int:
        return (
            self.daily_limit
            - self.reserved_requests
        )

    @property
    def requests_used(self) -> int:
        self._reset_if_new_day()
        return self._requests_used

    @property
    def requests_remaining(self) -> int:
        self._reset_if_new_day()

        return max(
            0,
            self.usable_limit
            - self._requests_used,
        )

    def can_make_request(self) -> bool:
        return self.requests_remaining > 0

    def record_request(self) -> None:
        self._reset_if_new_day()

        if not self.can_make_request():
            raise RuntimeError(
                "Daily football API budget has been reached."
            )

        self._requests_used += 1

    def _reset_if_new_day(self) -> None:
        today = date.today()

        if today != self._request_date:
            self._request_date = today
            self._requests_used = 0
