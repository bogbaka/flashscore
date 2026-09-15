from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.match import Match


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Match]:
        statement = select(Match).order_by(Match.kickoff_at)
        return list(self.db.scalars(statement).all())

    def get_by_id(self, match_id: int) -> Match | None:
        statement = select(Match).where(Match.id == match_id)
        return self.db.scalar(statement)

    def get_by_status(self, status: str) -> list[Match]:
        statement = (
            select(Match)
            .where(Match.status == status)
            .order_by(Match.kickoff_at)
        )
        return list(self.db.scalars(statement).all())

    def get_by_date(self, start: datetime, end: datetime) -> list[Match]:
        statement = (
            select(Match)
            .where(
                Match.kickoff_at >= start,
                Match.kickoff_at < end,
            )
            .order_by(Match.kickoff_at)
        )
        return list(self.db.scalars(statement).all())