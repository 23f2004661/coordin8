"""Core configuration settings for Coordin8."""

import os
from functools import lru_cache
from typing import Literal

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        app_env: Literal["development", "staging", "production"] = "development"
        api_host: str = "127.0.0.1"
        api_port: int = 8000
        secret_key: str = "default-insecure-secret-key-coordin8"

        # Database
        database_url: str = "sqlite:///./data/coordin8.db"

        # Qdrant Vector Store
        qdrant_url: str = "http://localhost:6333"
        qdrant_api_key: str | None = None
        qdrant_collection_prefix: str = "coordin8"

        # LLM (LM Studio / OpenAI compatible)
        llm_base_url: str = "http://127.0.0.1:1234/v1"
        llm_api_key: str = "not-needed-for-local"
        llm_model: str = "meta-llama-3.1-8b-instruct"
        llm_temperature: float = 0.1

        # Embeddings & Reranker
        embedding_provider: str = "local"
        embedding_model: str = "text-embedding-bge-m3"
        embedding_dimensions: int = 1024
        reranker_provider: str = "local"
        reranker_model: str = "bge-reranker-large"

        # Unlimited-OCR Microservice & Cloud Fallback
        ocr_base_url: str = "http://127.0.0.1:9001"
        ocr_provider: str = "unlimited_ocr"
        ocr_timeout_seconds: int = 60
        mistral_api_key: str | None = None
        mistral_ocr_model: str = "mistral-ocr-latest"
        mistral_ocr_base_url: str = "https://api.mistral.ai/v1"

        # Storage
        artifact_root: str = "./data"

        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "extra": "ignore",
        }

except ImportError:
    # Lightweight fallback when pydantic-settings is not yet installed
    class Settings:  # type: ignore[no-redef]
        def __init__(self) -> None:
            self.app_env: str = os.getenv("APP_ENV", "development")
            self.api_host: str = os.getenv("API_HOST", "127.0.0.1")
            self.api_port: int = int(os.getenv("API_PORT", "8000"))
            self.secret_key: str = os.getenv("SECRET_KEY", "default-insecure-secret-key-coordin8")
            self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/coordin8.db")
            self.qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
            self.qdrant_api_key: str | None = os.getenv("QDRANT_API_KEY")
            self.qdrant_collection_prefix: str = os.getenv("QDRANT_COLLECTION_PREFIX", "coordin8")
            self.llm_base_url: str = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
            self.llm_api_key: str = os.getenv("LLM_API_KEY", "not-needed-for-local")
            self.llm_model: str = os.getenv("LLM_MODEL", "meta-llama-3.1-8b-instruct")
            self.llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
            self.embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "local")
            self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
            self.embedding_dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "1024"))
            self.reranker_provider: str = os.getenv("RERANKER_PROVIDER", "local")
            self.reranker_model: str = os.getenv("RERANKER_MODEL", "bge-reranker-large")
            self.ocr_base_url: str = os.getenv("OCR_BASE_URL", "http://127.0.0.1:9001")
            self.ocr_provider: str = os.getenv("OCR_PROVIDER", "unlimited_ocr")
            self.ocr_timeout_seconds: int = int(os.getenv("OCR_TIMEOUT_SECONDS", "60"))
            self.mistral_api_key: str | None = os.getenv("MISTRAL_API_KEY")
            self.mistral_ocr_model: str = os.getenv("MISTRAL_OCR_MODEL", "mistral-ocr-latest")
            self.mistral_ocr_base_url: str = os.getenv("MISTRAL_OCR_BASE_URL", "https://api.mistral.ai/v1")
            self.artifact_root: str = os.getenv("ARTIFACT_ROOT", "./data")


@lru_cache
def get_settings() -> Settings:
    return Settings()
