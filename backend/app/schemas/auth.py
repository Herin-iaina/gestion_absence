"""Schémas Pydantic pour l'authentification"""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Demande de login"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Réponse avec token"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str
