from app.schemas.competition import CompetitionResponse
from app.schemas.match import MatchResponse
from app.schemas.match_event import MatchEventResponse
from app.schemas.team import TeamResponse


class MatchDetailsResponse(MatchResponse):
    competition: CompetitionResponse
    home_team: TeamResponse
    away_team: TeamResponse
    events: list[MatchEventResponse]