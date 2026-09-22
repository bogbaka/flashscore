from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.favorite import Favorite


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_team_favorite(
        self,
        user_id: int,
        team_id: int,
    ) -> Favorite | None:
        return self.db.scalar(
            select(Favorite)
            .options(
                joinedload(Favorite.team),
            )
            .where(
                Favorite.user_id == user_id,
                Favorite.team_id == team_id,
            )
        )

    def get_competition_favorite(
        self,
        user_id: int,
        competition_id: int,
    ) -> Favorite | None:
        return self.db.scalar(
            select(Favorite)
            .options(
                joinedload(Favorite.competition),
            )
            .where(
                Favorite.user_id == user_id,
                Favorite.competition_id == competition_id,
            )
        )

    def add(
        self,
        favorite: Favorite,
    ) -> Favorite:
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)

        return favorite

    def delete(
        self,
        favorite: Favorite,
    ) -> None:
        self.db.delete(favorite)
        self.db.commit()

    def list_for_user(
        self,
        user_id: int,
    ) -> list[Favorite]:
        statement = (
            select(Favorite)
            .options(
                joinedload(Favorite.team),
                joinedload(Favorite.competition),
            )
            .where(
                Favorite.user_id == user_id,
            )
            .order_by(Favorite.id)
        )

        return list(
            self.db.scalars(statement).all()
        )