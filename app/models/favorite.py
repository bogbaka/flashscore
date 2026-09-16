from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

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
    )

    id: Mapped[int] = mapped_column(primary_key=True)

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