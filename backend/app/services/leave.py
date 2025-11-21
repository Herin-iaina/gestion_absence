"""Service pour la gestion des congés"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.models.leave_request import LeaveRequest, LeaveStatus, LeaveType
from app.schemas.leave import LeaveRequestCreate, LeaveRequestUpdate


class LeaveService:
    """Service pour gérer les demandes de congé"""
    
    @staticmethod
    def create_leave_request(db: Session, user_id: int, leave_data: LeaveRequestCreate) -> LeaveRequest:
        """Créer une nouvelle demande de congé"""
        # Vérifier que les dates sont valides
        if leave_data.end_date < leave_data.start_date:
            raise ValueError("La date de fin doit être après la date de début")
        
        leave_request = LeaveRequest(
            user_id=user_id,
            start_date=leave_data.start_date,
            end_date=leave_data.end_date,
            leave_type=leave_data.leave_type,
            comment=leave_data.comment,
            status=LeaveStatus.PENDING
        )
        
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)
        
        # Charger les relations
        db.refresh(leave_request, ['user'])
        
        return leave_request
    
    @staticmethod
    def get_leave_request(db: Session, leave_id: int) -> Optional[LeaveRequest]:
        """Récupérer une demande de congé par ID"""
        return db.query(LeaveRequest).options(
            joinedload(LeaveRequest.user),
            joinedload(LeaveRequest.approved_by)
        ).filter(LeaveRequest.id == leave_id).first()
    
    @staticmethod
    def list_user_leaves(db: Session, user_id: int, year: Optional[int] = None) -> List[LeaveRequest]:
        """Lister les demandes de congé d'un utilisateur"""
        query = db.query(LeaveRequest).options(
            joinedload(LeaveRequest.user),
            joinedload(LeaveRequest.approved_by)
        ).filter(LeaveRequest.user_id == user_id)
        
        if year:
            query = query.filter(
                db.func.extract('year', LeaveRequest.start_date) == year
            )
        
        return query.order_by(LeaveRequest.start_date.desc()).all()
    
    @staticmethod
    def list_all_leaves(db: Session, status: Optional[str] = None, year: Optional[int] = None) -> List[LeaveRequest]:
        """Lister toutes les demandes de congé avec filtres"""
        query = db.query(LeaveRequest).options(
            joinedload(LeaveRequest.user),
            joinedload(LeaveRequest.approved_by)
        )
        
        if status:
            query = query.filter(LeaveRequest.status == status)
        
        if year:
            query = query.filter(
                db.func.extract('year', LeaveRequest.start_date) == year
            )
        
        return query.order_by(LeaveRequest.start_date.desc()).all()
    
    @staticmethod
    def list_pending_leaves(db: Session, manager_id: int) -> List[LeaveRequest]:
        """Lister les demandes en attente d'approbation"""
        return db.query(LeaveRequest).options(
            joinedload(LeaveRequest.user),
            joinedload(LeaveRequest.approved_by)
        ).filter(
            LeaveRequest.status == LeaveStatus.PENDING
        ).order_by(LeaveRequest.created_at.desc()).all()
    
    @staticmethod
    def list_team_leaves(db: Session, from_date: datetime, to_date: datetime) -> List[LeaveRequest]:
        """Lister les congés validés de l'équipe sur une période"""
        return db.query(LeaveRequest).options(
            joinedload(LeaveRequest.user),
            joinedload(LeaveRequest.approved_by)
        ).filter(
            LeaveRequest.status == LeaveStatus.APPROVED,
            LeaveRequest.start_date <= to_date,
            LeaveRequest.end_date >= from_date
        ).order_by(LeaveRequest.start_date).all()
    
    @staticmethod
    def update_leave_request(db: Session, leave_id: int, leave_data: LeaveRequestUpdate, user_id: int) -> LeaveRequest:
        """Mettre à jour une demande de congé"""
        leave_request = LeaveService.get_leave_request(db, leave_id)
        
        if not leave_request:
            raise ValueError("Demande de congé non trouvée")
        
        if leave_request.user_id != user_id:
            raise ValueError("Vous n'avez pas le droit de modifier cette demande")
        
        if leave_request.status != LeaveStatus.PENDING:
            raise ValueError("Impossible de modifier une demande déjà traitée")
        
        # Mettre à jour les champs
        update_data = leave_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(leave_request, field, value)
        
        leave_request.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(leave_request)
        
        return leave_request
    
    @staticmethod
    def approve_leave(db: Session, leave_id: int, approver_id: int) -> LeaveRequest:
        """Approuver une demande de congé"""
        leave_request = LeaveService.get_leave_request(db, leave_id)
        
        if not leave_request:
            raise ValueError("Demande de congé non trouvée")
        
        if leave_request.status != LeaveStatus.PENDING:
            raise ValueError("Cette demande a déjà été traitée")
        
        leave_request.status = LeaveStatus.APPROVED
        leave_request.approved_by_id = approver_id
        leave_request.approved_at = datetime.utcnow()
        leave_request.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(leave_request)
        
        return leave_request
    
    @staticmethod
    def reject_leave(db: Session, leave_id: int, reason: str, rejector_id: int) -> LeaveRequest:
        """Rejeter une demande de congé"""
        leave_request = LeaveService.get_leave_request(db, leave_id)
        
        if not leave_request:
            raise ValueError("Demande de congé non trouvée")
        
        if leave_request.status != LeaveStatus.PENDING:
            raise ValueError("Cette demande a déjà été traitée")
        
        leave_request.status = LeaveStatus.REJECTED
        leave_request.rejection_reason = reason
        leave_request.approved_by_id = rejector_id
        leave_request.approved_at = datetime.utcnow()
        leave_request.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(leave_request)
        
        return leave_request
    
    @staticmethod
    def get_statistics(db: Session) -> dict:
        """Obtenir les statistiques des congés"""
        pending_count = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.PENDING
        ).count()
        
        approved_count = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.APPROVED
        ).count()
        
        rejected_count = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.REJECTED
        ).count()
        
        return {
            "pending": pending_count,
            "approved": approved_count,
            "rejected": rejected_count,
            "total": pending_count + approved_count + rejected_count
        }