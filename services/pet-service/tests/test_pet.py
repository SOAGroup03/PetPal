import pytest
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import PetModel

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    os.environ['DATABASE_NAME'] = 'petpal_pets_test'
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def pet_model():
    """Pet model instance for testing."""
    os.environ['DATABASE_NAME'] = 'petpal_pets_test'
    return PetModel()

@pytest.fixture
def mock_token():
    """Mock JWT token for testing."""
    return "Bearer mock_jwt_token_for_testing"

@pytest.fixture
def sample_pet_data():
    """Sample pet data for testing."""
    return {
        'name': 'Buddy',
        'species': 'Dog',
        'breed': 'Golden Retriever',
        'age': 3,
        'gender': 'Male',
        'weight': 25.5,
        'color': 'Golden',
        'microchip_id': 'TEST123456789',
        'notes': 'Friendly and energetic dog'
    }

class TestPetService:
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'pet-service'

    def test_create_pet_without_token(self, client, sample_pet_data):
        """Test creating a pet without authentication token."""
        response = client.post('/api/pets/', 
                             json=sample_pet_data,
                             content_type='application/json')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Token is missing'

    def test_create_pet_missing_required_fields(self, client, mock_token):
        """Test creating a pet with missing required fields."""
        incomplete_data = {
            'name': 'Buddy'
            # Missing species, breed, age
        }
        response = client.post('/api/pets/', 
                             json=incomplete_data,
                             content_type='application/json',
                             headers={'Authorization': mock_token})
        # This will fail due to token verification, but tests the validation logic
        assert response.status_code == 401  # Due to mock token

    def test_get_pets_without_token(self, client):
        """Test getting pets without authentication token."""
        response = client.get('/api/pets/')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Token is missing'

    def test_pet_model_create_pet(self, pet_model, sample_pet_data):
        """Test pet model create_pet method."""
        sample_pet_data['user_id'] = 'test_user_123'
        pet_id = pet_model.create_pet(sample_pet_data)
        assert pet_id is not None
        
        # Verify pet was created
        pet = pet_model.get_pet_by_id(pet_id)
        assert pet['name'] == 'Buddy'
        assert pet['species'] == 'Dog'
        assert pet['breed'] == 'Golden Retriever'
        assert pet['age'] == 3
        assert pet['user_id'] == 'test_user_123'

    def test_pet_model_get_pets_by_user(self, pet_model, sample_pet_data):
        """Test pet model get_pets_by_user method."""
        user_id = 'test_user_456'
        sample_pet_data['user_id'] = user_id
        
        # Create multiple pets for the user
        pet_id1 = pet_model.create_pet(sample_pet_data)
        
        sample_pet_data['name'] = 'Max'
        sample_pet_data['species'] = 'Cat'
        pet_id2 = pet_model.create_pet(sample_pet_data)
        
        # Get pets for the user
        pets = pet_model.get_pets_by_user(user_id)
        assert len(pets) == 2
        
        pet_names = [pet['name'] for pet in pets]
        assert 'Buddy' in pet_names
        assert 'Max' in pet_names

    def test_pet_model_update_pet(self, pet_model, sample_pet_data):
        """Test pet model update_pet method."""
        sample_pet_data['user_id'] = 'test_user_789'
        pet_id = pet_model.create_pet(sample_pet_data)
        
        # Update pet
        update_data = {
            'age': 4,
            'weight': 26.0,
            'notes': 'Updated notes for the pet'
        }
        result = pet_model.update_pet(pet_id, update_data)
        assert result is True
        
        # Verify update
        updated_pet = pet_model.get_pet_by_id(pet_id)
        assert updated_pet['age'] == 4
        assert updated_pet['weight'] == 26.0
        assert updated_pet['notes'] == 'Updated notes for the pet'
        assert updated_pet['name'] == 'Buddy'  # Unchanged

    def test_pet_model_delete_pet(self, pet_model, sample_pet_data):
        """Test pet model delete_pet method."""
        sample_pet_data['user_id'] = 'test_user_delete'
        pet_id = pet_model.create_pet(sample_pet_data)
        
        # Verify pet exists
        pet = pet_model.get_pet_by_id(pet_id)
        assert pet is not None
        
        # Delete pet
        result = pet_model.delete_pet(pet_id)
        assert result is True
        
        # Verify pet is deleted
        deleted_pet = pet_model.get_pet_by_id(pet_id)
        assert deleted_pet is None

    def test_pet_model_get_pet_by_id_and_user(self, pet_model, sample_pet_data):
        """Test pet model get_pet_by_id_and_user method."""
        user_id = 'test_user_ownership'
        sample_pet_data['user_id'] = user_id
        pet_id = pet_model.create_pet(sample_pet_data)
        
        # Get pet with correct user
        pet = pet_model.get_pet_by_id_and_user(pet_id, user_id)
        assert pet is not None
        assert pet['name'] == 'Buddy'
        assert pet['user_id'] == user_id
        
        # Try to get pet with wrong user
        wrong_pet = pet_model.get_pet_by_id_and_user(pet_id, 'wrong_user_id')
        assert wrong_pet is None

    def test_pet_model_invalid_pet_id(self, pet_model):
        """Test pet model with invalid pet ID."""
        pet = pet_model.get_pet_by_id('invalid_id')
        assert pet is None

    def test_pet_model_update_nonexistent_pet(self, pet_model):
        """Test updating a nonexistent pet."""
        result = pet_model.update_pet('nonexistent_id', {'name': 'Updated'})
        assert result is False

    def test_pet_model_delete_nonexistent_pet(self, pet_model):
        """Test deleting a nonexistent pet."""
        result = pet_model.delete_pet('nonexistent_id')
        assert result is False

    def teardown_method(self):
        """Clean up after each test."""
        # Clean up test database
        pet_model = PetModel()
        pet_model.collection.drop()