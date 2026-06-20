from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Transaction Processing Pipeline"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str
    redis_url: str

    celery_broker_url: str
    celery_result_backend: str

    gemini_api_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

