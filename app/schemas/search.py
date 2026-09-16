from pydantic import BaseModel

from app.schemas.competition import CompetitionResponse
from app.schemas.team import TeamResponse


class SearchResponse(BaseModel):
    teams: list[TeamResponse]
    competitions: list[CompetitionResponse]