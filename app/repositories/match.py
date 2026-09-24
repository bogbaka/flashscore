from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.match import Match


LIVE_STATUSES = (
    "1H",
    "HT",
    "2H",
    "ET",
    "BT",
    "P",
    "LIVE",
)


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        page: int,
        limit: int,
    ) -> tuple[list[Match], int]:
        query = (
            select(Match)
            .options(
                joinedload(Match.competition),
                joinedload(Match.home_team),
                joinedload(Match.away_team),
            )
            .order_by(
                Match.kickoff_at,
                Match.id,
            )
        )

        return self._paginate(
            query,
            page,
            limit,
        )

    def get_by_status(
        self,
        status: str,
        page: int,
        limit: int,
    ) -> tuple[list[Match], int]:
        query = (
            select(Match)
            .where(
                Match.status == status
            )
            .options(
                joinedload(Match.competition),
                joinedload(Match.home_team),
                joinedload(Match.away_team),
            )
            .order_by(
                Match.kickoff_at,
                Match.id,
            )
        )

        return self._paginate(
            query,
            page,
            limit,
        )

    def get_live(
        self,
        page: int,
        limit: int,
    ) -> tuple[list[Match], int]:
        query = (
            select(Match)
            .where(
                Match.status.in_(LIVE_STATUSES)
            )
            .options(
                joinedload(Match.competition),
                joinedload(Match.home_team),
                joinedload(Match.away_team),
            )
            .order_by(
                Match.kickoff_at,
                Match.id,
            )
        )

        return self._paginate(
            query,
            page,
            limit,
        )

    def get_by_date(
        self,
        start: datetime,
        end: datetime,
        page: int,
        limit: int,
    ) -> tuple[list[Match], int]:
        query = (
            select(Match)
            .where(
                Match.kickoff_at >= start,
                Match.kickoff_at < end,
            )
            .options(
                joinedload(Match.competition),
                joinedload(Match.home_team),
                joinedload(Match.away_team),
            )
            .order_by(
                Match.kickoff_at,
                Match.id,
            )
        )

        return self._paginate(
            query,
            page,
            limit,
        )

    def get_by_id(
        self,
        match_id: int,
    ) -> Match | None:
        query = (
            select(Match)
            .where(
                Match.id == match_id
            )
            .options(
                joinedload(Match.competition),
                joinedload(Match.home_team),
                joinedload(Match.away_team),
            )
        )

        return self.db.scalar(query)

    def _paginate(
        self,
        query,
        page: int,
        limit: int,
    ) -> tuple[list[Match], int]:
        count_query = select(
            func.count()
        ).select_from(
            query.subquery()
        )

        total = self.db.scalar(
            count_query
        ) or 0

        offset = (page - 1) * limit

        matches = self.db.scalars(
            query.offset(offset).limit(limit)
        ).all()

        return matches, total