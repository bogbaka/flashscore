from sqlalchemy.orm import Session

from app.repositories.standing import StandingRepository


class StandingService:
    def __init__(self, db: Session):
        self.repository = StandingRepository(db)

    def get_by_competition(
        self,
        competition_id: int,
    ):
        return self.repository.get_by_competition(
            competition_id
        )