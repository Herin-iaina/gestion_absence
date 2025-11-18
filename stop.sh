#!/bin/bash
# Stop all services

echo "Arrêt des services..."
cd backend
docker-compose down

echo "✅ Services arrêtés"
