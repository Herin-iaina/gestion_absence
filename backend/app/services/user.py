"""Service de gestion des utilisateurs"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import csv
from io import StringIO
from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import Role


class UserService:
    """Service pour la gestion des utilisateurs"""
    
    @staticmethod
    def list_users(db: Session, role: Optional[Role] = None, is_active: Optional[bool] = None) -> List[User]:
        """Lister les utilisateurs avec filtres"""
        query = db.query(User).filter(User.is_deleted == False)
        
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.all()
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Récupérer un utilisateur par ID"""
        return db.query(User).filter(
            and_(User.id == user_id, User.is_deleted == False)
        ).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """Mettre à jour un utilisateur"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("Utilisateur non trouvé")
        
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        
        if user_update.email is not None:
            user.email = user_update.email
        
        if user_update.role is not None:
            user.role = user_update.role
        
        if user_update.is_active is not None:
            user.is_active = user_update.is_active
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> None:
        """Soft-delete un utilisateur"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("Utilisateur non trouvé")
        
        user.is_deleted = True
        db.commit()
    
    @staticmethod
    def import_users_from_csv(db: Session, csv_content: str) -> tuple[int, List[str]]:
        """Importer des utilisateurs depuis un CSV"""
        csv_reader = csv.DictReader(StringIO(csv_content))
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # start=2 car ligne 1 = headers
            try:
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                full_name = row.get('full_name', '').strip()
                role = row.get('role', 'employee').strip().lower()
                password = row.get('password', '').strip()
                
                # Validation
                if not username or not email or not password:
                    errors.append(f"Ligne {row_num}: username, email et password sont requis")
                    continue
                
                # Vérifier que l'utilisateur n'existe pas
                existing = db.query(User).filter(
                    or_(User.username == username, User.email == email)
                ).first()
                
                if existing:
                    errors.append(f"Ligne {row_num}: utilisateur '{username}' ou email '{email}' existe déjà")
                    continue
                
                # Créer l'utilisateur
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hash_password(password),
                    full_name=full_name or None,
                    role=Role(role) if role in [r.value for r in Role] else Role.EMPLOYEE
                )
                
                db.add(user)
                created_count += 1
            
            except Exception as e:
                errors.append(f"Ligne {row_num}: {str(e)}")
        
        db.commit()
        return created_count, errors
    
    @staticmethod
    def create_default_admin(db: Session, username: str = "admin", email: str = "admin@example.com", password: str = "admin123") -> Optional[User]:
        """Créer un utilisateur admin par défaut (s'il n'existe pas)"""
        existing_admin = db.query(User).filter(User.role == Role.ADMIN).first()
        
        if existing_admin:
            return None
        
        admin = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            full_name="Administrateur",
            role=Role.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
