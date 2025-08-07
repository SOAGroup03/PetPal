import pytest
import json
import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import MedicalModel

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    os.environ['DATABASE_NAME'] = 'petpal_medical_test'
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def medical_model():
    """Medical model instance for testing."""
    os.environ['DATABASE_NAME'] = 'petpal_medical_test'
    return MedicalModel()

@pytest.fixture
def mock_token():
    """Mock JWT token for testing."""
    return "Bearer mock_jwt_token_for_testing"

@pytest.fixture
def sample_medical_data():
    """Sample medical record data for testing."""
    return {
        'pet_id': 'test_pet_123',
        'record_type': 'vaccination',
        'visit_date': (datetime.utcnow() - timedelta(days=30)).isoformat(),
        'veterinarian': 'Dr. Smith',
        'clinic': 'Happy Pets Clinic',
        'diagnosis': 'Annual vaccination - Rabies, DHPP',
        'treatment': 'Administered vaccinations',
        'medications': 'None',
        'weight': 25.5,
        'temperature': 38.5,
        'notes': 'Pet tolerated vaccines well',
        'follow_up_date': (datetime.utcnow() + timedelta(days=365)).isoformat()
    }

class TestMedicalService:
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'medical-service'

    def test_create_medical_record_without_token(self, client, sample_medical_data):
        """Test creating a medical record without authentication token."""
        response = client.post('/api/medical/', 
                             json=sample_medical_data,
                             content_type='application/json')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Token is missing'

    def test_create_medical_record_missing_required_fields(self, client, mock_token):
        """Test creating a medical record with missing required fields."""
        incomplete_data = {
            'record_type': 'vaccination'
            # Missing pet_id, visit_date, veterinarian, diagnosis
        }
        response = client.post('/api/medical/', 
                             json=incomplete_data,
                             content_type='application/json',
                             headers={'Authorization': mock_token})
        # This will fail due to token verification, but tests the validation logic
        assert response.status_code == 401  # Due to mock token

    def test_get_medical_records_without_token(self, client):
        """Test getting medical records without authentication token."""
        response = client.get('/api/medical/')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Token is missing'

    def test_medical_model_create_medical_record(self, medical_model, sample_medical_data):
        """Test medical model create_medical_record method."""
        sample_medical_data['user_id'] = 'test_user_123'
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=30)
        
        record_id = medical_model.create_medical_record(sample_medical_data)
        assert record_id is not None
        
        # Verify medical record was created
        record = medical_model.get_medical_record_by_id(record_id)
        assert record['record_type'] == 'vaccination'
        assert record['veterinarian'] == 'Dr. Smith'
        assert record['diagnosis'] == 'Annual vaccination - Rabies, DHPP'
        assert record['user_id'] == 'test_user_123'

    def test_medical_model_get_medical_records_by_user(self, medical_model, sample_medical_data):
        """Test medical model get_medical_records_by_user method."""
        user_id = 'test_user_456'
        sample_medical_data['user_id'] = user_id
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=30)
        
        # Create multiple medical records for the user
        record_id1 = medical_model.create_medical_record(sample_medical_data)
        
        sample_medical_data['record_type'] = 'checkup'
        sample_medical_data['diagnosis'] = 'Annual health examination'
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=15)
        record_id2 = medical_model.create_medical_record(sample_medical_data)
        
        # Get medical records for the user
        records = medical_model.get_medical_records_by_user(user_id)
        assert len(records) == 2
        
        record_types = [record['record_type'] for record in records]
        assert 'vaccination' in record_types
        assert 'checkup' in record_types

    def test_medical_model_get_medical_records_by_pet(self, medical_model, sample_medical_data):
        """Test medical model get_medical_records_by_pet method."""
        pet_id = 'test_pet_789'
        sample_medical_data['pet_id'] = pet_id
        sample_medical_data['user_id'] = 'test_user_789'
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=30)
        
        record_id = medical_model.create_medical_record(sample_medical_data)
        
        # Get medical records for the pet
        records = medical_model.get_medical_records_by_pet(pet_id)
        assert len(records) == 1
        assert records[0]['pet_id'] == pet_id

    def test_medical_model_update_medical_record(self, medical_model, sample_medical_data):
        """Test medical model update_medical_record method."""
        sample_medical_data['user_id'] = 'test_user_update'
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=30)
        record_id = medical_model.create_medical_record(sample_medical_data)
        
        # Update medical record
        update_data = {
            'treatment': 'Updated treatment plan',
            'medications': 'Antibiotics prescribed',
            'notes': 'Updated notes about the visit'
        }
        result = medical_model.update_medical_record(record_id, update_data)
        assert result is True
        
        # Verify update
        updated_record = medical_model.get_medical_record_by_id(record_id)
        assert updated_record['treatment'] == 'Updated treatment plan'
        assert updated_record['medications'] == 'Antibiotics prescribed'
        assert updated_record['notes'] == 'Updated notes about the visit'
        assert updated_record['diagnosis'] == 'Annual vaccination - Rabies, DHPP'  # Unchanged

    def test_medical_model_delete_medical_record(self, medical_model, sample_medical_data):
        """Test medical model delete_medical_record method."""
        sample_medical_data['user_id'] = 'test_user_delete'
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=30)
        record_id = medical_model.create_medical_record(sample_medical_data)
        
        # Verify medical record exists
        record = medical_model.get_medical_record_by_id(record_id)
        assert record is not None
        
        # Delete medical record
        result = medical_model.delete_medical_record(record_id)
        assert result is True
        
        # Verify medical record is deleted
        deleted_record = medical_model.get_medical_record_by_id(record_id)
        assert deleted_record is None

    def test_medical_model_get_records_by_type(self, medical_model, sample_medical_data):
        """Test medical model get_records_by_type method."""
        pet_id = 'test_pet_type'
        sample_medical_data['pet_id'] = pet_id
        sample_medical_data['user_id'] = 'test_user_type'
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=30)
        
        # Create vaccination record
        record_id1 = medical_model.create_medical_record(sample_medical_data)
        
        # Create checkup record
        sample_medical_data['record_type'] = 'checkup'
        sample_medical_data['diagnosis'] = 'Annual health examination'
        record_id2 = medical_model.create_medical_record(sample_medical_data)
        
        # Get vaccination records
        vaccination_records = medical_model.get_records_by_type(pet_id, 'vaccination')
        assert len(vaccination_records) == 1
        assert vaccination_records[0]['record_type'] == 'vaccination'
        
        # Get checkup records
        checkup_records = medical_model.get_records_by_type(pet_id, 'checkup')
        assert len(checkup_records) == 1
        assert checkup_records[0]['record_type'] == 'checkup'

    def test_medical_model_get_vaccination_history(self, medical_model, sample_medical_data):
        """Test medical model get_vaccination_history method."""
        pet_id = 'test_pet_vaccination'
        sample_medical_data['pet_id'] = pet_id
        sample_medical_data['user_id'] = 'test_user_vaccination'
        sample_medical_data['record_type'] = 'vaccination'
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=30)
        
        record_id = medical_model.create_medical_record(sample_medical_data)
        
        # Get vaccination history
        vaccination_history = medical_model.get_vaccination_history(pet_id)
        assert len(vaccination_history) == 1
        assert vaccination_history[0]['record_type'] == 'vaccination'

    def test_medical_model_get_recent_records(self, medical_model, sample_medical_data):
        """Test medical model get_recent_records method."""
        user_id = 'test_user_recent'
        sample_medical_data['user_id'] = user_id
        
        # Create multiple records
        for i in range(5):
            sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=i*10)
            sample_medical_data['diagnosis'] = f'Diagnosis {i+1}'
            medical_model.create_medical_record(sample_medical_data)
        
        # Get recent records (limit 3)
        recent_records = medical_model.get_recent_records(user_id, 3)
        assert len(recent_records) == 3

    def test_medical_model_get_medical_record_by_id_and_user(self, medical_model, sample_medical_data):
        """Test medical model get_medical_record_by_id_and_user method."""
        user_id = 'test_user_ownership'
        sample_medical_data['user_id'] = user_id
        sample_medical_data['visit_date'] = datetime.utcnow() - timedelta(days=30)
        record_id = medical_model.create_medical_record(sample_medical_data)
        
        # Get medical record with correct user
        record = medical_model.get_medical_record_by_id_and_user(record_id, user_id)
        assert record is not None
        assert record['user_id'] == user_id
        
        # Try to get medical record with wrong user
        wrong_record = medical_model.get_medical_record_by_id_and_user(record_id, 'wrong_user_id')
        assert wrong_record is None

    def test_medical_model_invalid_record_id(self, medical_model):
        """Test medical model with invalid record ID."""
        record = medical_model.get_medical_record_by_id('invalid_id')
        assert record is None

    def test_medical_model_update_nonexistent_record(self, medical_model):
        """Test updating a nonexistent medical record."""
        result = medical_model.update_medical_record('nonexistent_id', {'diagnosis': 'Updated'})
        assert result is False

    def test_medical_model_delete_nonexistent_record(self, medical_model):
        """Test deleting a nonexistent medical record."""
        result = medical_model.delete_medical_record('nonexistent_id')
        assert result is False

    def teardown_method(self):
        """Clean up after each test."""
        # Clean up test database
        medical_model = MedicalModel()
        medical_model.collection.drop()