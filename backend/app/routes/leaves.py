"""Routes pour la gestion des demandes de congé"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.config import Role
from app.models.user import User
from app.schemas.leave import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse
from app.services.leave import LeaveService
from app.routes.deps import require_role, get_current_user

router = APIRouter(prefix="/api/leaves", tags=["leaves"])


@router.post("/", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def create_leave_request(
    leave_create: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle demande de congé"""
    try:
        leave_request = LeaveService.create_leave_request(db, current_user.id, leave_create)
        return LeaveRequestResponse.from_orm(leave_request)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[LeaveRequestResponse])
@router.get("", response_model=List[LeaveRequestResponse], include_in_schema=False)
def list_all_leaves(
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    year: Optional[int] = Query(None, description="Filtrer par année"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister tous les congés avec filtres optionnels (admin/manager)"""
    # Seuls admin et manager peuvent voir tous les congés
    if current_user.role not in [Role.MANAGER, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )
    
    leaves = LeaveService.list_all_leaves(db, status, year)
    return [LeaveRequestResponse.from_orm(l) for l in leaves]


@router.get("/my-requests", response_model=List[LeaveRequestResponse])
def get_my_leaves(
    year: Optional[int] = Query(None, description="Filtrer par année"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer toutes mes demandes de congé"""
    leaves = LeaveService.list_user_leaves(db, current_user.id, year)
    return [LeaveRequestResponse.from_orm(l) for l in leaves]


@router.get("/pending-approvals")
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MANAGER, Role.ADMIN))
):
    """Récupérer les demandes en attente d'approbation (manager/admin)"""
    leaves = LeaveService.list_pending_leaves(db, current_user.id)
    return [LeaveRequestResponse.from_orm(l) for l in leaves]


@router.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MANAGER, Role.ADMIN))
):
    """Obtenir les statistiques des congés"""
    return LeaveService.get_statistics(db)


@router.get("/team/calendar")
def get_team_calendar(
    from_date: Optional[datetime] = Query(None, description="Date de début"),
    to_date: Optional[datetime] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer le calendrier de l'équipe (congés validés)"""
    if not from_date:
        from_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    
    if not to_date:
        # Dernier jour du mois actuel
        next_month = from_date.replace(day=28) + timedelta(days=4)
        to_date = (next_month - timedelta(days=next_month.day)).replace(hour=23, minute=59, second=59)
    
    leaves = LeaveService.list_team_leaves(db, from_date, to_date)
    
    # Grouper par utilisateur
    by_user = {}
    for leave in leaves:
        user_id = leave.user_id
        if user_id not in by_user:
            by_user[user_id] = {
                "user_id": user_id,
                "username": leave.user.username if leave.user else "Unknown",
                "email": leave.user.email if leave.user else "",
                "leaves": []
            }
        by_user[user_id]["leaves"].append(LeaveRequestResponse.from_orm(leave))
    
    return list(by_user.values())


@router.get("/{leave_id}", response_model=LeaveRequestResponse)
def get_leave_request(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les détails d'une demande de congé"""
    leave_request = LeaveService.get_leave_request(db, leave_id)
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de congé non trouvée"
        )
    
    # Vérifier qu'on a le droit de voir cette demande
    if current_user.id != leave_request.user_id and current_user.role not in [Role.MANAGER, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )
    
    return LeaveRequestResponse.from_orm(leave_request)


@router.put("/{leave_id}", response_model=LeaveRequestResponse)
def update_leave_request(
    leave_id: int,
    leave_update: LeaveRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour une demande de congé"""
    try:
        leave_request = LeaveService.update_leave_request(db, leave_id, leave_update, current_user.id)
        return LeaveRequestResponse.from_orm(leave_request)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{leave_id}/approve", response_model=LeaveRequestResponse)
def approve_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MANAGER, Role.ADMIN))
):
    """Approuver une demande de congé (manager/admin)"""
    try:
        leave_request = LeaveService.approve_leave(db, leave_id, current_user.id)
        return LeaveRequestResponse.from_orm(leave_request)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{leave_id}/reject")
def reject_leave(
    leave_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.MANAGER, Role.ADMIN))
):
    """Rejeter une demande de congé (manager/admin)"""
    try:
        leave_request = LeaveService.reject_leave(db, leave_id, reason, current_user.id)
        return LeaveRequestResponse.from_orm(leave_request)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )