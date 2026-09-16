from sqlalchemy.orm import Session

from app.repositories.team import TeamRepository


class TeamService:
    def __init__(self, db: Session):
        self.repository = TeamRepository(db)

    def get_all_teams(self):
        return self.repository.get_all()

    def get_team(self, team_id: int):
        return self.repository.get_by_id(team_id)

    def get_team_details(self, team_id: int):
        team = self.repository.get_by_id(team_id)

        if team is None:
            return None

        return {
            "id": team.id,
            "name": team.name,
            "short_name": team.short_name,
            "logo_url": team.logo_url,
            "matches": self.repository.get_matches(team_id),
        }