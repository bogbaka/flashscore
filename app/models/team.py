from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Team(Base):
    __tablename__ = "teams"

    __table_args__ = (
        UniqueConstraint(
            "provider_id",
            name="uq_teams_provider_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    provider_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    short_name: Mapped[str | None] = mapped_column(
        String(50),
    )

    logo_url: Mapped[str | None] = mapped_column(
        String(500),
    )

    favorites = relationship(
        "Favorite",
        back_populates="team",
        lazy="selectin",
    )