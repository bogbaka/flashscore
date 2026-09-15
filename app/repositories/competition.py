from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.competition import Competition


class CompetitionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Competition]:
        statement = select(Competition).order_by(Competition.name)
        return list(self.db.scalars(statement).all())

    def get_by_id(self, competition_id: int) -> Competition | None:
        statement = select(Competition).where(
            Competition.id == competition_id
        )
        return self.db.scalar(statement)