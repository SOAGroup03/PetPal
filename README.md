# 🐾 PetPal - Pet Care Management System

A comprehensive microservices-based pet care management system built with Python Flask, MongoDB, and modern DevOps practices.

## ✨ Features

- **User Management**: Registration, authentication, and profile management
- **Pet Profiles**: Complete pet information with CRUD operations
- **Appointment Scheduling**: Veterinary appointment management
- **Medical Records**: Comprehensive medical history tracking
- **Microservices Architecture**: Four independent services
- **Modern UI**: Bootstrap-based responsive frontend
- **Monitoring**: Prometheus and Grafana integration
- **Containerization**: Docker and Kubernetes ready
- **CI/CD Pipeline**: Automated testing and deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Load Balancer  │    │   Monitoring    │
│   (Flask)       │    │                 │    │ (Prometheus/    │
│   Port: 3000    │    │                 │    │  Grafana)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Service   │    │  Pet Service    │    │Appointment Svc  │
│  Port: 5001     │    │  Port: 5002     │    │  Port: 5003     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Medical Service │
                    │  Port: 5004     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  MongoDB Atlas  │
                    │   (Database)    │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- MongoDB Atlas account
- Kubernetes cluster (for K8s deployment)

### Local Development with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PetPal
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001 (admin/admin)

### Manual Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes Deployment

1. **Build and push images** (optional)
   ```bash
   # Build images for each service
   docker build -t petpal/user-service ./services/user-service
   docker build -t petpal/pet-service ./services/pet-service
   docker build -t petpal/appointment-service ./services/appointment-service
   docker build -t petpal/medical-service ./services/medical-service
   docker build -t petpal/frontend ./frontend
   ```

2. **Deploy to Kubernetes**
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

3. **Access the application**
   ```bash
   kubectl port-forward service/frontend 3000:3000 -n petpal
   ```

## 📁 Project Structure

```
PetPal/
├── frontend/                 # Flask frontend application
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── services/
│   ├── user-service/         # User management microservice
│   ├── pet-service/          # Pet management microservice
│   ├── appointment-service/  # Appointment management microservice
│   └── medical-service/      # Medical records microservice
├── kubernetes/               # Kubernetes deployment files
├── monitoring/               # Prometheus and Grafana configs
├── tests/                    # Integration and E2E tests
├── scripts/                  # Setup and deployment scripts
├── docker-compose.yml
└── README.md
```

## 🛠️ Development

### Running Individual Services

Each microservice can be run independently:

```bash
cd services/user-service
pip install -r requirements.txt
python app.py
```

### Environment Variables

Create a `.env` file in the root directory:

```env
MONGODB_URI=mongodb+srv://acsujan69:petpal123@petpal.9k6d9qu.mongodb.net/
JWT_SECRET=your_jwt_secret_key_here
USER_SERVICE_URL=http://localhost:5001
PET_SERVICE_URL=http://localhost:5002
APPOINTMENT_SERVICE_URL=http://localhost:5003
MEDICAL_SERVICE_URL=http://localhost:5004
```

### Running Tests

```bash
# Install test dependencies
pip install pytest requests

# Run unit tests for a specific service
cd services/user-service
python -m pytest tests/ -v

# Run integration tests
python -m pytest tests/integration/ -v

# Run all tests
python -m pytest tests/ -v --tb=short
```

## 📊 API Documentation

### User Service (Port 5001)

- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `DELETE /api/users/profile` - Delete user profile

### Pet Service (Port 5002)

- `POST /api/pets/` - Create new pet
- `GET /api/pets/` - Get user's pets
- `GET /api/pets/{id}` - Get specific pet
- `PUT /api/pets/{id}` - Update pet
- `DELETE /api/pets/{id}` - Delete pet

### Appointment Service (Port 5003)

- `POST /api/appointments/` - Schedule appointment
- `GET /api/appointments/` - Get appointments
- `GET /api/appointments/upcoming` - Get upcoming appointments
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment

### Medical Service (Port 5004)

- `POST /api/medical/` - Add medical record
- `GET /api/medical/` - Get medical records
- `GET /api/medical/{id}` - Get specific record
- `PUT /api/medical/{id}` - Update medical record
- `DELETE /api/medical/{id}` - Delete medical record

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for authentication:

1. Register or login to receive a JWT token
2. Include the token in the `Authorization` header: `Bearer <token>`
3. Tokens expire after 24 hours

## 📈 Monitoring

### Prometheus Metrics

Each service exposes metrics at `/metrics`:
- HTTP request counts and durations
- Service health status
- Custom business metrics

### Grafana Dashboards

Access Grafana at http://localhost:3001 (admin/admin) to view:
- Service performance metrics
- Request rates and error rates
- System resource usage

## 🧪 Testing Strategy

### Unit Tests
- Individual service functionality
- Model and route testing
- Mock external dependencies

### Integration Tests
- Service-to-service communication
- Database operations
- API contract testing

### End-to-End Tests
- Complete user workflows
- Frontend and backend integration
- Cross-service scenarios

## 🚀 CI/CD Pipeline

The project includes a GitHub Actions workflow that:

1. **Linting and Testing**: Runs code quality checks and unit tests
2. **Security Scanning**: Scans for vulnerabilities
3. **Building**: Creates Docker images for all services
4. **Deployment**: Deploys to staging and production environments
5. **Integration Testing**: Runs integration and E2E tests
6. **Monitoring**: Sends deployment notifications

## 🐳 Docker Images

Each service has its own Dockerfile optimized for:
- Small image size using Python slim base
- Multi-stage builds where applicable
- Proper layer caching
- Security best practices

## ☸️ Kubernetes Features

- **Deployments**: With replica sets for high availability
- **Services**: For service discovery and load balancing
- **ConfigMaps**: For configuration management
- **Health Checks**: Liveness and readiness probes
- **Resource Limits**: CPU and memory constraints
- **Horizontal Pod Autoscaling**: Automatic scaling based on load

## 🔧 Configuration

### MongoDB Setup

The application uses MongoDB Atlas. Update the connection string in:
- Environment variables
- Docker Compose file
- Kubernetes deployments

### Security Considerations

- Change default JWT secrets in production
- Use Kubernetes secrets for sensitive data
- Enable MongoDB authentication
- Configure HTTPS/TLS for production
- Implement rate limiting
- Add input validation and sanitization

## 📋 Production Checklist

- [ ] Update all default passwords and secrets
- [ ] Configure proper MongoDB security
- [ ] Set up HTTPS/TLS certificates
- [ ] Configure production logging
- [ ] Set up backup strategies
- [ ] Configure monitoring alerts
- [ ] Implement rate limiting
- [ ] Set up proper CORS policies
- [ ] Configure resource limits
- [ ] Set up autoscaling policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Services not starting**
   - Check Docker is running
   - Verify port availability
   - Check MongoDB connection

2. **Database connection errors**
   - Verify MongoDB URI
   - Check network connectivity
   - Ensure database exists

3. **Authentication issues**
   - Verify JWT secret consistency
   - Check token expiration
   - Validate user credentials

### Getting Help

- Check the logs: `docker-compose logs -f`
- View individual service logs: `docker logs <container-name>`
- For Kubernetes: `kubectl logs -f deployment/<service-name> -n petpal`

## 📞 Support

For support, please create an issue in the GitHub repository or contact the development team.

---

Made with ❤️ for pet lovers everywhere! 🐕🐱🐰