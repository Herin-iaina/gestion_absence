"""Modèle LeaveRequest"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base


class LeaveStatus(str, Enum):
    """Statut d'une demande de congé"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveType(str, Enum):
    """Types de congés"""
    CONGE_PAYE = "conge_paye"
    MALADIE = "maladie"
    RTT = "rtt"
    CONGÉ_PARENTAL = "conge_parental"
    AUTRE = "autre"


class LeaveRequest(Base):
    """Modèle de demande de congé"""
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Dates
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    
    # Infos
    leave_type = Column(SQLEnum(LeaveType), default=LeaveType.CONGE_PAYE, nullable=False)
    status = Column(SQLEnum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False, index=True)
    
    comment = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Validation
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Google Calendar
    calendar_event_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="leave_requests")
    approved_by = relationship("User", foreign_keys=[approved_by_id], back_populates="approved_leaves")
    
    def __repr__(self):
        return f"<LeaveRequest(id={self.id}, user_id={self.user_id}, status={self.status})>"
