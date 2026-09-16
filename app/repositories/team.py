from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.match import Match
from app.models.team import Team


class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Team]:
        statement = select(Team).order_by(Team.name)
        return list(self.db.scalars(statement).all())

    def get_by_id(self, team_id: int) -> Team | None:
        statement = select(Team).where(Team.id == team_id)
        return self.db.scalar(statement)

    def get_matches(self, team_id: int) -> list[Match]:
        statement = (
            select(Match)
            .where(
                (Match.home_team_id == team_id)
                | (Match.away_team_id == team_id)
            )
            .order_by(Match.kickoff_at)
        )

        return list(self.db.scalars(statement).all())