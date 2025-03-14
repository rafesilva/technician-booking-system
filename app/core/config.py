from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Technician Booking System"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        case_sensitive = True


settings = Settings()
