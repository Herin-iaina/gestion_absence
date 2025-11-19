"""Modèle User"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.core.config import Role


class User(Base):
    """Modèle utilisateur"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Rôle et statut
    role = Column(SQLEnum(Role), default=Role.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Google Calendar integration
    google_calendar_token = Column(String(2048), nullable=True)  # JSON serialisé
    google_calendar_refresh_token = Column(String(1024), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # Demandes de congés de l'utilisateur (user_id)
    leave_requests = relationship(
        "LeaveRequest",
        back_populates="user",
        foreign_keys="LeaveRequest.user_id"
    )
    
    # Demandes approuvées par l'utilisateur (approved_by_id)
    approved_leaves = relationship(
        "LeaveRequest",
        back_populates="approved_by",
        foreign_keys="LeaveRequest.approved_by_id"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
