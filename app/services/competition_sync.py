from sqlalchemy.orm import Session

from app.config import SUPPORTED_COMPETITIONS
from app.integrations.football_api.client import FootballAPIClient
from app.models.competition import Competition


class CompetitionSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = FootballAPIClient()

    def sync_competition(
        self,
        slug: str,
    ) -> Competition:
        competition_config = SUPPORTED_COMPETITIONS.get(slug)

        if competition_config is None:
            raise ValueError(
                f"Unsupported competition: {slug}"
            )

        provider_id = competition_config["provider_id"]

        data = self.client.get(
            "leagues",
            {
                "id": provider_id,
            },
        )

        if not data["response"]:
            raise ValueError(
                f"Competition not found: {slug}"
            )

        item = data["response"][0]

        league = item["league"]
        country = item.get("country") or {}

        competition = (
            self.db.query(Competition)
            .filter(
                Competition.provider_id == provider_id
            )
            .first()
        )

        if competition is None:
            competition = Competition(
                provider_id=provider_id,
                name=league["name"],
                country=country.get("name"),
                logo_url=league.get("logo"),
            )

            self.db.add(competition)

        else:
            competition.name = league["name"]
            competition.country = country.get("name")
            competition.logo_url = league.get("logo")

        return competition

    def sync_all(
        self,
    ) -> list[Competition]:
        competitions = []

        for slug in SUPPORTED_COMPETITIONS:
            competitions.append(
                self.sync_competition(slug)
            )

        return competitions