from pydantic import BaseModel


class StandingResponse(BaseModel):
    id: int
    competition_id: int
    team_id: int
    position: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int

    model_config = {
        "from_attributes": True,
    }