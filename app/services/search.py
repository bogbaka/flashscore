from sqlalchemy.orm import Session

from app.repositories.competition import CompetitionRepository
from app.repositories.team import TeamRepository


class SearchService:
    def __init__(self, db: Session):
        self.team_repository = TeamRepository(db)
        self.competition_repository = CompetitionRepository(db)

    def search(self, query: str):
        query = query.strip()

        if not query:
            return {
                "teams": [],
                "competitions": [],
            }

        return {
            "teams": self.team_repository.search(query),
            "competitions": self.competition_repository.search(
                query
            ),
        }