from datetime import datetime

from sqlalchemy import select
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
        season_id: int,
    ) -> list[Match]:
        data = self.client.get(
            "fixtures",
            {
                "league": league_id,
                "season": season,
            },
        )

        competition = self.db.scalar(
            select(Competition).where(
                Competition.provider_id == league_id
            )
        )

        if competition is None:
            raise ValueError(
                "Competition must be synced before matches."
            )

        teams = self.db.scalars(
            select(Team)
        ).all()

        teams_by_provider_id = {
            team.provider_id: team
            for team in teams
        }

        fixtures = data["response"]

        provider_ids = [
            item["fixture"]["id"]
            for item in fixtures
        ]

        existing_matches = self.db.scalars(
            select(Match).where(
                Match.provider_id.in_(provider_ids)
            )
        ).all()

        matches_by_provider_id = {
            match.provider_id: match
            for match in existing_matches
        }

        matches = []

        for item in fixtures:
            fixture = item["fixture"]
            fixture_teams = item["teams"]
            goals = item["goals"]

            home_team = teams_by_provider_id.get(
                fixture_teams["home"]["id"]
            )

            away_team = teams_by_provider_id.get(
                fixture_teams["away"]["id"]
            )

            if home_team is None or away_team is None:
                continue

            match = matches_by_provider_id.get(
                fixture["id"]
            )

            kickoff_at = datetime.fromisoformat(
                fixture["date"]
            )

            if match is None:
                match = Match(
                    provider_id=fixture["id"],
                    competition_id=competition.id,
                    season_id=season_id,
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
                match.season_id = season_id
                match.home_team_id = home_team.id
                match.away_team_id = away_team.id
                match.kickoff_at = kickoff_at
                match.status = fixture["status"]["short"]
                match.home_score = goals["home"] or 0
                match.away_score = goals["away"] or 0

            matches.append(match)

        return matches