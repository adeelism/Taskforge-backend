from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Defaults to a local SQLite file so the app runs with no database setup.
    # Set DATABASE_URL to a Postgres URL in real environments. Never hardcode
    # credentials in source.
    database_url: str = "sqlite:///./taskforge.db"


settings = Settings()
