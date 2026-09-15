from datetime import datetime

from sqlalchemy.orm import Session

from app.integrations.football_api.client import FootballAPIClient
from app.models.competition import Competition
from app.models.match import Match
from app.models.team import Team


class MatchSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = FootballAPIClient()

    def sync_matches(
        self,
        league_id: int,
        season: int,
    ) -> list[Match]:
        data = self.client.get(
            "fixtures",
            {
                "league": league_id,
                "season": season,
            },
        )

        competition = (
            self.db.query(Competition)
            .filter(Competition.provider_id == league_id)
            .first()
        )

        if competition is None:
            raise ValueError(
                "Competition must be synced before matches."
            )

        matches = []

        for item in data["response"]:
            fixture = item["fixture"]
            teams = item["teams"]
            goals = item["goals"]

            home_team = (
                self.db.query(Team)
                .filter(
                    Team.provider_id == teams["home"]["id"]
                )
                .first()
            )

            away_team = (
                self.db.query(Team)
                .filter(
                    Team.provider_id == teams["away"]["id"]
                )
                .first()
            )

            if home_team is None or away_team is None:
                continue

            match = (
                self.db.query(Match)
                .filter(
                    Match.provider_id == fixture["id"]
                )
                .first()
            )

            kickoff_at = datetime.fromisoformat(
                fixture["date"]
            )

            if match is None:
                match = Match(
                    provider_id=fixture["id"],
                    competition_id=competition.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    kickoff_at=kickoff_at,
                    status=fixture["status"]["short"],
                    home_score=goals["home"] or 0,
                    away_score=goals["away"] or 0,
                )

                self.db.add(match)

            else:
                match.competition_id = competition.id
                match.home_team_id = home_team.id
                match.away_team_id = away_team.id
                match.kickoff_at = kickoff_at
                match.status = fixture["status"]["short"]
                match.home_score = goals["home"] or 0
                match.away_score = goals["away"] or 0

            matches.append(match)

        self.db.commit()

        for match in matches:
            self.db.refresh(match)

        return matches