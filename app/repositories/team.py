from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.match import Match
from app.models.standing import Standing
from app.models.team import Team


class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Team], int]:
        offset = (page - 1) * limit

        statement = (
            select(Team)
            .order_by(Team.name)
            .offset(offset)
            .limit(limit)
        )

        teams = list(
            self.db.scalars(statement).all()
        )

        total = self.db.scalar(
            select(func.count()).select_from(Team)
        ) or 0

        return teams, total

    def get_by_id(
        self,
        team_id: int,
    ) -> Team | None:
        return self.db.get(Team, team_id)

    def get_matches(
        self,
        team_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        offset = (page - 1) * limit

        statement = (
            select(Match)
            .where(
                (Match.home_team_id == team_id)
                | (Match.away_team_id == team_id)
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
                (Match.home_team_id == team_id)
                | (Match.away_team_id == team_id)
            )
        ) or 0

        return matches, total

    def get_standing(
        self,
        team_id: int,
    ) -> Standing | None:
        statement = (
            select(Standing)
            .where(Standing.team_id == team_id)
            .order_by(Standing.position)
        )

        return self.db.scalar(statement)