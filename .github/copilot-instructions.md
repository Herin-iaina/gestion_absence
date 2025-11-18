<!-- Instructions mises à jour pour les agents IA travaillant sur ce dépôt -->

# But et contexte (v2.0)

Ce dépôt contient une **application complète de gestion des congés** avec:
- **Backend FastAPI + PostgreSQL** avec authentification JWT et rôles
- **Frontend HTML5 + JS vanilla** avec 4 interfaces (login, employee, manager, admin)
- **API REST** conforme OpenAPI/Swagger
- **Gestion d'utilisateurs** (CRUD, import CSV)
- **Intégration optionnelle Google Calendar**

L'application remplace une version Flask antérieure (dossier `app.py` legacy à la racine).

## Structure principale

```
backend/
├── app/
│   ├── main.py          # Point d'entrée FastAPI
│   ├── core/
│   │   ├── config.py    # Settings + Role enum
│   │   ├── database.py  # SQLAlchemy + SessionLocal
│   │   └── security.py  # JWT + password hashing
│   ├── models/          # User, LeaveRequest, Team (SQLAlchemy ORM)
│   ├── schemas/         # Pydantic (UserCreate, LeaveRequestResponse, etc.)
│   ├── services/        # Business logic (AuthService, UserService, LeaveService)
│   └── routes/          # API endpoints (auth.py, users.py, leaves.py, deps.py)
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml

frontend/
├── index.html                  # Login (publique)
├── employee-dashboard.html     # Employé: demandes + calendrier équipe
├── manager-dashboard.html      # Manager: validation des demandes
└── admin-dashboard.html        # Admin: gestion users + overview
```

## Flux d'authentification

1. Utilisateur se connecte via `/api/auth/login` (POST username + password)
2. Backend retourne un **JWT token** (valide 30 min par défaut)
3. Frontend stocke le token dans `localStorage`
4. Chaque requête ajoute `Authorization: Bearer <token>`
5. Backend extrait le token et valide le user + rôle via `get_current_user()` et `require_role()`

## Rôles et permissions

| Rôle | Endpoints autorisés |
|------|---------------------|
| **admin** | `/api/users/*`, `/api/leaves/*/approve\|reject`, tout voir |
| **manager** | `/api/leaves/pending-approvals`, `/api/leaves/{id}/approve\|reject` |
| **employee** | `POST /api/leaves/`, `GET /api/leaves/my-requests`, `GET /api/leaves/team/calendar` |

## Points clés d'intégration

### Database
- PostgreSQL 14+ via SQLAlchemy ORM
- Migrations: utiliser `alembic upgrade head` (à implémenter)
- Modèles: `User` (hashed password, role, google tokens), `LeaveRequest` (dates, statut, approuver_by), `Team` (members M2M)

### Google Calendar (optionnel)
- Flux OAuth: routes `/api/auth/google` + `/api/auth/google/callback` (à implémenter)
- Tokens stockés dans `User.google_calendar_token` (JSON sérialisé)
- Création d'événement: via `LeaveService.create_calendar_event()` (inachevé)

### Import CSV
- Format: `username,email,full_name,role,password` (voir `README.md`)
- Endpoint: `POST /api/users/import/csv` (FormData file)
- Utilise `UserService.import_users_from_csv()`

### Credentials par défaut
- Admin créé au démarrage (username: `admin`, password: `admin123`)
- À changer en production via `.env`

## Workflows courants pour agents IA

### Ajouter un nouvel endpoint API
1. Créer la route dans `app/routes/<domain>.py`
2. Utiliser `get_current_user()` ou `require_role(Role.ADMIN)` pour auth
3. Valider les données avec Pydantic schemas
4. Appeler la logique dans `app/services/<domain>.py`
5. Retourner un modèle Pydantic (FastAPI le sérialise automatiquement)

### Modifier une permission utilisateur
1. Éditer `app/core/config.py` → classe `Role`
2. Appliquer les checks dans `app/routes/deps.py` → `require_role()`
3. Tester avec les 3 rôles

### Ajouter un champ au modèle User
1. Éditer `app/models/user.py` → ajouter colonne SQLAlchemy
2. Créer migration Alembic: `alembic revision --autogenerate -m "Add field"`
3. Mettre à jour `UserResponse` schema si exposé via API
4. Documenter dans `README.md`

## Commandes pratiques

```bash
# Backend local
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Docker (recommandé)
docker-compose up -d
# Logs: docker-compose logs -f api

# Tests
pytest --cov=app

# DB migrations (à implémenter)
alembic revision --autogenerate -m "Describe change"
alembic upgrade head
```

## Bonnes pratiques du projet

- **Monolithe volontaire**: tout dans `backend/` (pas de microservices pour l'instant)
- **Type hints obligatoires**: Pydantic schemas pour input/output
- **Dépendances FastAPI**: utiliser `Depends()` pour auth, DB, validation
- **Frontend minimal**: HTML5 + JS vanilla (pas de framework) pour simplicité
- **Logs**: ajouter `logger.info()` pour debug (Uvicorn logs sur stderr)
- **Secrets**: jamais commiter `.env`, utiliser `.env.example`
- **Transactions DB**: `db.commit()` après modification, `db.close()` en finally

## Checklist pour agent IA modifiant le code

- [ ] Lire `backend/README.md` pour l'architecture backend
- [ ] Lire `backend/app/core/config.py` pour comprendre Settings et Role
- [ ] Vérifier que les modèles SQLAlchemy dans `app/models/` existent
- [ ] Pour API: ajouter schemas Pydantic dans `app/schemas/` + routes dans `app/routes/`
- [ ] Pour services: implémenter logique dans `app/services/` + utiliser dans routes
- [ ] Tester avec `pytest` et vérifier `/docs` (Swagger)
- [ ] Ne pas refactorer massivement sans confirmation préalable
- [ ] Conserver les messages utilisateur en français
- [ ] Documenter les changements dans `README.md`

## Intégrations externes

- **Google Calendar API**: à configurer dans `.env` (GOOGLE_CLIENT_ID, etc.)
- **PostgreSQL**: URL dans `DATABASE_URL` (docker-compose fournit un container)
- **JWT secret**: `SECRET_KEY` en production = clé aléatoire forte

## Questions au mainteneur

- Faut-il implémenter les migrations Alembic maintenant ?
- Voulez-vous Google Calendar intégré ou modulaire (déployer sans) ?
- Frontend: rester en vanilla JS ou migrer vers React ?
- Tests: à quel level (unitaires, intégration, e2e) ?

---

**Version**: 2.0.0 (refactor FastAPI)  
**Dernière MAJ**: Novembre 2025
