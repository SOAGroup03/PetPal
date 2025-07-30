echo "🏠 Setting up PetPal for local development..."

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

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p microservices/user-service
mkdir -p microservices/pet-service
mkdir -p microservices/appointment-service
mkdir -p microservices/medical-service
mkdir -p frontend/templates
mkdir -p frontend/static/css
mkdir -p frontend/static/js
mkdir -p kubernetes
mkdir -p monitoring
mkdir -p scripts

# Create .env file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
MONGO_URI=mongodb+srv://acsujan69:petpal123@petpal.9k6d9qu.mongodb.net/petpal
SECRET_KEY=petpal-secret-key-2024
USER_SERVICE_URL=http://localhost:5001
PET_SERVICE_URL=http://localhost:5002
APPOINTMENT_SERVICE_URL=http://localhost:5003
MEDICAL_SERVICE_URL=http://localhost:5004
EOF

echo "✅ Local environment setup completed!"
echo "📝 Next steps:"
echo "1. Copy all service files into their respective directories"
echo "2. Run: docker-compose up --build"
echo "3. Access the application at http://localhost:5000"