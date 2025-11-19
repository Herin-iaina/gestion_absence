"""Service de gestion des demandes de congé"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from app.models.leave_request import LeaveRequest, LeaveStatus
from app.models.user import User
from app.schemas.leave import LeaveRequestCreate, LeaveRequestUpdate
from app.core.config import Role


class LeaveService:
    """Service pour la gestion des demandes de congé"""
    
    @staticmethod
    def create_leave_request(db: Session, user_id: int, leave_create: LeaveRequestCreate) -> LeaveRequest:
        """Créer une nouvelle demande de congé"""
        # Vérifier que l'utilisateur existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Utilisateur non trouvé")
        
        # Vérifier que start_date < end_date
        if leave_create.start_date >= leave_create.end_date:
            raise ValueError("La date de fin doit être après la date de début")
        
        # Créer la demande
        leave_request = LeaveRequest(
            user_id=user_id,
            start_date=leave_create.start_date,
            end_date=leave_create.end_date,
            leave_type=leave_create.leave_type,
            comment=leave_create.comment,
            status=LeaveStatus.PENDING
        )
        
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)
        return leave_request
    
    @staticmethod
    def get_leave_request(db: Session, leave_id: int) -> Optional[LeaveRequest]:
        """Récupérer une demande de congé par ID"""
        return db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    
    @staticmethod
    def list_user_leaves(db: Session, user_id: int, status: Optional[LeaveStatus] = None) -> List[LeaveRequest]:
        """Lister les congés d'un utilisateur"""
        query = db.query(LeaveRequest).filter(LeaveRequest.user_id == user_id)
        
        if status:
            query = query.filter(LeaveRequest.status == status)
        
        return query.order_by(LeaveRequest.start_date.desc()).all()
    
    @staticmethod
    def list_pending_leaves(db: Session, manager_id: int) -> List[LeaveRequest]:
        """Lister les congés en attente pour validation par un manager"""
        # Un manager voit les demandes de ses équipiers
        # Pour simplifier: les managers voient toutes les demandes en attente
        # (adapter selon votre logique d'équipes)
        return db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.PENDING
        ).order_by(LeaveRequest.created_at.desc()).all()
    
    @staticmethod
    def list_all_leaves(db: Session, status_filter: str = None) -> List[LeaveRequest]:
        """Lister tous les congés avec filtre optionnel sur le statut"""
        query = db.query(LeaveRequest)
        
        if status_filter:
            # Parse status filter (peut être "approved,rejected,cancelled" ou "approved")
            statuses = [s.strip().upper() for s in status_filter.split(',')]
            status_enums = [LeaveStatus[s] for s in statuses if s in LeaveStatus.__members__]
            if status_enums:
                query = query.filter(LeaveRequest.status.in_(status_enums))
        
        return query.order_by(LeaveRequest.created_at.desc()).all()
    
    @staticmethod
    def list_team_leaves(db: Session, from_date: datetime, to_date: datetime) -> List[LeaveRequest]:
        """Lister tous les congés validés dans une plage de dates"""
        return db.query(LeaveRequest).filter(
            and_(
                LeaveRequest.status == LeaveStatus.APPROVED,
                LeaveRequest.start_date <= to_date,
                LeaveRequest.end_date >= from_date
            )
        ).order_by(LeaveRequest.start_date).all()
    
    @staticmethod
    def approve_leave(db: Session, leave_id: int, approved_by_id: int) -> LeaveRequest:
        """Approuver une demande de congé"""
        leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
        
        if not leave_request:
            raise ValueError("Demande de congé non trouvée")
        
        if leave_request.status != LeaveStatus.PENDING:
            raise ValueError("Seules les demandes en attente peuvent être approuvées")
        
        leave_request.status = LeaveStatus.APPROVED
        leave_request.approved_by_id = approved_by_id
        leave_request.approved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(leave_request)
        return leave_request
    
    @staticmethod
    def reject_leave(db: Session, leave_id: int, reason: str, approved_by_id: int) -> LeaveRequest:
        """Rejeter une demande de congé"""
        leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
        
        if not leave_request:
            raise ValueError("Demande de congé non trouvée")
        
        if leave_request.status != LeaveStatus.PENDING:
            raise ValueError("Seules les demandes en attente peuvent être rejetées")
        
        leave_request.status = LeaveStatus.REJECTED
        leave_request.rejection_reason = reason
        leave_request.approved_by_id = approved_by_id
        leave_request.approved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(leave_request)
        return leave_request
    
    @staticmethod
    def update_leave_request(db: Session, leave_id: int, leave_update: LeaveRequestUpdate, user_id: int) -> LeaveRequest:
        """Mettre à jour une demande de congé (avant approbation)"""
        leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
        
        if not leave_request:
            raise ValueError("Demande de congé non trouvée")
        
        # Vérifier que c'est le propriétaire ou un admin
        if leave_request.user_id != user_id:
            raise ValueError("Vous ne pouvez modifier que vos propres demandes")
        
        if leave_request.status != LeaveStatus.PENDING:
            raise ValueError("Vous ne pouvez modifier que les demandes en attente")
        
        if leave_update.start_date:
            leave_request.start_date = leave_update.start_date
        
        if leave_update.end_date:
            leave_request.end_date = leave_update.end_date
        
        if leave_update.leave_type:
            leave_request.leave_type = leave_update.leave_type
        
        if leave_update.comment is not None:
            leave_request.comment = leave_update.comment
        
        db.commit()
        db.refresh(leave_request)
        return leave_request
