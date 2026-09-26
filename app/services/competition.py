from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.models.match import Match
from app.repositories.competition import CompetitionRepository


class CompetitionService:
    def __init__(self, db: Session):
        self.repository = CompetitionRepository(db)

    def get_all_competitions(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Competition], int]:
        return self.repository.get_all(
            page=page,
            limit=limit,
        )

    def get_competition(
        self,
        competition_id: int,
    ) -> Competition | None:
        return self.repository.get_by_id(
            competition_id
        )

    def get_competition_matches(
        self,
        competition_id: int,
        season_year: int | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        return self.repository.get_matches(
            competition_id=competition_id,
            season_year=season_year,
            page=page,
            limit=limit,
        )