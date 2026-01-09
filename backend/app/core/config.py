"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/license_manager"
    
    # JWT Settings
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@license-manager.com"
    EMAIL_FROM_NAME: str = "License Manager"
    
    # Server Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # License Settings
    LICENSE_KEY_LENGTH: int = 32
    DEFAULT_CACHE_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
