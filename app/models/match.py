from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Match(Base):
    __tablename__ = "matches"

    __table_args__ = (
        Index(
            "ix_matches_kickoff_at",
            "kickoff_at",
        ),
        Index(
            "ix_matches_status",
            "status",
        ),
        Index(
            "ix_matches_competition_id",
            "competition_id",
        ),
        Index(
            "ix_matches_home_team_id",
            "home_team_id",
        ),
        Index(
            "ix_matches_away_team_id",
            "away_team_id",
        ),
        Index(
            "ix_matches_season_id",
            "season_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    provider_id: Mapped[int | None] = mapped_column(
        nullable=True,
        unique=True,
    )

    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
        nullable=False,
    )

    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id"),
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

    kickoff_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="scheduled",
    )

    home_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    away_score: Mapped[int] = mapped_column(
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
        back_populates="matches",
        lazy="joined",
    )

    home_team = relationship(
        "Team",
        foreign_keys=[home_team_id],
        lazy="joined",
    )

    away_team = relationship(
        "Team",
        foreign_keys=[away_team_id],
        lazy="joined",
    )

    events = relationship(
        "MatchEvent",
        lazy="selectin",
        order_by="MatchEvent.minute",
    )