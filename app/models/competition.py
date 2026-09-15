from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int | None] = mapped_column(nullable=True, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str | None] = mapped_column(String(100))
    logo_url: Mapped[str | None] = mapped_column(String(500))