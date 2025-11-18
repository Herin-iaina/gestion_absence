"""Schémas Pydantic pour LeaveRequest"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.leave_request import LeaveStatus, LeaveType


class LeaveRequestCreate(BaseModel):
    """Créer une demande de congé"""
    start_date: datetime
    end_date: datetime
    leave_type: LeaveType = LeaveType.CONGE_PAYE
    comment: Optional[str] = None


class LeaveRequestUpdate(BaseModel):
    """Mettre à jour une demande de congé"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    leave_type: Optional[LeaveType] = None
    comment: Optional[str] = None
    status: Optional[LeaveStatus] = None


class LeaveRequestResponse(BaseModel):
    """Réponse demande de congé"""
    id: int
    user_id: int
    start_date: datetime
    end_date: datetime
    leave_type: LeaveType
    status: LeaveStatus
    comment: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
