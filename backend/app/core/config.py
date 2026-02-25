import os
from pydantic import BaseModel


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_name: str = "Crisis Radar API"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./crisis_radar.db")
    cors_origins: list[str] = ["*"]
    skip_ingest_on_startup: bool = _as_bool(os.getenv("SKIP_INGEST_ON_STARTUP"), default=False)


settings = Settings()
