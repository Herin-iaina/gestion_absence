"""Service d'authentification"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate


class AuthService:
    """Service pour la gestion de l'authentification"""
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Créer un nouvel utilisateur"""
        # Vérifier que l'utilisateur n'existe pas
        existing_user = db.query(User).filter(
            (User.username == user_create.username) | (User.email == user_create.email)
        ).first()
        
        if existing_user:
            raise ValueError("L'utilisateur existe déjà")
        
        # Créer l'utilisateur
        user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hash_password(user_create.password),
            full_name=user_create.full_name,
            role=user_create.role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User:
        """Authentifier un utilisateur"""
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Identifiants invalides")
        
        if not user.is_active:
            raise ValueError("Utilisateur désactivé")
        
        return user
    
    @staticmethod
    def create_access_token(user: User) -> str:
        """Créer un token d'accès pour un utilisateur"""
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        }
        return create_access_token(token_data)
