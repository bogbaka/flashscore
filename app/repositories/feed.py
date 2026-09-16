from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.models.competition import Competition
from app.models.match import Match
from app.models.team import Team


class FeedRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_matches(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        statuses: list[str] | None = None,
    ):
        home_team = aliased(Team)
        away_team = aliased(Team)

        statement = (
            select(
                Match,
                home_team,
                away_team,
                Competition,
            )
            .join(
                Competition,
                Match.competition_id == Competition.id,
            )
            .join(
                home_team,
                Match.home_team_id == home_team.id,
            )
            .join(
                away_team,
                Match.away_team_id == away_team.id,
            )
        )

        if start is not None:
            statement = statement.where(
                Match.kickoff_at >= start
            )

        if end is not None:
            statement = statement.where(
                Match.kickoff_at < end
            )

        if statuses:
            statement = statement.where(
                Match.status.in_(statuses)
            )

        statement = statement.order_by(
            Match.kickoff_at
        )

        return list(
            self.db.execute(statement).all()
        )