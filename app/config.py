from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # allow Docker Compose vars (POSTGRES_*) without rejection
    )

    DATABASE_URL: str

    # Auth — Module 2 (defaults allow the app to start before Module 2 is wired)
    SECRET_KEY: str = "change-me-before-module-2-goes-live"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ENVIRONMENT: str = "development"


settings = Settings()
