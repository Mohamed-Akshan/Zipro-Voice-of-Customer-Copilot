
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    # Application
    APP_NAME: str = "Zipro Voice of Customer Copilot"
    APP_ENV: str = "development"
    DEBUG: bool = True
    FRONTEND_URL: str = "http://localhost:5173"

    # OpenAI for chat and agents
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-6-luna"

    # Existing LLM providers
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # Gemini embeddings
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768

    # PostgreSQL
    DATABASE_URL: str = ""

    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX: str = "zipro-feedback"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"

    # Cohere reranking
    COHERE_API_KEY: str = ""
    COHERE_MODEL: str = "rerank-v5.0-fast"

    # Langfuse
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Ingestion settings
    INGEST_BATCH_SIZE: int = 5
    INGEST_DELAY_SECONDS: int = 10
    INGEST_RETRIES: int = 3
    INGEST_RETRY_SECONDS: int = 65

    # Upload settings
    MAX_UPLOAD_MB: int = 8

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
