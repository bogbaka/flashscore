from pydantic import BaseModel

from app.schemas.match import MatchResponse


class FeedResponse(BaseModel):
    live: list[MatchResponse]
    today: list[MatchResponse]
    upcoming: list[MatchResponse]
    finished: list[MatchResponse]