from app.schemas.match import MatchResponse
from app.schemas.team import TeamResponse


class TeamDetailsResponse(TeamResponse):
    matches: list[MatchResponse]