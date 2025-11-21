"""Schémas pour les demandes de congé"""
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
from app.models.leave_request import LeaveStatus, LeaveType


class LeaveRequestBase(BaseModel):
    """Schéma de base pour une demande de congé"""
    start_date: datetime
    end_date: datetime
    leave_type: LeaveType
    comment: Optional[str] = None

    @validator('end_date')
    def validate_dates(cls, v, values):
        """Valider que la date de fin est après la date de début"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("La date de fin doit être après la date de début")
        return v


class LeaveRequestCreate(LeaveRequestBase):
    """Schéma pour créer une demande de congé"""
    pass


class LeaveRequestUpdate(BaseModel):
    """Schéma pour mettre à jour une demande de congé"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    leave_type: Optional[LeaveType] = None
    comment: Optional[str] = None
    status: Optional[LeaveStatus] = None


class LeaveRequestResponse(LeaveRequestBase):
    """Schéma de réponse pour une demande de congé"""
    id: int
    user_id: int
    status: LeaveStatus
    rejection_reason: Optional[str] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    calendar_event_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Champs calculés
    number_of_days: int
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    approved_by_name: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True

    @staticmethod
    def from_orm(leave_request):
        """Créer une réponse à partir d'un objet ORM"""
        # Calculer le nombre de jours
        delta = leave_request.end_date - leave_request.start_date
        # Inclure le jour de début et de fin
        number_of_days = delta.days + 1
        
        # Exclure les weekends (optionnel, à adapter selon vos besoins)
        # Pour l'instant, on compte tous les jours
        
        data = {
            "id": leave_request.id,
            "user_id": leave_request.user_id,
            "start_date": leave_request.start_date,
            "end_date": leave_request.end_date,
            "leave_type": leave_request.leave_type,
            "status": leave_request.status,
            "comment": leave_request.comment,
            "rejection_reason": leave_request.rejection_reason,
            "approved_by_id": leave_request.approved_by_id,
            "approved_at": leave_request.approved_at,
            "calendar_event_id": leave_request.calendar_event_id,
            "created_at": leave_request.created_at,
            "updated_at": leave_request.updated_at,
            "number_of_days": number_of_days,
        }
        
        # Ajouter les informations de l'employé si disponibles
        if hasattr(leave_request, 'user') and leave_request.user:
            data["employee_name"] = leave_request.user.username
            data["employee_email"] = leave_request.user.email
        
        # Ajouter les informations de l'approbateur si disponibles
        if hasattr(leave_request, 'approved_by') and leave_request.approved_by:
            data["approved_by_name"] = leave_request.approved_by.username
        
        return LeaveRequestResponse(**data)