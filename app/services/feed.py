from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.match import Match
from app.repositories.feed import FeedRepository


class FeedService:
    def __init__(self, db: Session):
        self.repository = FeedRepository(db)

    def get_feed(
        self,
        start: datetime,
        end: datetime,
        limit: int = 20,
        now: datetime | None = None,
    ) -> dict[str, list[Match]]:
        current_time = (
            now
            or datetime.now(timezone.utc)
        )

        today_matches = (
            self.repository.get_matches_by_date(
                start=start,
                end=end,
            )
        )

        live_matches = (
            self.repository.get_live_matches(
                start=start,
                end=end,
            )
        )

        upcoming_matches = (
            self.repository.get_upcoming_matches(
                now=current_time,
                limit=limit,
            )
        )

        finished_matches = (
            self.repository.get_finished_matches(
                start=start,
                end=end,
                limit=limit,
            )
        )

        return {
            "live": live_matches,
            "today": today_matches,
            "upcoming": upcoming_matches,
            "finished": finished_matches,
        }