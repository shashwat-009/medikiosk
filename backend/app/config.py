from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    app_version: str
    database_url: str
    sarvam_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()