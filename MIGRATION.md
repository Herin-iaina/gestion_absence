# Migration Flask → FastAPI

Guide pour migrer du code existant vers la nouvelle architecture.

## Changements majeurs

| Aspect | Flask | FastAPI |
|--------|-------|---------|
| **Framework** | Flask | FastAPI (Starlette) |
| **ORM** | SQLAlchemy (même) | SQLAlchemy (même) |
| **Base de données** | En mémoire (`conges_db`) | PostgreSQL (persistant) |
| **Auth** | Session Flask | JWT tokens |
| **Rôles** | Hardcodés | Enum + middleware |
| **Frontend** | Jinja2 templates | HTML5 + JS vanilla |
| **Port** | 5009 | 8000 |

## Étapes de migration

### 1. Backup de l'ancienne version
```bash
mv app.py app.py.legacy
mv templates/ templates.legacy/
```

### 2. Déployer la nouvelle version
```bash
cd backend
docker-compose up -d
```

### 3. Exporter les données de la BD Flask
Si besoin de migrer les congés depuis `conges_db`:

```python
# Script de migration (à créer en backend/scripts/migrate_legacy.py)
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.leave_request import LeaveRequest, LeaveStatus
from app.models.user import User

# Charger le JSON ancien
with open('../app.py', 'r') as f:
    # Extraire conges_db du fichier (manuel ou via regex)
    pass

# Créer les records dans PostgreSQL
# ...
```

### 4. Créer les utilisateurs
```bash
# Via import CSV (voir backend/README.md)
# Ou créer manuellement via /api/users/
```

### 5. Configurer Google Calendar
```bash
# Copier credentials.json dans backend/
cp credentials.json backend/credentials.json

# Ou configurer via .env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### 6. Tester les workflows
- [ ] Login admin (admin/admin123)
- [ ] Créer un employee et manager
- [ ] Créer une demande de congé (employee)
- [ ] Valider (manager)
- [ ] Vérifier sur le calendrier

### 7. Déployer en production
```bash
# Copier docker-compose.yml + backend/ sur serveur
# Adapter .env pour production (SECRET_KEY fort, DB external, etc.)
# Lancer: docker-compose -f docker-compose.yml up -d
```

## Correspondances d'endpoints

| Ancien (Flask) | Nouveau (FastAPI) | Notes |
|---|---|---|
| `GET /` | `GET /` | Vue d'accueil → redirection login |
| `POST /demande` | `POST /api/leaves/` | Créer demande |
| `GET /validation` | `GET /api/leaves/pending-approvals` | Manager validation |
| `POST /api/valider/{id}` | `POST /api/leaves/{id}/approve` | Approuver |
| `POST /api/refuser/{id}` | `POST /api/leaves/{id}/reject` | Rejeter |
| `GET /api/conges` | `GET /api/leaves/` (voir note) | Liste congés |
| N/A | `POST /api/users/` | Créer user (nouveau) |
| N/A | `POST /api/users/import/csv` | Import CSV (nouveau) |

**Note**: L'API Flask retournait tous les congés. La nouvelle API filtre par permission (employee voit sien, manager voit équipe, admin voit tout).

## Points à vérifier

- [ ] **Timezones**: Ancien = `Indian/Antananarivo`, nouveau = UTC + option config
- [ ] **Emails**: L'ancienne app proposait notifications (non implémenté). À faire si besoin.
- [ ] **Apps Script Google**: L'exemple dans `readme.md` legacy fonctionne toujours (endpoint `/api/conges` existe) mais auth Bearer requise
- [ ] **CORS**: Frontend sur port 3000, API sur 8000 → CORS activé dans `docker-compose.yml`

## Support

Pour questions: consulter `backend/README.md` ou `.github/copilot-instructions.md`
