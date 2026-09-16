from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Season(Base):
    __tablename__ = "seasons"

    __table_args__ = (
        UniqueConstraint(
            "competition_id",
            "year",
            name="uq_seasons_competition_year",
        ),
        Index(
            "ix_seasons_competition_id",
            "competition_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    competition = relationship(
        "Competition",
        back_populates="seasons",
        lazy="joined",
    )

    matches = relationship(
        "Match",
        back_populates="season",
        lazy="selectin",
    )

    standings = relationship(
        "Standing",
        back_populates="season",
        lazy="selectin",
    )