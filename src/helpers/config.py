from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuration class for the application.
    """
    APP_NAME: str
    APP_DESCRIPTION: str
    APP_VERSION: str
    
    # APIs Tokens
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
        env_file = ".env"
        extra = "forbid"

def get_settings():
    """
    Load the configuration settings from environment variables.
    """
    return Settings()