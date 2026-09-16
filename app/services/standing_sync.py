from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.football_api.client import FootballAPIClient
from app.models.competition import Competition
from app.models.standing import Standing
from app.models.team import Team


class StandingSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = FootballAPIClient()

    def sync_standings(
        self,
        league_id: int,
        season: int,
        season_id: int,
    ) -> list[Standing]:
        data = self.client.get(
            "standings",
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
                "Competition must be synced before standings."
            )

        standings_data = (
            data["response"][0]
            ["league"]["standings"][0]
        )

        self.db.query(Standing).filter(
            Standing.competition_id == competition.id,
            Standing.season_id == season_id,
        ).delete()

        teams = self.db.scalars(
            select(Team)
        ).all()

        teams_by_provider_id = {
            team.provider_id: team
            for team in teams
        }

        standings = []

        for item in standings_data:
            team_data = item["team"]

            team = teams_by_provider_id.get(
                team_data["id"]
            )

            if team is None:
                continue

            standing = Standing(
                competition_id=competition.id,
                season_id=season_id,
                team_id=team.id,
                position=item["rank"],
                played=item["all"]["played"],
                wins=item["all"]["win"],
                draws=item["all"]["draw"],
                losses=item["all"]["lose"],
                goals_for=item["all"]["goals"]["for"],
                goals_against=item["all"]["goals"]["against"],
                points=item["points"],
            )

            self.db.add(standing)
            standings.append(standing)

        return standings