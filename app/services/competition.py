from sqlalchemy.orm import Session

from app.repositories.competition import CompetitionRepository


class CompetitionService:
    def __init__(self, db: Session):
        self.repository = CompetitionRepository(db)

    def get_all_competitions(self):
        return self.repository.get_all()

    def get_competition(self, competition_id: int):
        return self.repository.get_by_id(competition_id)