from app.schemas.match import MatchResponse
from app.schemas.match_event import MatchEventResponse


class MatchDetailsResponse(MatchResponse):
    events: list[MatchEventResponse]