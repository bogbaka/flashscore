from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Favorite(Base):
    __tablename__ = "favorites"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "team_id",
            name="uq_favorites_user_team",
        ),
        UniqueConstraint(
            "user_id",
            "competition_id",
            name="uq_favorites_user_competition",
        ),
        CheckConstraint(
            "(team_id IS NOT NULL) != "
            "(competition_id IS NOT NULL)",
            name="ck_favorites_exactly_one_target",
        ),
        Index(
            "ix_favorites_user_id",
            "user_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True,
    )

    competition_id: Mapped[int | None] = mapped_column(
        ForeignKey("competitions.id"),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="favorites",
    )

    team = relationship(
        "Team",
        back_populates="favorites",
        lazy="joined",
    )

    competition = relationship(
        "Competition",
        back_populates="favorites",
        lazy="joined",
    )