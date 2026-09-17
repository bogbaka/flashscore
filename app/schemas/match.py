from datetime import datetime

from pydantic import BaseModel

from app.schemas.competition import CompetitionResponse
from app.schemas.team import TeamResponse


class MatchResponse(BaseModel):
    id: int
    competition_id: int
    home_team_id: int
    away_team_id: int
    kickoff_at: datetime
    status: str
    home_score: int
    away_score: int

    competition: CompetitionResponse
    home_team: TeamResponse
    away_team: TeamResponse

    model_config = {
        "from_attributes": True,
    }


class MatchListResponse(BaseModel):
    page: int
    limit: int
    total: int
    matches: list[MatchResponse]
