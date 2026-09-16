from datetime import datetime

from sqlalchemy.orm import Session

from app.models.match import Match
from app.repositories.match import MatchRepository


class MatchService:
    def __init__(self, db: Session):
        self.repository = MatchRepository(db)

    def get_all_matches(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        return self.repository.get_all(
            page=page,
            limit=limit,
        )

    def get_match(
        self,
        match_id: int,
    ) -> Match | None:
        return self.repository.get_by_id(
            match_id
        )

    def get_matches_by_status(
        self,
        status: str,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        return self.repository.get_by_status(
            status=status,
            page=page,
            limit=limit,
        )

    def get_matches_by_date(
        self,
        start: datetime,
        end: datetime,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        return self.repository.get_by_date(
            start=start,
            end=end,
            page=page,
            limit=limit,
        )

    def get_match_details(
        self,
        match_id: int,
    ) -> Match | None:
        return self.repository.get_by_id(
            match_id
        )