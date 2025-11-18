# 📝 INSTRUCTIONS POST-LIVRAISON

## Contenu de la livraison

### Backend (/backend)
```
✅ FastAPI application complete
✅ PostgreSQL models (User, LeaveRequest, Team)
✅ JWT authentication + Role-based access control
✅ Services (Auth, User, Leave)
✅ Routes (auth, users, leaves)
✅ Requirements.txt et configuration .env
✅ Docker + Docker Compose setup
✅ Dockerfile pour deployment
✅ README.md détaillé
```

### Frontend (/frontend)
```
✅ Login page (index.html)
✅ Employee dashboard
✅ Manager dashboard
✅ Admin dashboard
✅ Responsive CSS
✅ Vanilla JavaScript (no dependencies)
```

### Documentation
```
✅ README.md - Documentation générale
✅ QUICKSTART.md - Démarrage rapide
✅ MIGRATION.md - Guide Flask → FastAPI
✅ CHANGELOG.md - Résumé des changements
✅ .github/copilot-instructions.md - Instructions AI agents
✅ backend/README.md - Documentation API
✅ test_api.py - Script de test
✅ start.sh / stop.sh - Scripts helper
```

### Configuration
```
✅ .env.example - Template de configuration
✅ .gitignore - Exclusions Git
✅ example_users.csv - Exemple import
```

## ✅ Checklist avant usage

- [ ] **Dépendances installées**: `pip install -r requirements.txt` (dans backend/)
- [ ] **Base de données**: PostgreSQL 14+ running (ou Docker Compose)
- [ ] **.env créé**: Copier `.env.example` → `.env` et configurer
- [ ] **Admin créé**: Automatique au démarrage (admin/admin123)
- [ ] **Port 8000 libre**: API écoute sur localhost:8000
- [ ] **Port 5432 libre**: PostgreSQL (si Docker)

## 🚀 Démarrage rapide

```bash
# 1. Dans /backend
docker-compose up -d

# 2. Attendre ~30s pour que PostgreSQL démarre
docker-compose logs api

# 3. Tester l'API
python ../test_api.py

# 4. Servir le frontend (dans /frontend)
python -m http.server 3000

# 5. Ouvrir http://localhost:3000
```

Credentials: **admin** / **admin123**

## 📚 Documentation à lire en priorité

1. **README.md** (racine) - Vue d'ensemble du projet
2. **QUICKSTART.md** - Démarrage en 5 min
3. **backend/README.md** - API endpoints détaillés
4. **.github/copilot-instructions.md** - Conventions de code

## 🔧 Configuration importante

### .env
```env
DATABASE_URL=postgresql://user:password@localhost:5432/gestion_absence_db
SECRET_KEY=<changez cette clé en production>
GOOGLE_CLIENT_ID=<si vous utilisez Google Calendar>
DEBUG=False  # En production
```

### Secrets
- ❌ NE PAS commiter `.env`
- ❌ NE PAS commiter `credentials.json`
- ✅ Utiliser `.env.example` comme template

## 📝 Première utilisation

### 1. Login (Admin)
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin123`

### 2. Créer des utilisateurs
**Via interface Admin**:
- Aller sur Dashboard Admin
- Clicker "Créer un utilisateur"
- Remplir le formulaire

**Via import CSV**:
- Préparer un fichier (voir `example_users.csv`)
- Upload via "📤 Importer CSV"

### 3. Créer une demande de congé
- Se connecter en tant qu'employee
- Aller sur Employee Dashboard
- Remplir le formulaire "Demander un congé"
- Soumettre

### 4. Valider (Manager)
- Se connecter en tant que manager
- Aller sur Manager Dashboard
- Voir les demandes en attente
- Valider ou refuser

### 5. Voir le calendrier
- Employee Dashboard → Section "Congés validés de l'équipe"
- Affiche tous les congés approuvés

## 🐛 Dépannage

### "Connection refused" (8000 ou 5432)
```bash
# Vérifier que Docker est lancé
docker ps

# Relancer les services
docker-compose up -d

# Vérifier les logs
docker-compose logs api
```

### "Token invalide" au login
- Vérifier que `SECRET_KEY` dans `.env` est défini
- Redémarrer l'API: `docker-compose restart api`

### PostgreSQL ne démarre pas
```bash
# Vérifier les logs
docker-compose logs db

# Réinitialiser (attention: perte de données)
docker-compose down -v
docker-compose up -d
```

### CORS errors
- Vérifier que frontend et API sont sur les bons ports (3000 et 8000)
- CORS est activé dans `docker-compose.yml`

## 📊 API Endpoints clés

```bash
# Login
POST /api/auth/login
Body: {"username": "admin", "password": "admin123"}

# Créer utilisateur (Admin)
POST /api/users/
Headers: Authorization: Bearer <token>

# Importer CSV (Admin)
POST /api/users/import/csv
Headers: Authorization: Bearer <token>
Content-Type: multipart/form-data

# Créer demande (Employee)
POST /api/leaves/
Headers: Authorization: Bearer <token>

# Valider (Manager)
POST /api/leaves/{id}/approve
Headers: Authorization: Bearer <token>

# Documentation interactive
GET /docs
```

## 🧪 Tests

### Script automatisé
```bash
python test_api.py
```

### Tests manuels avec curl
```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Lister utilisateurs
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/users/
```

## 📦 Déploiement

### Production checklist
- [ ] Générer `SECRET_KEY` fort
- [ ] Configurer `DATABASE_URL` (RDS/managed DB)
- [ ] HTTPS configuré (Certbot/Cloudflare)
- [ ] CORS adapté (pas * en production)
- [ ] Google OAuth configuré si besoin
- [ ] Logs externalisés
- [ ] Backups DB automatiques
- [ ] Health checks + monitoring

### Déployer
```bash
# Via Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Ou manuellement
# 1. Installer Python 3.12+
# 2. pip install -r requirements.txt
# 3. gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
```

## 🎓 Évolutions recommandées

### Court terme (MVP+)
- [ ] Ajouter tests (pytest)
- [ ] Google Calendar sync
- [ ] Notifications email

### Moyen terme (v2.1)
- [ ] Frontend React
- [ ] Gestion d'équipes avancée
- [ ] Rapports/Analytics

### Long terme (v3.0)
- [ ] Mobile app
- [ ] SSO/SAML
- [ ] Multi-tenant

## 📞 Support

Pour questions ou bugs:
1. Consulter la documentation (README.md, .github/copilot-instructions.md)
2. Vérifier les logs: `docker-compose logs -f`
3. Tester l'API: `python test_api.py`
4. Créer une issue si bug confirmé

## 👨‍💻 Développement

Respecter les conventions dans `.github/copilot-instructions.md` pour toute modification.

Workflow de changement:
1. Créer une branche: `git checkout -b feature/nom`
2. Faire les modifications
3. Tester: `python test_api.py`
4. Commiter: `git commit -m "feat: description"`
5. Push et PR

## 📄 Licenses & Attributions

- FastAPI: BSD 3-Clause
- SQLAlchemy: MIT
- PostgreSQL: PostgreSQL License

## 📅 Dates clés

- **Version**: 2.0.0
- **Date**: Novembre 2025
- **Statut**: Beta - Prêt pour usage
- **Dernière MAJ**: [Aujourd'hui]

---

**Merci d'avoir utilisé Gestion des Congés!**

Pour toute question: Consulter la documentation ou créer une issue.

Bon développement! 🚀
