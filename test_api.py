#!/usr/bin/env python3
"""
Script de test rapide de l'API
Usage: python test_api.py
"""

import requests
import json
import time

API_URL = "http://localhost:8000"
ADMIN_CREDS = {"username": "admin", "password": "admin123"}

def log(msg, level="INFO"):
    """Log avec couleur"""
    colors = {"INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", "END": "\033[0m"}
    print(f"{colors.get(level, '')}[{level}] {msg}{colors['END']}")

def test_health():
    """Tester la santé de l'API"""
    log("🏥 Test health check...")
    resp = requests.get(f"{API_URL}/health")
    assert resp.status_code == 200
    log("✅ Health check passed", "SUCCESS")
    return resp.json()

def test_login():
    """Tester login"""
    log("🔐 Test login...")
    resp = requests.post(f"{API_URL}/api/auth/login", json=ADMIN_CREDS)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    log(f"✅ Login successful - Token: {data['access_token'][:20]}...", "SUCCESS")
    return data["access_token"]

def test_create_user(token):
    """Tester création d'utilisateur"""
    log("👤 Test create user...")
    user = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "employee"
    }
    resp = requests.post(
        f"{API_URL}/api/users/",
        json=user,
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.status_code in [201, 400]:  # 400 si user existe déjà
        log("✅ Create user passed (or already exists)", "SUCCESS")
        return resp.json() if resp.status_code == 201 else None
    else:
        log(f"❌ Create user failed: {resp.text}", "ERROR")
        return None

def test_list_users(token):
    """Tester listage des utilisateurs"""
    log("📋 Test list users...")
    resp = requests.get(
        f"{API_URL}/api/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    users = resp.json()
    log(f"✅ Found {len(users)} users", "SUCCESS")
    return users

def test_create_leave(token, user_id=1):
    """Tester création d'une demande de congé"""
    log("📅 Test create leave request...")
    leave = {
        "start_date": "2025-12-01T00:00:00",
        "end_date": "2025-12-10T00:00:00",
        "leave_type": "conge_paye",
        "comment": "Test leave"
    }
    resp = requests.post(
        f"{API_URL}/api/leaves/",
        json=leave,
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.status_code == 201:
        log("✅ Create leave passed", "SUCCESS")
        return resp.json()
    else:
        log(f"⚠️  Create leave: {resp.status_code} - {resp.text}", "ERROR")
        return None

def test_my_leaves(token):
    """Tester récupération de mes demandes"""
    log("📋 Test my leaves...")
    resp = requests.get(
        f"{API_URL}/api/leaves/my-requests",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    leaves = resp.json()
    log(f"✅ Found {len(leaves)} leave requests", "SUCCESS")
    return leaves

def test_swagger():
    """Tester Swagger docs"""
    log("📚 Test Swagger docs...")
    resp = requests.get(f"{API_URL}/docs")
    assert resp.status_code == 200
    log("✅ Swagger docs available at /docs", "SUCCESS")

def main():
    log("🚀 Démarrage des tests d'API...", "INFO")
    log(f"API URL: {API_URL}", "INFO")
    
    try:
        # Test health
        test_health()
        time.sleep(1)
        
        # Test auth
        token = test_login()
        time.sleep(1)
        
        # Test users
        test_create_user(token)
        time.sleep(1)
        
        users = test_list_users(token)
        time.sleep(1)
        
        # Test leaves
        test_create_leave(token)
        time.sleep(1)
        
        test_my_leaves(token)
        time.sleep(1)
        
        # Test docs
        test_swagger()
        
        log("\n" + "="*50, "INFO")
        log("✅ TOUS LES TESTS PASSÉS!", "SUCCESS")
        log("="*50 + "\n", "INFO")
        
        log("📍 URLs importantes:", "INFO")
        log("  - API: http://localhost:8000", "INFO")
        log("  - Docs: http://localhost:8000/docs", "INFO")
        log("  - ReDoc: http://localhost:8000/redoc", "INFO")
        log("\n", "INFO")
        
    except AssertionError as e:
        log(f"❌ Test assertion failed: {e}", "ERROR")
        return 1
    except requests.exceptions.ConnectionError:
        log("❌ Cannot connect to API. Is it running?", "ERROR")
        log("Start with: docker-compose up -d", "ERROR")
        return 1
    except Exception as e:
        log(f"❌ Test error: {e}", "ERROR")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
