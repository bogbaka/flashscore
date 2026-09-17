from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.standing import Standing


class StandingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_competition(
        self,
        competition_id: int,
    ) -> list[Standing]:
        statement = (
            select(Standing)
            .where(
                Standing.competition_id == competition_id
            )
            .options(
                joinedload(Standing.team),
                joinedload(Standing.competition),
                joinedload(Standing.season),
            )
            .order_by(Standing.position)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_team(
        self,
        team_id: int,
    ) -> Standing | None:
        statement = (
            select(Standing)
            .where(
                Standing.team_id == team_id
            )
            .options(
                joinedload(Standing.team),
                joinedload(Standing.competition),
                joinedload(Standing.season),
            )
            .order_by(Standing.position)
        )

        return self.db.scalar(statement)