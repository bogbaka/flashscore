from sqlalchemy.orm import Session

from app.integrations.football_api.client import FootballAPIClient
from app.models.competition import Competition


class FootballSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = FootballAPIClient()

    def sync_competition(self, name: str) -> Competition:
        data = self.client.get(
            "leagues",
            {"name": name},
        )

        league = data["response"][0]

        provider_id = league["league"]["id"]

        competition = (
            self.db.query(Competition)
            .filter(Competition.provider_id == provider_id)
            .first()
        )

        if competition is None:
            competition = Competition(
                provider_id=provider_id,
                name=league["league"]["name"],
                country=league["country"]["name"],
                logo_url=league["league"]["logo"],
            )
            self.db.add(competition)
        else:
            competition.name = league["league"]["name"]
            competition.country = league["country"]["name"]
            competition.logo_url = league["league"]["logo"]

        self.db.commit()
        self.db.refresh(competition)

        return competition