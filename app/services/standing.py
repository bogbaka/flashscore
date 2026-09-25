from sqlalchemy.orm import Session

from app.models.standing import Standing
from app.repositories.standing import StandingRepository


class StandingService:
    def __init__(self, db: Session):
        self.repository = StandingRepository(db)

    def get_competition_standings(
        self,
        competition_id: int,
        season_year: int | None = None,
    ) -> list[Standing]:
        return self.repository.get_by_competition(
            competition_id,
            season_year,
        )

    def get_team_standing(
        self,
        team_id: int,
    ) -> Standing | None:
        return self.repository.get_by_team(
            team_id
        )