from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.models.favorite import Favorite
from app.models.team import Team
from app.repositories.favorite import FavoriteRepository


class FavoriteService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = FavoriteRepository(db)

    def add_team(
        self,
        user_id: int,
        team_id: int,
    ) -> Favorite:
        team = self.db.get(Team, team_id)

        if team is None:
            raise ValueError("Team not found")

        existing = self.repository.get_team_favorite(
            user_id,
            team_id,
        )

        if existing is not None:
            raise ValueError("Team already favorited")

        favorite = Favorite(
            user_id=user_id,
            team_id=team_id,
        )

        return self.repository.add(favorite)

    def add_competition(
        self,
        user_id: int,
        competition_id: int,
    ) -> Favorite:
        competition = self.db.get(
            Competition,
            competition_id,
        )

        if competition is None:
            raise ValueError("Competition not found")

        existing = self.repository.get_competition_favorite(
            user_id,
            competition_id,
        )

        if existing is not None:
            raise ValueError(
                "Competition already favorited"
            )

        favorite = Favorite(
            user_id=user_id,
            competition_id=competition_id,
        )

        return self.repository.add(favorite)

    def remove_team(
        self,
        user_id: int,
        team_id: int,
    ) -> None:
        favorite = self.repository.get_team_favorite(
            user_id,
            team_id,
        )

        if favorite is None:
            raise ValueError("Team favorite not found")

        self.repository.delete(favorite)

    def remove_competition(
        self,
        user_id: int,
        competition_id: int,
    ) -> None:
        favorite = self.repository.get_competition_favorite(
            user_id,
            competition_id,
        )

        if favorite is None:
            raise ValueError(
                "Competition favorite not found"
            )

        self.repository.delete(favorite)

    def list_favorites(
        self,
        user_id: int,
    ) -> list[Favorite]:
        return self.repository.list_for_user(user_id)