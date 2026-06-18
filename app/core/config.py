from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "AIKON AI"
    debug: bool = False
    gemini_api_key: str

    database_url: str = "sqlite+aiosqlite:///./aikon_ai.db"

    gemini_image_model: str = "gemini-2.5-flash-preview-05-20"
    gemini_prompt_version: str = "v1"

    s3_bucket: str = "aikon"
    s3_endpoint_url: str | None = None
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_region: str = "ap-northeast-2"


settings = Settings()
