from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.match import MatchRepository


class MatchService:
    def __init__(self, db: Session):
        self.repository = MatchRepository(db)

    def get_all_matches(self):
        return self.repository.get_all()

    def get_match(self, match_id: int):
        return self.repository.get_by_id(match_id)

    def get_matches_by_status(self, status: str):
        return self.repository.get_by_status(status)

    def get_matches_by_date(self, start: datetime, end: datetime):
        return self.repository.get_by_date(start, end)