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

    # OpenRouter (legacy — ya no se usa para HERMES/MYSTIC)
    OPENROUTER_API_KEY: str = ""
    # HERMES: orquestador — llama3 local via Ollama
    HERMES_MODEL: str = "llama3:latest"
    # MYSTIC: analista — mistral local via Ollama (razonamiento estructurado)
    MYSTIC_MODEL: str = "mistral:latest"

    # Qdrant RAG
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""

    # Ollama (embeddings)
    OLLAMA_URL: str = "http://ollama:11434"

    # Evolution API
    EVOLUTION_URL: str = "http://evolution:8080"
    EVOLUTION_API_KEY: str

    # Telegram (tokens por bot)
    TELEGRAM_TOKEN_CEO: str = ""
    TELEGRAM_TOKEN_HERMES: str = ""
    TELEGRAM_TOKEN_PUBLIC: str = ""
    TELEGRAM_TOKEN_MYSTIC: str = ""

    # HeyGen
    HEYGEN_API_KEY: str = ""
    HEYGEN_WEBHOOK_SECRET: str = ""

    # fal.ai
    FAL_API_KEY: str = ""
    FAL_WEBHOOK_SECRET: str = ""

    # MercadoPago
    MP_ACCESS_TOKEN: str = ""

    # Seguridad
    ALLOWED_HOSTS: List[str] = ["sonoradigitalcorp.com", "www.sonoradigitalcorp.com", "localhost", "hermes-api", "127.0.0.1", "*"]
    CORS_ORIGINS: List[str] = ["https://sonoradigitalcorp.com"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
