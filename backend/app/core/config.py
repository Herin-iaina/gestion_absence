"""Configuration centralisée de l'application"""
from pydantic_settings import BaseSettings
from enum import Enum


class Role(str, Enum):
    """Rôles disponibles dans l'application"""
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class Settings(BaseSettings):
    """Configuration globale via .env"""
    # Base de données
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/gestion_absence_db"
    
    # JWT
    SECRET_KEY: str = "changez_ceci_en_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Calendar OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    GOOGLE_APPLICATION_CREDENTIALS: str = "./credentials.json"
    
    # App
    DEBUG: bool = True
    APP_NAME: str = "Gestion des Congés"
    APP_VERSION: str = "2.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
