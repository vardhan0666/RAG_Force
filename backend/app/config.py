import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "RAGForge Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "SECRET_KEY_CHANGE_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "ragforge_user"
    POSTGRES_PASSWORD: str = "ragforge_password"
    POSTGRES_DB: str = "ragforge_db"
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: str | None = None

    # Redis & Qdrant
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "ragforge_chunks"

    # AI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str | None = None
    LLM_MODEL: str = "llama-3.1-8b-instant"
    EMBEDDING_MODEL: str = "mock-embedding"
    EMBEDDING_DIMENSION: int = 1536

    # Chunking & RAG
    DEFAULT_CHUNK_SIZE: int = 1000
    DEFAULT_CHUNK_OVERLAP: int = 200
    DEFAULT_TOP_K: int = 5
    UPLOAD_DIR: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
settings.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)