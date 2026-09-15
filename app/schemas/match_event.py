from pydantic import BaseModel


class MatchEventResponse(BaseModel):
    id: int
    minute: int | None = None
    event_type: str
    player_name: str | None = None
    team_id: int | None = None
    description: str | None = None

    model_config = {
        "from_attributes": True,
    }