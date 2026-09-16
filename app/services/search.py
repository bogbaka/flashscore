from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.models.team import Team
from app.repositories.search import SearchRepository


class SearchService:
    def __init__(self, db: Session):
        self.repository = SearchRepository(db)

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, list[Team | Competition]]:
        return {
            "teams": self.repository.search_teams(
                query=query,
                limit=limit,
            ),
            "competitions": (
                self.repository.search_competitions(
                    query=query,
                    limit=limit,
                )
            ),
        }