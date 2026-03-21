from functools import lru_cache
import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Mystic API v2"
    app_description: str = "FastAPI modular bootstrap for the Sonora Digital monorepo"
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: list[str] = [origin for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
