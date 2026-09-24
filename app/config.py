from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Football LiveScore API"
    app_env: str = "development"
    debug: bool = True

    football_api_key: str
    football_api_base_url: str = (
        "https://v3.football.api-sports.io"
    )
    football_api_timeout: float = 10.0

    football_current_season: int = 2026

    football_api_daily_limit: int = 100
    football_api_reserved_requests: int = 20

    jwt_secret_key: str = Field(
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env.local",
        extra="ignore",
    )


settings = Settings()


SUPPORTED_COMPETITIONS = {
    "premier-league": {
        "name": "Premier League",
        "provider_id": 39,
        "country": "England",
    },
    "la-liga": {
        "name": "La Liga",
        "provider_id": 140,
        "country": "Spain",
    },
    "serie-a": {
        "name": "Serie A",
        "provider_id": 135,
        "country": "Italy",
    },
    "bundesliga": {
        "name": "Bundesliga",
        "provider_id": 78,
        "country": "Germany",
    },
    "ligue-1": {
        "name": "Ligue 1",
        "provider_id": 61,
        "country": "France",
    },
    "champions-league": {
        "name": "UEFA Champions League",
        "provider_id": 2,
        "country": "World",
    },
    "europa-league": {
        "name": "UEFA Europa League",
        "provider_id": 3,
        "country": "World",
    },
    "afcon": {
        "name": "Africa Cup of Nations",
        "provider_id": 6,
        "country": "World",
    },
    "caf-champions-league": {
        "name": "CAF Champions League",
        "provider_id": 12,
        "country": "World",
    },
}