from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    host: str = "0.0.0.0"
    port: int = 8090
    log_level: str = "info"

    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_api_key: str = ""

    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    generation_provider: str = "openai"
    generation_model: str = "qwen/qwen-2.5-14b-instruct"
    generation_api_key: str = ""
    generation_base_url: str = "https://openrouter.ai/api/v1"
    generation_temperature: float = 0.2
    generation_max_tokens: int = 800
    generation_system_prompt: str = (
        "You are a support assistant. Answer strictly using provided context. "
        "If context is insufficient, say what is missing."
    )

    chunk_size: int = 1200
    chunk_overlap: int = 200
    max_url_chars: int = 200000

    service_api_key: str = ""


settings = Settings()
