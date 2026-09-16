from pydantic import BaseModel


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    team_id: int | None = None
    competition_id: int | None = None