from pydantic import BaseModel

from app.schemas.team import TeamResponse


class StandingResponse(BaseModel):
    id: int
    competition_id: int
    season_id: int
    team_id: int
    position: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int

    team: TeamResponse

    model_config = {
        "from_attributes": True,
    }