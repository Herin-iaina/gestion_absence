"""Configuration et session de base de données"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Créer le moteur de base de données
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """Dépendance FastAPI pour récupérer une session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
