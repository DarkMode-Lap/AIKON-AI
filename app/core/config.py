from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "AIKON AI"
    debug: bool = False
    gemini_api_key: str


settings = Settings()
