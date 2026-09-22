from pydantic import BaseModel

from app.schemas.competition import CompetitionResponse
from app.schemas.team import TeamResponse


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    team_id: int | None = None
    competition_id: int | None = None

    team: TeamResponse | None = None
    competition: CompetitionResponse | None = None

    model_config = {
        "from_attributes": True,
    }