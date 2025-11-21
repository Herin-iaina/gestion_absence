# QUICKSTART - Démarrage en 5 minutes

## 1. Prérequis

- Docker + Docker Compose installés
- Terminal ouvert dans `gestion_absence/`

## 2. Lancer l'application

```bash
# Rendre les scripts exécutables
chmod +x start.sh stop.sh

# Démarrer
./start.sh
```

Attendez ~30 secondes pour que PostgreSQL et l'API se lancent.

## 3. Accès

- **API**: http://localhost:8000
- **Documentation interactive**: http://localhost:8000/docs
- **Frontend login**: Servez `frontend/index.html` sur un serveur local (voir étape 5)

## 4. Credentials par défaut

```
Username: admin
Password: admin123
```

## 5. Servir le frontend

En parallèle, lancez un serveur local pour les fichiers frontend:

```bash
# Terminal 2
# cd frontend
python -m http.server 3000
```

Ouvrez http://localhost:3000 et connectez-vous avec admin/admin123.

## 6. Premiers pas

### Créer un utilisateur (manual)

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "role": "employee"
  }'
```

### Importer des utilisateurs (CSV)

```bash
curl -X POST http://localhost:8000/api/users/import/csv \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@example_users.csv"
```

### Créer une demande de congé

```bash
curl -X POST http://localhost:8000/api/leaves/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token_john>" \
  -d '{
    "start_date": "2025-12-01T00:00:00",
    "end_date": "2025-12-10T00:00:00",
    "leave_type": "conge_paye",
    "comment": "Vacances de Noël"
  }'
```

### Valider une demande (Manager)

```bash
curl -X POST http://localhost:8000/api/leaves/1/approve \
  -H "Authorization: Bearer <manager_token>"
```

## 7. Logs et debug

```bash
# Voir les logs
docker-compose -f backend/docker-compose.yml logs -f api

# Vérifier la BD
docker-compose -f backend/docker-compose.yml exec db psql -U user -d gestion_absence_db
```

## 8. Arrêter l'application

```bash
./stop.sh
```

## Prochaines étapes

- Voir `README.md` pour la documentation complète
- Consulter `backend/README.md` pour l'API détaillée
- Lire `.github/copilot-instructions.md` pour les conventions de code

---

Besoin d'aide ? Consultez les fichiers README ou créez une issue.
