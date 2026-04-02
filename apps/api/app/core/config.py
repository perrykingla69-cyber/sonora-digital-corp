from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    DOMAIN: str = "sonoradigitalcorp.com"

    # DB
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str
    RATE_LIMIT_PER_MINUTE: int = 100

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Encryption (para datos sensibles en DB)
    ENCRYPTION_KEY: str

    # OpenRouter (acceso a Gemini, GLM, Claude, GPT, etc.)
    OPENROUTER_API_KEY: str
    # HERMES: orquestador — rápido y barato
    HERMES_MODEL: str = "google/gemini-2.0-flash-001"
    # MYSTIC: analista — mejor razonamiento
    MYSTIC_MODEL: str = "thudm/glm-z1-rumination:free"

    # Qdrant RAG
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""

    # Ollama (embeddings)
    OLLAMA_URL: str = "http://ollama:11434"

    # Evolution API
    EVOLUTION_URL: str = "http://evolution:8080"
    EVOLUTION_API_KEY: str

    # Seguridad
    ALLOWED_HOSTS: List[str] = ["sonoradigitalcorp.com", "www.sonoradigitalcorp.com", "localhost", "hermes-api", "127.0.0.1", "*"]
    CORS_ORIGINS: List[str] = ["https://sonoradigitalcorp.com"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
