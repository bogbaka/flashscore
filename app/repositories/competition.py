from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.models.match import Match


class CompetitionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Competition], int]:
        offset = (page - 1) * limit

        statement = (
            select(Competition)
            .order_by(Competition.name)
            .offset(offset)
            .limit(limit)
        )

        competitions = list(
            self.db.scalars(statement).all()
        )

        total = self.db.scalar(
            select(func.count())
            .select_from(Competition)
        ) or 0

        return competitions, total

    def get_by_id(
        self,
        competition_id: int,
    ) -> Competition | None:
        return self.db.get(
            Competition,
            competition_id,
        )

    def get_matches(
        self,
        competition_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        offset = (page - 1) * limit

        statement = (
            select(Match)
            .where(
                Match.competition_id == competition_id
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
                Match.competition_id == competition_id
            )
        ) or 0

        return matches, total