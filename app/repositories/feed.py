from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.match import Match


LIVE_STATUSES = {
    "1H",
    "HT",
    "2H",
    "ET",
    "BT",
    "P",
    "LIVE",
}

FINISHED_STATUSES = {
    "FT",
    "AET",
    "PEN",
}


class FeedRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_live_matches(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Match]:
        statement = (
            select(Match)
            .where(
                Match.status.in_(LIVE_STATUSES),
                Match.kickoff_at >= start,
                Match.kickoff_at < end,
            )
            .order_by(Match.kickoff_at)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_matches_by_date(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Match]:
        statement = (
            select(Match)
            .where(
                Match.kickoff_at >= start,
                Match.kickoff_at < end,
            )
            .order_by(Match.kickoff_at)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_upcoming_matches(
        self,
        now: datetime,
        limit: int = 20,
    ) -> list[Match]:
        statement = (
            select(Match)
            .where(
                Match.kickoff_at > now,
                ~Match.status.in_(FINISHED_STATUSES),
            )
            .order_by(Match.kickoff_at)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_finished_matches(
        self,
        limit: int = 20,
    ) -> list[Match]:
        statement = (
            select(Match)
            .where(
                Match.status.in_(FINISHED_STATUSES)
            )
            .order_by(Match.kickoff_at.desc())
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )