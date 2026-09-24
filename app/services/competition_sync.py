from sqlalchemy.orm import Session

from app.config import SUPPORTED_COMPETITIONS
from app.integrations.football_api.client import FootballAPIClient
from app.models.competition import Competition
from app.repositories.competition import CompetitionRepository


class CompetitionSyncService:
    def __init__(
        self,
        db: Session,
        football_api: FootballAPIClient | None = None,
    ):
        self.db = db
        self.repository = CompetitionRepository(db)
        self.football_api = (
            football_api
            or FootballAPIClient()
        )
        self._owns_client = football_api is None

    def sync_competition(
        self,
        slug: str,
    ) -> Competition:
        config = SUPPORTED_COMPETITIONS.get(slug)

        if config is None:
            raise ValueError(
                f"Unsupported competition: {slug}"
            )

        provider_id = config["provider_id"]

        competition = (
            self.repository.get_by_provider_id(
                provider_id
            )
        )

        if competition is None:
            competition = Competition(
                provider_id=provider_id,
                name=config["name"],
                country=config["country"],
            )

            self.db.add(competition)
            self.db.flush()

        else:
            competition.name = config["name"]
            competition.country = config["country"]

        data = self.football_api.get(
            "/leagues",
            {"id": provider_id},
        )

        response = data.get("response", [])

        if response:
            league_data = response[0].get(
                "league",
                {},
            )

            country_data = response[0].get(
                "country",
                {},
            )

            competition.name = league_data.get(
                "name",
                competition.name,
            )

            competition.country = country_data.get(
                "name",
                competition.country,
            )

            competition.logo_url = league_data.get(
                "logo",
                competition.logo_url,
            )

        self.db.flush()

        return competition

    def close(self) -> None:
        if self._owns_client:
            self.football_api.close()