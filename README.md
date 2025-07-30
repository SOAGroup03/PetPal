# 🐾 PetPal - Complete Pet Care Management System

A comprehensive microservices-based pet care management system built with Flask, MongoDB Atlas, and deployed on Google Cloud Platform with Prometheus and Grafana monitoring.

## 🏗️ Architecture

- **Frontend**: HTML/CSS/JavaScript with Bootstrap
- **Backend**: 4 Python Flask microservices with JWT authentication
- **Database**: MongoDB Atlas (Cloud)
- **Monitoring**: Prometheus & Grafana
- **Deployment**: Docker & Kubernetes on Google Cloud Platform
- **Cloud**: Google Cloud Platform (Project: petpal-467223)

## 🔧 Configuration

### Database
- **MongoDB Atlas**: `mongodb+srv://acsujan69:petpal123@petpal.9k6d9qu.mongodb.net/petpal`
- **Database Name**: `petpal`

### Google Cloud
- **Project ID**: `petpal-467223`
- **Container Registry**: `gcr.io/petpal-467223`
- **Region**: `us-central1`

## 🚀 Quick Start

### Option 1: Local Development with Docker Compose
```bash
# 1. Create project structure
mkdir -p petpal && cd petpal

# 2. Copy all files from artifacts to respective directories

# 3. Run with Docker Compose
docker-compose up --build

# 4. Access applications
# Frontend: http://localhost:5000
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/petpal123)
```

### Option 2: Google Cloud Deployment
```bash
# 1. Ensure you have Google Cloud SDK installed
# 2. Make scripts executable
chmod +x scripts/*.sh

# 3. Run automated deployment
./scripts/build-and-deploy.sh

# 4. Access via LoadBalancer IPs provided in output
```

## 📁 Project Structure

```
petpal/
├── microservices/
│   ├── user-service/        # Authentication & user management
│   ├── pet-service/         # Pet profile management
│   ├── appointment-service/ # Appointment scheduling
│   └── medical-service/     # Medical history tracking
├── frontend/                # Web interface
├── kubernetes/              # K8s deployment manifests
├── monitoring/              # Prometheus & Grafana config
├── scripts/                 # Deployment automation
├── docker-compose.yml       # Local development
└── README.md
```

## 🔌 API Endpoints

### User Service (Port 5001)
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `DELETE /api/users/profile` - Delete account

### Pet Service (Port 5002)
- `POST /api/pets/` - Add new pet
- `GET /api/pets/` - Get user's pets
- `GET /api/pets/{id}` - Get specific pet
- `PUT /api/pets/{id}` - Update pet
- `DELETE /api/pets/{id}` - Delete pet

### Appointment Service (Port 5003)
- `POST /api/appointments/` - Schedule appointment
- `GET /api/appointments/` - Get appointments
- `GET /api/appointments/{id}` - Get specific appointment
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment

### Medical Service (Port 5004)
- `POST /api/medical/` - Add medical record
- `GET /api/medical/` - Get all records
- `GET /api/medical/{id}` - Get specific record
- `PUT /api/medical/{id}` - Update record
- `DELETE /api/medical/{id}` - Delete record
- `GET /api/medical/pet/{pet_id}` - Get records by pet

## 🛠️ Development Setup

### Prerequisites
- Docker & Docker Compose
- Google Cloud SDK (for cloud deployment)
- Python 3.9+ (for local development)

### Local Development
```bash
# Run local setup script
./scripts/local-setup.sh

# Install dependencies for each service
cd microservices/user-service && pip install -r requirements.txt
cd ../pet-service && pip install -r requirements.txt
cd ../appointment-service && pip install -r requirements.txt
cd ../medical-service && pip install -r requirements.txt
cd ../../frontend && pip install -r requirements.txt

# Run each service in separate terminals
python microservices/user-service/app.py
python microservices/pet-service/app.py
python microservices/appointment-service/app.py
python microservices/medical-service/app.py
python frontend/app.py
```

