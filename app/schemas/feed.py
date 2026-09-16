from datetime import datetime

from pydantic import BaseModel


class FeedTeamResponse(BaseModel):
    id: int
    name: str
    short_name: str | None = None
    logo_url: str | None = None


class FeedCompetitionResponse(BaseModel):
    id: int
    name: str
    country: str | None = None
    logo_url: str | None = None


class FeedMatchResponse(BaseModel):
    id: int
    kickoff_at: datetime
    status: str
    home_score: int
    away_score: int
    home_team: FeedTeamResponse
    away_team: FeedTeamResponse
    competition: FeedCompetitionResponse


class FeedResponse(BaseModel):
    live: list[FeedMatchResponse]
    today: list[FeedMatchResponse]
    upcoming: list[FeedMatchResponse]
    finished: list[FeedMatchResponse]