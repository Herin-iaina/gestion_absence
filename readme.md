mkdir gestion-conges
cd gestion-conges

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

gestion-conges/
├── app.py                  # Fichier principal (code Python fourni)
├── requirements.txt
├── credentials.json        # À télécharger depuis Google Cloud
├── .env                   # Variables d'environnement
└── templates/
    ├── base.html
    ├── index.html
    ├── demande.html
    ├── validation.html
    └── confirmation.html


🔐 Configuration Google Calendar API
1. Créer un projet Google Cloud

Allez sur https://console.cloud.google.com
Créez un nouveau projet
Activez l'API Google Calendar

2. Créer des credentials OAuth

Dans Google Cloud Console → APIs & Services → Credentials
Créez des identifiants → ID client OAuth 2.0
Type d'application : Application Web
URI de redirection autorisés : http://localhost:5000/auth/google/callback
Téléchargez le fichier JSON et renommez-le credentials.json
Placez-le dans le dossier racine du projet

Créez un fichier .env:
FLASK_SECRET_KEY=votre_cle_secrete_super_longue_et_aleatoire
FLASK_ENV=development
GOOGLE_CLIENT_ID=votre_client_id
GOOGLE_CLIENT_SECRET=votre_client_secret


# Activer l'environnement virtuel
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Lancer l'application
python app.py


L'application sera accessible sur : http://localhost:5000
📡 API REST pour Apps Script
Endpoints disponibles
1. Créer une demande de congé (depuis email)


POST /api/conges
Content-Type: application/json

{
  "nom": "Jean Dupont",
  "email": "jean@example.com",
  "date_debut": "2025-12-01",
  "date_fin": "2025-12-10",
  "type": "conge",
  "commentaire": "Vacances d'été"
}


Lister tous les congés
GET /api/conges

Détails d'un congé
GET /api/conges/1

Modifier un congé
PUT /api/conges/1
Content-Type: application/json

{
  "statut": "valide"
}

Supprimer un congé
DELETE /api/conges/1

Intégration avec Apps Script (Gmail)
Créez ce script dans Apps Script pour traiter les emails de demande de congé:
function traiterEmailsConges() {
  const threads = GmailApp.search('subject:"Demande de congé" is:unread');
  
  threads.forEach(thread => {
    const message = thread.getMessages()[0];
    const body = message.getPlainBody();
    
    // Parser l'email pour extraire les infos
    const nom = extraireInfo(body, 'Nom:');
    const dateDebut = extraireInfo(body, 'Du:');
    const dateFin = extraireInfo(body, 'Au:');
    
    // Envoyer à l'API
    const url = 'http://votre-serveur:5000/api/conges';
    const options = {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({
        nom: nom,
        email: message.getFrom(),
        date_debut: dateDebut,
        date_fin: dateFin,
        type: 'conge'
      })
    };
    
    UrlFetchApp.fetch(url, options);
    message.markRead();
  });
}

function extraireInfo(text, label) {
  const regex = new RegExp(label + '\\s*(.+)');
  const match = text.match(regex);
  return match ? match[1].trim() : '';
}


Utiliser une vraie base de données (Production)
Pour la production, remplacez le dictionnaire par SQLite:
import sqlite3

def init_db():
    conn = sqlite3.connect('conges.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conges
                 (id INTEGER PRIMARY KEY, 
                  nom TEXT, 
                  email TEXT, 
                  date_debut TEXT, 
                  date_fin TEXT, 
                  type TEXT,
                  statut TEXT,
                  event_id TEXT)''')
    conn.commit()
    conn.close()

Déploiement
Option 1: Heroku
# Créer un Procfile
echo "web: python app.py" > Procfile

# Déployer
heroku create
git push heroku main


Option 2: PythonAnywhere
Uploadez vos fichiers
Configurez l'application web
Ajoutez les variables d'environnement

Option 3: VPS (DigitalOcean, AWS, etc.)
# Installer gunicorn
pip install gunicorn

# Lancer avec gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app


🔒 Sécurité
À faire en production:

 Utiliser HTTPS
 Ajouter l'authentification utilisateur
 Valider toutes les entrées
 Limiter les requêtes API (rate limiting)
 Chiffrer les tokens dans la base de données
 Configurer CORS correctement
 Utiliser une vraie base de données (PostgreSQL)

📧 Notifications par email
Ajoutez ceci pour envoyer des emails:
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'votre-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'votre-mot-de-passe-app'

mail = Mail(app)

def envoyer_notification_validation(leave):
    msg = Message(
        'Congé validé',
        sender='noreply@company.com',
        recipients=[leave['email']]
    )
    msg.body = f"Bonjour {leave['nom']},\n\nVotre congé du {leave['date_debut']} au {leave['date_fin']} a été validé."
    mail.send(msg)

    Personnalisation
Vous pouvez personnaliser:

Les couleurs dans les CSS
Les types de congés
Les règles de validation
Les notifications
L'intégration avec d'autres outils (Slack, Teams, etc.)
