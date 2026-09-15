from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Standing(Base):
    __tablename__ = "standings"

    id: Mapped[int] = mapped_column(primary_key=True)

    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
        nullable=False,
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(Integer, nullable=False)
    played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    draws: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    goals_for: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    goals_against: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)