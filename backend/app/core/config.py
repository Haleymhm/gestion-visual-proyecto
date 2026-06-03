from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración global de la aplicación."""
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()
