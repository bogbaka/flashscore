from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MatchEvent(Base):
    __tablename__ = "match_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id"),
        nullable=False,
    )

    minute: Mapped[int | None] = mapped_column(nullable=True)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    player_name: Mapped[str | None] = mapped_column(String(100))
    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(String(255))