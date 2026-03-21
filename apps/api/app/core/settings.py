from functools import lru_cache
import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Mystic API v2"
    app_description: str = "FastAPI modular bootstrap for the Sonora Digital monorepo"
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: list[str] = [origin for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin]
    memory_data_dir: str = os.getenv("MEMORY_DATA_DIR", ".data")
    memory_backend: str = os.getenv("MEMORY_BACKEND", "json")
    memory_sqlalchemy_url: str | None = os.getenv("MEMORY_SQLALCHEMY_URL")
    memory_qdrant_url: str | None = os.getenv("MEMORY_QDRANT_URL")
    memory_qdrant_collection: str = os.getenv("MEMORY_QDRANT_COLLECTION", "mystic_memory")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
