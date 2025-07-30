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
- 
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
