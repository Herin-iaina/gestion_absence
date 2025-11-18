"""Application FastAPI principale"""
from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.routes import auth, users, leaves
from app.services.user import UserService

# Créer les tables
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de gestion des demandes de congé"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Fonction de démarrage pour créer l'admin par défaut
@app.on_event("startup")
def startup_event():
    """Créer l'utilisateur admin par défaut au démarrage"""
    db = next(get_db())
    try:
        admin = UserService.create_default_admin(db)
        if admin:
            print(f"✓ Admin créé: {admin.username} / admin123")
    finally:
        db.close()


# Inclure les routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(leaves.router)


@app.get("/")
def read_root():
    """Racine de l'API"""
    return {"message": "Bienvenue sur l'API de gestion des congés"}


@app.get("/health")
def health_check():
    """Vérifier l'état de l'application"""
    return {"status": "ok"}


# Dépendance pour extraire le token du header Authorization
async def get_token_from_header(authorization: str = Header(None)) -> str:
    """Extraire le token Bearer du header Authorization"""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
