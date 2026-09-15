from pydantic import BaseModel


class CompetitionResponse(BaseModel):
    id: int
    name: str
    country: str | None = None
    logo_url: str | None = None

    model_config = {
        "from_attributes": True,
    }