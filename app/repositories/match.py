from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.match import Match


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        offset = (page - 1) * limit

        statement = (
            select(Match)
            .order_by(Match.kickoff_at)
            .offset(offset)
            .limit(limit)
        )

        matches = list(
            self.db.scalars(statement).all()
        )

        total = self.db.scalar(
            select(func.count())
            .select_from(Match)
        ) or 0

        return matches, total

    def get_by_id(
        self,
        match_id: int,
    ) -> Match | None:
        statement = select(Match).where(
            Match.id == match_id
        )

        return self.db.scalar(statement)

    def get_by_status(
        self,
        status: str,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        offset = (page - 1) * limit

        statement = (
            select(Match)
            .where(Match.status == status)
            .order_by(Match.kickoff_at)
            .offset(offset)
            .limit(limit)
        )

        matches = list(
            self.db.scalars(statement).all()
        )

        total = self.db.scalar(
            select(func.count())
            .select_from(Match)
            .where(Match.status == status)
        ) or 0

        return matches, total

    def get_by_date(
        self,
        start: datetime,
        end: datetime,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        offset = (page - 1) * limit

        statement = (
            select(Match)
            .where(
                Match.kickoff_at >= start,
                Match.kickoff_at < end,
            )
            .order_by(Match.kickoff_at)
            .offset(offset)
            .limit(limit)
        )

        matches = list(
            self.db.scalars(statement).all()
        )

        total = self.db.scalar(
            select(func.count())
            .select_from(Match)
            .where(
                Match.kickoff_at >= start,
                Match.kickoff_at < end,
            )
        ) or 0

        return matches, total