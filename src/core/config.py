from pydantic_settings import BaseSettings
from pydantic import SecretStr
from pathlib import Path

class Settings(BaseSettings):
    """
    Configuration class for the application.
    """
    APP_NAME: str
    APP_DESCRIPTION: str
    APP_VERSION: str
    
    # ----------------------------------------- APP Security -------------------------------------
    API_TOKEN: SecretStr
    
    # ----------------------------------------- APIs Tokens --------------------------------------
    HF_TOKEN: SecretStr
    GOOGLE_API_KEY: SecretStr
    GROK_API_KEY: SecretStr
    TAVILY_API_KEY: SecretStr
    
    # ----------------------------------------- DB Configurations ----------------------------------
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    DB_DRIVER: str
    
    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        extra = "forbid"

def get_settings():
    """
    Load the configuration settings from environment variables.
    """
    return Settings()