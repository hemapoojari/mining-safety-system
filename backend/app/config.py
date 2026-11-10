"""
System Configuration & Environment Settings
Supports SQLite for rapid local prototyping and PostgreSQL for production migration.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI/ML Mining Safety & Evacuation System"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", 7860)))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database Configuration (Default: SQLite; Switch DATABASE_URL for PostgreSQL migration)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mining_safety.db")

    # Simulation Defaults
    SIMULATION_INTERVAL_SECONDS: float = float(os.getenv("SIMULATION_INTERVAL_SECONDS", 2.0))
    ENABLE_SYNTHETIC_GENERATOR: bool = os.getenv("ENABLE_SYNTHETIC_GENERATOR", "True").lower() == "true"

    # CORS Allowed Origins
    CORS_ORIGINS: list[str] = [
        "*",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:7860",
        "http://localhost:7860",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
