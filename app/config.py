from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Football LiveScore API"
    app_env: str = "development"
    debug: bool = True

    football_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env.local",
        extra="ignore",
    )


settings = Settings()