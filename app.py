"""
Application de gestion des congés
Fonctionnalités:
- Demande de congé par les utilisateurs
- Validation par les managers
- Création automatique d'événements Google Calendar
- API REST pour intégration avec Apps Script
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta
import json
import os
from google.oauth2.credentials import Credentials
import google.auth
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'  # Changez ceci en production

# Configuration Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = "credentials.json"  # Fichier à télécharger depuis Google Cloud Console

# Base de données simple (en production, utilisez SQLite, PostgreSQL, etc.)
# Structure: {id: {nom, email, date_debut, date_fin, statut, date_demande, valideur}}
conges_db = {}
next_id = 1

# Liste des managers (à adapter selon vos besoins)
MANAGERS = ['manager@example.com']

# ============= ROUTES PRINCIPALES =============

@app.route('/')
def index():
    """Page d'accueil avec calendrier des congés"""
    return render_template('index.html', conges=get_approved_leaves())

@app.route('/demande', methods=['GET', 'POST'])
def demande():
    """Page de demande de congé pour les utilisateurs"""
    if request.method == 'POST':
        return create_leave_request(request.form)
    return render_template('demande.html')

@app.route('/validation')
def validation():
    """Page de validation pour les managers"""
    pending_leaves = {k: v for k, v in conges_db.items() if v['statut'] == 'en_attente'}
    return render_template('validation.html', conges=pending_leaves)

@app.route('/api/valider/<int:leave_id>', methods=['POST'])
def valider_conge(leave_id):
    """Valider un congé et créer l'événement Calendar"""
    if leave_id not in conges_db:
        return jsonify({'error': 'Congé non trouvé'}), 404
    
    conges_db[leave_id]['statut'] = 'valide'
    conges_db[leave_id]['valideur'] = request.json.get('valideur', 'Manager')
    conges_db[leave_id]['date_validation'] = datetime.now().isoformat()
    
    # Créer l'événement Google Calendar
    try:
        event_id = create_calendar_event(conges_db[leave_id])
        conges_db[leave_id]['event_id'] = event_id
        return jsonify({
            'success': True, 
            'message': 'Congé validé et événement créé',
            'event_id': event_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Congé validé mais erreur Calendar: {str(e)}'
        })

@app.route('/api/refuser/<int:leave_id>', methods=['POST'])
def refuser_conge(leave_id):
    """Refuser un congé"""
    if leave_id not in conges_db:
        return jsonify({'error': 'Congé non trouvé'}), 404
    
    conges_db[leave_id]['statut'] = 'refuse'
    conges_db[leave_id]['motif_refus'] = request.json.get('motif', '')
    
    return jsonify({'success': True, 'message': 'Congé refusé'})

# ============= API REST (pour Apps Script) =============

@app.route('/api/conges', methods=['GET', 'POST'])
def api_conges():
    """
    GET: Liste tous les congés
    POST: Créer une nouvelle demande via API (depuis Apps Script mail)
    """
    if request.method == 'GET':
        return jsonify(list(conges_db.values()))
    
    if request.method == 'POST':
        data = request.json
        return create_leave_request(data, from_api=True)

@app.route('/api/conges/<int:leave_id>', methods=['GET', 'PUT', 'DELETE'])
def api_conge_detail(leave_id):
    """Opérations sur un congé spécifique"""
    if leave_id not in conges_db:
        return jsonify({'error': 'Congé non trouvé'}), 404
    
    if request.method == 'GET':
        return jsonify(conges_db[leave_id])
    
    if request.method == 'PUT':
        conges_db[leave_id].update(request.json)
        return jsonify({'success': True, 'data': conges_db[leave_id]})
    
    if request.method == 'DELETE':
        del conges_db[leave_id]
        return jsonify({'success': True, 'message': 'Congé supprimé'})

# ============= FONCTIONS HELPER =============

def create_leave_request(data, from_api=False):
    """Créer une demande de congé"""
    global next_id
    
    try:
        leave = {
            'id': next_id,
            'nom': data.get('nom'),
            'email': data.get('email'),
            'date_debut': data.get('date_debut'),
            'date_fin': data.get('date_fin'),
            'type': data.get('type', 'conge'),  # conge, maladie, etc.
            'commentaire': data.get('commentaire', ''),
            'statut': 'en_attente',
            'date_demande': datetime.now().isoformat()
        }
        
        conges_db[next_id] = leave
        next_id += 1
        
        if from_api:
            return jsonify({'success': True, 'id': leave['id'], 'data': leave})
        else:
            return redirect(url_for('confirmation', leave_id=leave['id']))
    
    except Exception as e:
        if from_api:
            return jsonify({'error': str(e)}), 400
        else:
            return f"Erreur: {str(e)}", 400

def get_approved_leaves():
    """Récupérer tous les congés validés"""
    return {k: v for k, v in conges_db.items() if v['statut'] == 'valide'}

def create_calendar_event(leave_data):
    """
    Créer un événement "Absent du bureau" dans Google Calendar
    Retourne l'ID de l'événement créé
    """
    try:
        # Charger les credentials (à adapter selon votre méthode d'auth)
        creds = get_calendar_credentials(leave_data['email'])
        service = build('calendar', 'v3', credentials=creds)
        
        # Préparer l'événement
        event = {
            'summary': f'Absent du bureau - {leave_data["nom"]}',
            'description': f'Congé validé\nType: {leave_data.get("type", "congé")}',
            'start': {
                'date': leave_data['date_debut'],
                'timeZone': 'Indian/Antananarivo',
            },
            'end': {
                'date': leave_data['date_fin'],
                'timeZone': 'Indian/Antananarivo',
            },
            'transparency': 'transparent',
            'eventType': 'outOfOffice',
        }
        
        # Créer l'événement
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event['id']
    
    except HttpError as error:
        print(f'Erreur API Calendar: {error}')
        raise

def get_calendar_credentials(email):
    """
    Récupérer les credentials pour un utilisateur
    À implémenter selon votre système d'authentification
    """
    # Tentative 1: utiliser les credentials stockés dans la session (après /auth/google)
    try:
        if 'credentials' in session:
            info = session['credentials']
            try:
                return Credentials.from_authorized_user_info(info, SCOPES)
            except Exception:
                # si conversion échoue, on continue vers le fallback
                pass

        # Tentative 2: Application Default Credentials (pour development avec
        # GOOGLE_APPLICATION_CREDENTIALS défini sur un JSON de service account)
        try:
            creds, _ = google.auth.default(scopes=SCOPES)
            return creds
        except Exception:
            pass

        # Aucun credentials disponible
        raise RuntimeError(
            'No Google credentials available. Run /auth/google to authenticate or set '
            'GOOGLE_APPLICATION_CREDENTIALS to a service account JSON for server-side calls.'
        )
    except Exception as e:
        # remonter l'exception au caller
        raise

@app.route('/confirmation/<int:leave_id>')
def confirmation(leave_id):
    """Page de confirmation après demande"""
    if leave_id not in conges_db:
        return "Demande non trouvée", 404
    return render_template('confirmation.html', conge=conges_db[leave_id])

# ============= AUTHENTIFICATION GOOGLE (optionnel) =============

@app.route('/auth/google')
def google_auth():
    """Initier le flux OAuth Google"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('google_callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/auth/google/callback')
def google_callback():
    """Callback OAuth Google"""
    state = session['state']
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('google_callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    # Sauvegarder les credentials dans la session ou DB
    session['credentials'] = credentials_to_dict(credentials)
    
    return redirect(url_for('index'))

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# ============= LANCEMENT DE L'APPLICATION =============

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)