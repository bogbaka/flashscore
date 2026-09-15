from pydantic import BaseModel


class TeamResponse(BaseModel):
    id: int
    name: str
    short_name: str | None = None
    logo_url: str | None = None

    model_config = {
        "from_attributes": True,
    }