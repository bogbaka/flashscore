from app.schemas.competition import CompetitionResponse
from app.schemas.match import MatchResponse
from app.schemas.standing import StandingResponse


class CompetitionDetailsResponse(CompetitionResponse):
    matches: list[MatchResponse]
    standings: list[StandingResponse]