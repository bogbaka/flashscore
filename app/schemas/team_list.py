from pydantic import BaseModel

from app.schemas.team import TeamResponse


class TeamListResponse(BaseModel):
    page: int
    limit: int
    total: int
    teams: list[TeamResponse]