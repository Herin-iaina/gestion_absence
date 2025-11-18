#!/bin/bash
# Script de démarrage rapide du projet

set -e

echo "🚀 Démarrage de Gestion des Congés..."

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

echo "📦 Construction et démarrage des containers..."
docker-compose up -d

echo ""
echo "✅ Services démarrés!"
echo ""
echo "📍 URLs:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "👤 Credentials par défaut:"
echo "  - Username: admin"
echo "  - Password: admin123"
echo ""
echo "📋 Logs:"
echo "  docker-compose logs -f api"
echo ""
