import pytest
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import UserModel

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    os.environ['DATABASE_NAME'] = 'petpal_users_test'
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def user_model():
    """User model instance for testing."""
    os.environ['DATABASE_NAME'] = 'petpal_users_test'
    return UserModel()

class TestUserService:
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'user-service'

    def test_user_registration(self, client):
        """Test user registration."""
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone': '+1234567890'
        }
        print("Response JSON:", response.get_json())
        print("Response Status:", response.status_code)

        response = client.post('/api/users/register', 
                             json=user_data,
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert data['message'] == 'User created successfully'

    def test_user_registration_duplicate_email(self, client):
        """Test user registration with duplicate email."""
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone': '+1234567890'
        }
        # First registration
        client.post('/api/users/register', 
                   json=user_data,
                   content_type='application/json')
        
        # Second registration with same email
        response = client.post('/api/users/register', 
                             json=user_data,
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'User already exists'

    def test_user_login(self, client):
        """Test user login."""
        # First register a user
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone': '+1234567890'
        }
        client.post('/api/users/register', 
                   json=user_data,
                   content_type='application/json')
        
        # Then login
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = client.post('/api/users/login',
                             json=login_data,
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'

    def test_user_login_invalid_credentials(self, client):
        """Test user login with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = client.post('/api/users/login',
                             json=login_data,
                             content_type='application/json')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Invalid credentials'

    def test_get_profile_without_token(self, client):
        """Test getting profile without authentication token."""
        response = client.get('/api/users/profile')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Token is missing'

    def test_user_model_create_user(self, user_model):
        """Test user model create_user method."""
        user_data = {
            'name': 'Model Test User',
            'email': 'modeltest@example.com',
            'password': 'testpass123',
            'phone': '+1234567890'
        }
        user_id = user_model.create_user(user_data)
        assert user_id is not None
        
        # Verify user was created
        user = user_model.get_user_by_id(user_id)
        assert user['name'] == 'Model Test User'
        assert user['email'] == 'modeltest@example.com'

    def test_user_model_get_user_by_email(self, user_model):
        """Test user model get_user_by_email method."""
        user_data = {
            'name': 'Email Test User',
            'email': 'emailtest@example.com',
            'password': 'testpass123',
            'phone': '+1234567890'
        }
        user_id = user_model.create_user(user_data)
        
        # Get user by email
        user = user_model.get_user_by_email('emailtest@example.com')
        assert user is not None
        assert user['name'] == 'Email Test User'
        assert user['_id'] == user_id

    def test_user_model_verify_password(self, user_model):
        """Test user model verify_password method."""
        user_data = {
            'name': 'Password Test User',
            'email': 'passwordtest@example.com',
            'password': 'testpass123',
            'phone': '+1234567890'
        }
        user_model.create_user(user_data)
        
        # Verify correct password
        user = user_model.verify_password('passwordtest@example.com', 'testpass123')
        assert user is not None
        assert user['email'] == 'passwordtest@example.com'
        
        # Verify incorrect password
        user = user_model.verify_password('passwordtest@example.com', 'wrongpassword')
        assert user is None

    def teardown_method(self):
        """Clean up after each test."""
        # Clean up test database
        user_model = UserModel()
        user_model.collection.drop()
