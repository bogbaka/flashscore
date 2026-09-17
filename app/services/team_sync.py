from sqlalchemy.orm import Session

from app.integrations.football_api.client import FootballAPIClient
from app.models.team import Team


class TeamSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = FootballAPIClient()

    def sync_teams(
        self,
        league_id: int,
        season: int,
    ) -> list[Team]:
        data = self.client.get(
            "teams",
            {
                "league": league_id,
                "season": season,
            },
        )

        teams = []

        for item in data["response"]:
            team_data = item["team"]
            provider_id = team_data["id"]

            team = (
                self.db.query(Team)
                .filter(Team.provider_id == provider_id)
                .first()
            )

            if team is None:
                team = Team(
                    provider_id=provider_id,
                    name=team_data["name"],
                    short_name=team_data.get("code"),
                    logo_url=team_data.get("logo"),
                )
                self.db.add(team)
            else:
                team.name = team_data["name"]
                team.short_name = team_data.get("code")
                team.logo_url = team_data.get("logo")

            teams.append(team)

        # Make newly-created teams visible to the next sync step.
        self.db.flush()

        return teams