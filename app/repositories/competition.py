from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.competition import Competition
from app.models.match import Match
from app.models.season import Season


class CompetitionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Competition], int]:
        offset = (page - 1) * limit

        statement = (
            select(Competition)
            .order_by(Competition.name)
            .offset(offset)
            .limit(limit)
        )

        competitions = list(
            self.db.scalars(statement).all()
        )

        total = self.db.scalar(
            select(func.count())
            .select_from(Competition)
        ) or 0

        return competitions, total

    def get_by_id(
        self,
        competition_id: int,
    ) -> Competition | None:
        return self.db.get(
            Competition,
            competition_id,
        )

    def get_by_provider_id(
        self,
        provider_id: int,
    ) -> Competition | None:
        statement = select(Competition).where(
            Competition.provider_id == provider_id
        )

        return self.db.scalar(statement)

    def get_season(
        self,
        competition_id: int,
        year: int,
    ) -> Season | None:
        statement = select(Season).where(
            Season.competition_id == competition_id,
            Season.year == year,
        )

        return self.db.scalar(statement)

    def get_matches(
        self,
        competition_id: int,
        season_year: int | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Match], int]:
        offset = (page - 1) * limit

        statement = (
            select(Match)
            .where(
                Match.competition_id == competition_id
            )
            .options(
                joinedload(Match.competition),
                joinedload(Match.season),
                joinedload(Match.home_team),
                joinedload(Match.away_team),
            )
        )

        count_statement = (
            select(func.count())
            .select_from(Match)
            .where(
                Match.competition_id == competition_id
            )
        )

        if season_year is not None:
            statement = statement.join(
                Season,
                Match.season_id == Season.id,
            ).where(
                Season.year == season_year,
                Season.competition_id == competition_id,
            )

            count_statement = count_statement.join(
                Season,
                Match.season_id == Season.id,
            ).where(
                Season.year == season_year,
                Season.competition_id == competition_id,
            )

        statement = (
            statement
            .order_by(
    Match.kickoff_at,
    Match.id,
)
            .offset(offset)
            .limit(limit)
        )

        matches = list(
            self.db.scalars(statement).all()
        )

        total = self.db.scalar(
            count_statement
        ) or 0

        return matches, total