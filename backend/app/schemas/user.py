"""Schémas Pydantic pour User"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.core.config import Role


class UserCreate(BaseModel):
    """Créer un utilisateur"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Role = Role.EMPLOYEE


class UserUpdate(BaseModel):
    """Mettre à jour un utilisateur"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Réponse utilisateur"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: Role
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
