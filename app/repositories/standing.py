from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.season import Season
from app.models.standing import Standing


class StandingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_competition(
        self,
        competition_id: int,
        season_year: int | None = None,
    ) -> list[Standing]:
        statement = (
            select(Standing)
            .where(
                Standing.competition_id == competition_id
            )
        )

        if season_year is not None:
            season_id = self.db.scalar(
                select(Season.id).where(
                    Season.competition_id == competition_id,
                    Season.year == season_year,
                )
            )

            if season_id is None:
                return []

            statement = statement.where(
                Standing.season_id == season_id
            )

        statement = (
            statement
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