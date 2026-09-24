from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.football_api.client import FootballAPIClient
from app.models.competition import Competition
from app.models.match import Match
from app.models.team import Team


class MatchSyncService:
    def __init__(
        self,
        db: Session,
        client: FootballAPIClient | None = None,
    ):
        self.db = db
        self.client = client or FootballAPIClient()
        self._owns_client = client is None

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
            if team.provider_id is not None
        }

        fixtures = data.get("response", [])

        if not fixtures:
            return []

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
        skipped_fixtures = []

        for item in fixtures:
            fixture = item["fixture"]
            fixture_teams = item["teams"]
            goals = item["goals"]

            home_provider_id = fixture_teams["home"]["id"]
            away_provider_id = fixture_teams["away"]["id"]

            home_team = teams_by_provider_id.get(
                home_provider_id
            )
            away_team = teams_by_provider_id.get(
                away_provider_id
            )

            if home_team is None or away_team is None:
                skipped_fixtures.append(
                    {
                        "fixture_id": fixture["id"],
                        "home_team_id": home_provider_id,
                        "away_team_id": away_provider_id,
                    }
                )
                continue

            kickoff_at = datetime.fromisoformat(
                fixture["date"].replace("Z", "+00:00")
            )

            match = matches_by_provider_id.get(
                fixture["id"]
            )

            home_score = goals.get("home") or 0
            away_score = goals.get("away") or 0
            status = fixture["status"]["short"]

            if match is None:
                match = Match(
                    provider_id=fixture["id"],
                    competition_id=competition.id,
                    season_id=season_id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    kickoff_at=kickoff_at,
                    status=status,
                    home_score=home_score,
                    away_score=away_score,
                )
                self.db.add(match)
            else:
                match.competition_id = competition.id
                match.season_id = season_id
                match.home_team_id = home_team.id
                match.away_team_id = away_team.id
                match.kickoff_at = kickoff_at
                match.status = status
                match.home_score = home_score
                match.away_score = away_score

            matches.append(match)

        if skipped_fixtures:
            print(
                f"Warning: skipped {len(skipped_fixtures)} "
                "fixtures because their teams were not found."
            )

        self.db.flush()

        return matches

    def close(self) -> None:
        if self._owns_client:
            self.client.close()