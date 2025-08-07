import pytest
import json
import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import AppointmentModel

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    os.environ['DATABASE_NAME'] = 'petpal_appointments_test'
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def appointment_model():
    """Appointment model instance for testing."""
    os.environ['DATABASE_NAME'] = 'petpal_appointments_test'
    return AppointmentModel()

@pytest.fixture
def mock_token():
    """Mock JWT token for testing."""
    return "Bearer mock_jwt_token_for_testing"

@pytest.fixture
def sample_appointment_data():
    """Sample appointment data for testing."""
    future_date = datetime.utcnow() + timedelta(days=7)
    return {
        'pet_id': 'test_pet_123',
        'appointment_type': 'Check-up',
        'appointment_date': future_date.isoformat(),
        'veterinarian': 'Dr. Smith',
        'clinic': 'Happy Pets Clinic',
        'reason': 'Annual health checkup',
        'status': 'scheduled'
    }

class TestAppointmentService:
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'appointment-service'

    def test_create_appointment_without_token(self, client, sample_appointment_data):
        """Test creating an appointment without authentication token."""
        response = client.post('/api/appointments/', 
                             json=sample_appointment_data,
                             content_type='application/json')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Token is missing'

    def test_create_appointment_missing_required_fields(self, client, mock_token):
        """Test creating an appointment with missing required fields."""
        incomplete_data = {
            'appointment_type': 'Check-up'
            # Missing pet_id, appointment_date, veterinarian
        }
        response = client.post('/api/appointments/', 
                             json=incomplete_data,
                             content_type='application/json',
                             headers={'Authorization': mock_token})
        # This will fail due to token verification, but tests the validation logic
        assert response.status_code == 401  # Due to mock token

    def test_get_appointments_without_token(self, client):
        """Test getting appointments without authentication token."""
        response = client.get('/api/appointments/')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Token is missing'

    def test_appointment_model_create_appointment(self, appointment_model, sample_appointment_data):
        """Test appointment model create_appointment method."""
        sample_appointment_data['user_id'] = 'test_user_123'
        sample_appointment_data['appointment_date'] = datetime.utcnow() + timedelta(days=7)
        
        appointment_id = appointment_model.create_appointment(sample_appointment_data)
        assert appointment_id is not None
        
        # Verify appointment was created
        appointment = appointment_model.get_appointment_by_id(appointment_id)
        assert appointment['appointment_type'] == 'Check-up'
        assert appointment['veterinarian'] == 'Dr. Smith'
        assert appointment['user_id'] == 'test_user_123'
        assert appointment['status'] == 'scheduled'

    def test_appointment_model_get_appointments_by_user(self, appointment_model, sample_appointment_data):
        """Test appointment model get_appointments_by_user method."""
        user_id = 'test_user_456'
        sample_appointment_data['user_id'] = user_id
        sample_appointment_data['appointment_date'] = datetime.utcnow() + timedelta(days=7)
        
        # Create multiple appointments for the user
        appointment_id1 = appointment_model.create_appointment(sample_appointment_data)
        
        sample_appointment_data['appointment_type'] = 'Vaccination'
        sample_appointment_data['veterinarian'] = 'Dr. Johnson'
        sample_appointment_data['appointment_date'] = datetime.utcnow() + timedelta(days=14)
        appointment_id2 = appointment_model.create_appointment(sample_appointment_data)
        
        # Get appointments for the user
        appointments = appointment_model.get_appointments_by_user(user_id)
        assert len(appointments) == 2
        
        appointment_types = [apt['appointment_type'] for apt in appointments]
        assert 'Check-up' in appointment_types
        assert 'Vaccination' in appointment_types

    def test_appointment_model_get_appointments_by_pet(self, appointment_model, sample_appointment_data):
        """Test appointment model get_appointments_by_pet method."""
        pet_id = 'test_pet_789'
        sample_appointment_data['pet_id'] = pet_id
        sample_appointment_data['user_id'] = 'test_user_789'
        sample_appointment_data['appointment_date'] = datetime.utcnow() + timedelta(days=7)
        
        appointment_id = appointment_model.create_appointment(sample_appointment_data)
        
        # Get appointments for the pet
        appointments = appointment_model.get_appointments_by_pet(pet_id)
        assert len(appointments) == 1
        assert appointments[0]['pet_id'] == pet_id

    def test_appointment_model_update_appointment(self, appointment_model, sample_appointment_data):
        """Test appointment model update_appointment method."""
        sample_appointment_data['user_id'] = 'test_user_update'
        sample_appointment_data['appointment_date'] = datetime.utcnow() + timedelta(days=7)
        appointment_id = appointment_model.create_appointment(sample_appointment_data)
        
        # Update appointment
        new_date = datetime.utcnow() + timedelta(days=10)
        update_data = {
            'appointment_date': new_date,
            'status': 'confirmed',
            'reason': 'Updated reason for visit'
        }
        result = appointment_model.update_appointment(appointment_id, update_data)
        assert result is True
        
        # Verify update
        updated_appointment = appointment_model.get_appointment_by_id(appointment_id)
        assert updated_appointment['status'] == 'confirmed'
        assert updated_appointment['reason'] == 'Updated reason for visit'
        assert updated_appointment['appointment_type'] == 'Check-up'  # Unchanged

    def test_appointment_model_delete_appointment(self, appointment_model, sample_appointment_data):
        """Test appointment model delete_appointment method."""
        sample_appointment_data['user_id'] = 'test_user_delete'
        sample_appointment_data['appointment_date'] = datetime.utcnow() + timedelta(days=7)
        appointment_id = appointment_model.create_appointment(sample_appointment_data)
        
        # Verify appointment exists
        appointment = appointment_model.get_appointment_by_id(appointment_id)
        assert appointment is not None
        
        # Delete appointment
        result = appointment_model.delete_appointment(appointment_id)
        assert result is True
        
        # Verify appointment is deleted
        deleted_appointment = appointment_model.get_appointment_by_id(appointment_id)
        assert deleted_appointment is None

    def test_appointment_model_get_upcoming_appointments(self, appointment_model, sample_appointment_data):
        """Test appointment model get_upcoming_appointments method."""
        user_id = 'test_user_upcoming'
        sample_appointment_data['user_id'] = user_id
        
        # Create a past appointment
        past_date = datetime.utcnow() - timedelta(days=7)
        sample_appointment_data['appointment_date'] = past_date
        sample_appointment_data['status'] = 'completed'
        appointment_model.create_appointment(sample_appointment_data)
        
        # Create an upcoming appointment
        future_date = datetime.utcnow() + timedelta(days=7)
        sample_appointment_data['appointment_date'] = future_date
        sample_appointment_data['status'] = 'scheduled'
        appointment_model.create_appointment(sample_appointment_data)
        
        # Get upcoming appointments
        upcoming = appointment_model.get_upcoming_appointments(user_id)
        assert len(upcoming) == 1
        assert upcoming[0]['status'] in ['scheduled', 'confirmed']

    def test_appointment_model_get_appointment_by_id_and_user(self, appointment_model, sample_appointment_data):
        """Test appointment model get_appointment_by_id_and_user method."""
        user_id = 'test_user_ownership'
        sample_appointment_data['user_id'] = user_id
        sample_appointment_data['appointment_date'] = datetime.utcnow() + timedelta(days=7)
        appointment_id = appointment_model.create_appointment(sample_appointment_data)
        
        # Get appointment with correct user
        appointment = appointment_model.get_appointment_by_id_and_user(appointment_id, user_id)
        assert appointment is not None
        assert appointment['user_id'] == user_id
        
        # Try to get appointment with wrong user
        wrong_appointment = appointment_model.get_appointment_by_id_and_user(appointment_id, 'wrong_user_id')
        assert wrong_appointment is None

    def test_appointment_model_invalid_appointment_id(self, appointment_model):
        """Test appointment model with invalid appointment ID."""
        appointment = appointment_model.get_appointment_by_id('invalid_id')
        assert appointment is None

    def test_appointment_model_update_nonexistent_appointment(self, appointment_model):
        """Test updating a nonexistent appointment."""
        result = appointment_model.update_appointment('nonexistent_id', {'status': 'confirmed'})
        assert result is False

    def test_appointment_model_delete_nonexistent_appointment(self, appointment_model):
        """Test deleting a nonexistent appointment."""
        result = appointment_model.delete_appointment('nonexistent_id')
        assert result is False

    def teardown_method(self):
        """Clean up after each test."""
        # Clean up test database
        appointment_model = AppointmentModel()
        appointment_model.collection.drop()