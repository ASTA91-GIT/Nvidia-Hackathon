import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "IncidentZero"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Nebius Token Factory & AI settings
    NEBIUS_API_KEY: Optional[str] = None
    NEBIUS_MODEL: str = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
    NEBIUS_API_BASE_URL: str = "https://api.tokenfactory.nebius.com/v1"
    AI_PROVIDER: str = "nebius"
    
    # Optional External Research (e.g. Tavily)
    TAVILY_API_KEY: Optional[str] = None
    
    # Server & DB settings
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    DATABASE_URL: str = "sqlite:///./incidentzero.db"
    
    # Test / Offline Mode toggle
    # When True or when AI_TEST_MODE is set, enables deterministic test agent execution
    TEST_MODE: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
