from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.models.match import Match
from app.models.match_event import MatchEvent
from app.models.team import Team
from app.repositories.match import MatchRepository


class MatchService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = MatchRepository(db)

    def get_all_matches(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        return self.repository.get_all(
            page,
            limit,
        )

    def get_match(
        self,
        match_id: int,
    ) -> Match | None:
        return self.repository.get_by_id(match_id)

    def get_matches_by_status(
        self,
        status: str,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        return self.repository.get_by_status(
            status,
            page,
            limit,
        )

    def get_matches_by_date(
        self,
        start: datetime,
        end: datetime,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        return self.repository.get_by_date(
            start,
            end,
            page,
            limit,
        )

    def get_match_details(
        self,
        match_id: int,
    ):
        match = self.repository.get_by_id(match_id)

        if match is None:
            return None

        competition = self.db.get(
            Competition,
            match.competition_id,
        )

        home_team = self.db.get(
            Team,
            match.home_team_id,
        )

        away_team = self.db.get(
            Team,
            match.away_team_id,
        )

        events = self.db.scalars(
            select(MatchEvent)
            .where(
                MatchEvent.match_id == match.id
            )
            .order_by(MatchEvent.minute)
        ).all()

        return {
            "id": match.id,
            "competition_id": match.competition_id,
            "home_team_id": match.home_team_id,
            "away_team_id": match.away_team_id,
            "kickoff_at": match.kickoff_at,
            "status": match.status,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "competition": competition,
            "home_team": home_team,
            "away_team": away_team,
            "events": list(events),
        }

