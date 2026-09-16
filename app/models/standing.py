from sqlalchemy import ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Standing(Base):
    __tablename__ = "standings"

    __table_args__ = (
        Index(
            "ix_standings_competition_id",
            "competition_id",
        ),
        Index(
            "ix_standings_team_id",
            "team_id",
        ),
        Index(
            "ix_standings_season_id",
            "season_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
        nullable=False,
    )

    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id"),
        nullable=False,
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    played: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    draws: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    losses: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    goals_for: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    goals_against: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    competition = relationship(
        "Competition",
        lazy="joined",
    )

    season = relationship(
        "Season",
        back_populates="standings",
        lazy="joined",
    )

    team = relationship(
        "Team",
        lazy="joined",
    )