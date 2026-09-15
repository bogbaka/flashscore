from datetime import datetime

from pydantic import BaseModel


class MatchResponse(BaseModel):
    id: int
    competition_id: int
    home_team_id: int
    away_team_id: int
    kickoff_at: datetime
    status: str
    home_score: int
    away_score: int

    model_config = {
        "from_attributes": True,
    }