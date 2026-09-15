from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int | None] = mapped_column(nullable=True, unique=True)

    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
        nullable=False,
    )

    home_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
    )

    away_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
    )

    kickoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled")

    home_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)