from sqlalchemy.orm import Session

from app.repositories.team import TeamRepository


class TeamService:
    def __init__(self, db: Session):
        self.repository = TeamRepository(db)

    def get_all_teams(
        self,
        page: int = 1,
        limit: int = 20,
    ):
        return self.repository.get_all(
            page=page,
            limit=limit,
        )

    def get_team(
        self,
        team_id: int,
    ):
        return self.repository.get_by_id(team_id)

    def get_team_matches(
        self,
        team_id: int,
        page: int = 1,
        limit: int = 20,
    ):
        return self.repository.get_matches(
            team_id=team_id,
            page=page,
            limit=limit,
        )

    def get_team_standing(
        self,
        team_id: int,
        competition_id: int,
        season_id: int,
    ):
        return self.repository.get_standing(
            team_id=team_id,
            competition_id=competition_id,
            season_id=season_id,
        )