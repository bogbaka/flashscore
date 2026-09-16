from app.schemas.standing import StandingResponse
from app.schemas.team import TeamResponse


class TeamDetailsResponse(TeamResponse):
    standing: StandingResponse | None = None