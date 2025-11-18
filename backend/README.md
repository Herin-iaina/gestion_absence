# API Gestion des Congés - FastAPI + PostgreSQL

Application moderne pour gérer les demandes de congé avec authentification, rôles utilisateur et intégration Google Calendar.

## Architecture

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Authentification**: JWT (JSON Web Tokens)
- **Base de données**: PostgreSQL (relations: User, LeaveRequest, Team)
- **Rôles**: Admin, Manager, Employee
- **Intégration**: Google Calendar API

## Démarrage rapide

### Avec Docker (recommandé)

```bash
# Démarrer PostgreSQL et l'API
docker-compose up -d

# L'API sera disponible sur http://localhost:8000
# Documentation interactive: http://localhost:8000/docs
```

### Localement (développement)

**Prérequis**: Python 3.12+, PostgreSQL 14+

```bash
# 1. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` sur Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Copier .env.example et configurer
cp .env.example .env
# Éditer .env avec vos paramètres (DATABASE_URL, SECRET_KEY, Google OAuth, etc.)

# 4. Créer les tables
alembic upgrade head  # optionnel si pas de migrations

# 5. Démarrer l'API
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Utilisation

### 1. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Réponse:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer",
#   "user_id": 1,
#   "username": "admin",
#   "role": "admin"
# }
```

### 2. Utiliser le token

Tous les endpoints (sauf `/api/auth/login`) nécessitent un header `Authorization`:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/leaves/my-requests
```

### 3. Endpoints principaux

#### Authentification
- `POST /api/auth/login` - Se connecter

#### Gestion des utilisateurs (Admin)
- `POST /api/users/` - Créer un utilisateur
- `GET /api/users/` - Lister tous les utilisateurs
- `GET /api/users/{user_id}` - Détails d'un utilisateur
- `PUT /api/users/{user_id}` - Modifier un utilisateur
- `DELETE /api/users/{user_id}` - Soft-delete un utilisateur
- `POST /api/users/import/csv` - Importer utilisateurs depuis CSV

#### Demandes de congé (Employee)
- `POST /api/leaves/` - Créer une demande
- `GET /api/leaves/my-requests` - Mes demandes
- `GET /api/leaves/{leave_id}` - Détails d'une demande
- `PUT /api/leaves/{leave_id}` - Modifier une demande (avant approbation)

#### Validation de congés (Manager/Admin)
- `POST /api/leaves/{leave_id}/approve` - Approuver
- `POST /api/leaves/{leave_id}/reject` - Rejeter (avec raison)
- `GET /api/leaves/pending-approvals` - Demandes en attente

#### Calendrier de l'équipe
- `GET /api/leaves/team/calendar` - Congés validés (par date)

## Format d'import CSV

Pour importer des utilisateurs, créez un fichier CSV avec les colonnes:

```csv
username,email,full_name,role,password
john_doe,john@example.com,John Doe,employee,password123
jane_smith,jane@example.com,Jane Smith,manager,password456
```

Téléchargez avec:

```bash
curl -X POST http://localhost:8000/api/users/import/csv \
  -H "Authorization: Bearer <token>" \
  -F "file=@users.csv"
```

## Configuration Google Calendar

1. Allez sur [Google Cloud Console](https://console.cloud.google.com)
2. Créez un projet et activez "Google Calendar API"
3. Créez un "OAuth 2.0 ID client" (type: Application Web)
4. Configurez dans `.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   ```

## Variables d'environnement

Voir `.env.example` pour la liste complète. Les variables principales:

```env
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/gestion_absence_db

# Sécurité JWT
SECRET_KEY=votre_cle_secrete_super_longue_et_aleatoire_change_en_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Mode debug
DEBUG=True
```

## Tests

```bash
# Installer pytest et dépendances test
pip install pytest pytest-asyncio httpx

# Lancer les tests
pytest

# Avec couverture
pytest --cov=app
```

## Structure du projet

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py      # Configuration (Role, Settings)
│   │   ├── database.py    # SQLAlchemy setup
│   │   └── security.py    # JWT, password hashing
│   ├── models/
│   │   ├── user.py        # User model
│   │   ├── leave_request.py  # LeaveRequest model
│   │   └── team.py        # Team model
│   ├── schemas/
│   │   ├── auth.py        # LoginRequest, TokenResponse
│   │   ├── user.py        # UserCreate, UserResponse
│   │   └── leave.py       # LeaveRequestCreate, LeaveRequestResponse
│   ├── services/
│   │   ├── auth.py        # Logique authentification
│   │   ├── user.py        # CRUD utilisateurs, import CSV
│   │   └── leave.py       # CRUD et validation congés
│   ├── routes/
│   │   ├── auth.py        # /api/auth/*
│   │   ├── users.py       # /api/users/*
│   │   ├── leaves.py      # /api/leaves/*
│   │   └── deps.py        # Dépendances (auth, roles)
│   └── main.py            # Application FastAPI
├── migrations/            # Alembic migrations (optionnel)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Évolutions futures

- [ ] Interface web frontend (React/Vue.js)
- [ ] Synchronisation Google Calendar automatique
- [ ] Notifications email
- [ ] Gestion d'équipes avancée
- [ ] Rapports et statistiques
- [ ] Tests unitaires et d'intégration complets
- [ ] Déploiement CI/CD (GitHub Actions)

## Support

Pour les questions ou bugs, créez une issue sur le dépôt ou consultez la documentation FastAPI:
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

**Version**: 2.0.0  
**Licence**: MIT
