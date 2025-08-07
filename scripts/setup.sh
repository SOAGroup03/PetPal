#!/bin/bash

# PetPal Setup Script
# This script sets up the PetPal application for local development

set -e

echo "🐾 Setting up PetPal Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# MongoDB Configuration
MONGODB_URI=mongodb+srv://acsujan69:petpal123@petpal.9k6d9qu.mongodb.net/
DATABASE_NAME=petpal

# JWT Configuration
JWT_SECRET=your_jwt_secret_key_here_change_this_in_production

# Service URLs (for development)
USER_SERVICE_URL=http://localhost:5001
PET_SERVICE_URL=http://localhost:5002
APPOINTMENT_SERVICE_URL=http://localhost:5003
MEDICAL_SERVICE_URL=http://localhost:5004

# Frontend Configuration
SECRET_KEY=your_secret_key_here_change_this_in_production
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build

echo "✅ Docker images built successfully"

# Start services
echo "🚀 Starting PetPal services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are healthy
check_service() {
    local service_name=$1
    local port=$2
    
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service_name is healthy"
    else
        echo "❌ $service_name is not responding"
        return 1
    fi
}

echo "🔍 Checking service health..."
check_service "User Service" 5001
check_service "Pet Service" 5002
check_service "Appointment Service" 5003
check_service "Medical Service" 5004

# Check if frontend is accessible
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 PetPal setup completed successfully!"
echo ""
echo "📋 Service URLs:"
echo "   Frontend:           http://localhost:3000"
echo "   User Service:       http://localhost:5001"
echo "   Pet Service:        http://localhost:5002"
echo "   Appointment Service: http://localhost:5003"
echo "   Medical Service:    http://localhost:5004"
echo "   Prometheus:         http://localhost:9090"
echo "   Grafana:           http://localhost:3001 (admin/admin)"
echo ""
echo "🔧 Useful commands:"
echo "   View logs:         docker-compose logs -f"
echo "   Stop services:     docker-compose down"
echo "   Restart services:  docker-compose restart"
echo "   Rebuild services:  docker-compose up --build"
echo ""
echo "📚 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Register a new account"
echo "   3. Start adding your pets!"
echo ""