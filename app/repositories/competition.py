from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.models.match import Match
from app.models.standing import Standing


class CompetitionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Competition]:
        statement = select(Competition).order_by(Competition.name)
        return list(self.db.scalars(statement).all())

    def get_by_id(
        self,
        competition_id: int,
    ) -> Competition | None:
        statement = select(Competition).where(
            Competition.id == competition_id
        )
        return self.db.scalar(statement)

    def get_matches(
        self,
        competition_id: int,
    ) -> list[Match]:
        statement = (
            select(Match)
            .where(Match.competition_id == competition_id)
            .order_by(Match.kickoff_at)
        )

        return list(self.db.scalars(statement).all())

    def get_standings(
        self,
        competition_id: int,
    ) -> list[Standing]:
        statement = (
            select(Standing)
            .where(
                Standing.competition_id == competition_id
            )
            .order_by(Standing.position)
        )

        return list(self.db.scalars(statement).all())