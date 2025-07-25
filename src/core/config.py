from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """
    Configuration class for the application.
    """
    APP_NAME: str
    APP_DESCRIPTION: str
    APP_VERSION: str
    
    # ----------------------------------------- APP Security -------------------------------------
    ADMIN_SECRET_KEY: str
    
    # ----------------------------------------- APIs Tokens --------------------------------------
    HF_TOKEN: str
    GOOGLE_API_KEY: str
    GROK_API_KEY: str
    TAVILY_API_KEY: str
    
    # ----------------------------------------- DB Configurations ----------------------------------
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE_NAME: str
    DB_DRIVER: str
    
    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        extra = "forbid"

def get_settings():
    """
    Load the configuration settings from environment variables.
    """
    return Settings()