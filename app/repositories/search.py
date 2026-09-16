from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.models.team import Team


class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_teams(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Team]:
        statement = (
            select(Team)
            .where(
                or_(
                    Team.name.ilike(f"%{query}%"),
                    Team.short_name.ilike(f"%{query}%"),
                )
            )
            .order_by(Team.name)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def search_competitions(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Competition]:
        statement = (
            select(Competition)
            .where(
                or_(
                    Competition.name.ilike(
                        f"%{query}%"
                    ),
                    Competition.country.ilike(
                        f"%{query}%"
                    ),
                )
            )
            .order_by(Competition.name)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )