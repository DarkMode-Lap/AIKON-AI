from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AIKON AI"
    debug: bool = False
    gemini_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()