## 📊 Monitoring

### Prometheus Metrics
- HTTP request rates and response times
- Error rates and status codes
- System resource usage (CPU, memory)
- Custom business metrics

### Grafana Dashboards
- Service health monitoring
- Performance metrics visualization
- Real-time alerting
- Resource utilization tracking

**Access**: Grafana at port 3000 (admin/petpal123)

## 🔐 Security Features

- JWT token-based authentication
- Password hashing with Werkzeug
- Input validation and sanitization
- User-based data isolation
- CORS protection
- Kubernetes secrets management

## 📈 Scaling & Performance

- Horizontal Pod Autoscaling (HPA)
- Multi-replica deployments
- Load balancing with GCP Load Balancer
- Persistent storage for monitoring
- Resource limits and requests

## 🚀 Deployment Commands

### Build and Deploy to Google Cloud
```bash
./scripts/build-and-deploy.sh
```

### Update Images
```bash
./scripts/update-images.sh
```

### Cleanup Resources
```bash
./scripts/cleanup.sh
```

### Manual Kubernetes Commands
```bash
# Apply all manifests
kubectl apply -f kubernetes/

# Check pod status
kubectl get pods -n petpal

# View logs
kubectl logs -f deployment/user-service -n petpal

# Scale deployment
kubectl scale deployment user-service --replicas=5 -n petpal
```

## 🗄️ Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "first_name": "string",
  "last_name": "string", 
  "email": "string",
  "password": "hashed_string",
  "phone": "string",
  "address": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Pets Collection
```json
{
  "_id": "ObjectId",
  "owner_id": "string",
  "name": "string",
  "species": "string",
  "breed": "string",
  "date_of_birth": "date",
  "gender": "string",
  "weight": "number",
  "color": "string",
  "microchip_id": "string"
}
```

### Appointments Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "pet_id": "string", 
  "appointment_date": "date",
  "appointment_time": "time",
  "vet_name": "string",
  "reason": "string",
  "status": "string",
  "notes": "string"
}
```

### Medical History Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "pet_id": "string",
  "visit_date": "date", 
  "vet_name": "string",
  "diagnosis": "string",
  "treatment": "string",
  "medications": "string",
  "follow_up_date": "date",
  "notes": "string"
}
```

## 🔧 Troubleshooting

### Common Issues

**MongoDB Connection**
- Ensure IP is whitelisted in MongoDB Atlas
- Verify connection string is correct

**Kubernetes Pods Not Starting**
```bash
kubectl describe pod <pod-name> -n petpal
kubectl logs <pod-name> -n petpal
```

**Service Communication Issues**
```bash
kubectl get services -n petpal
kubectl get endpoints -n petpal
```

**Image Pull Errors**
```bash
# Re-authenticate with GCR
gcloud auth configure-docker
```

### Monitoring Health
```bash
# Check all deployments
kubectl get deployments -n petpal

# Check HPA status  
kubectl get hpa -n petpal

# View resource usage
kubectl top pods -n petpal
```

## 🌟 Features

### User Management
- User registration and authentication
- Profile management
- JWT token-based security

### Pet Management
- Add/edit/delete pets
- Comprehensive pet profiles
- Species and breed tracking

### Appointment Scheduling
- Schedule vet appointments
- Track appointment status
- Veterinarian information

### Medical History
- Detailed medical records
- Treatment tracking
- Medication management
- Follow-up scheduling

### Monitoring & Analytics
- Real-time system monitoring
- Performance dashboards
- Resource utilization tracking

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review logs via `kubectl logs`
- Monitor via Grafana dashboards
- Create GitHub issues for bugs

---

**🎉 PetPal is now ready for deployment!**

Copy each artifact content to the respective files and run:
- **Local**: `docker-compose up --build` 
- **Cloud**: `./scripts/build-and-deploy.sh`