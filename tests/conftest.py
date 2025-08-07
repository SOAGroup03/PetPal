"""
Global test configuration and fixtures for PetPal tests.
"""
import pytest
import os
import time
import requests
from typing import Dict, Any

# Test configuration
TEST_CONFIG = {
    'base_url': os.getenv('TEST_BASE_URL', 'http://localhost:3000'),
    'user_service_url': os.getenv('USER_SERVICE_URL', 'http://localhost:5001'),
    'pet_service_url': os.getenv('PET_SERVICE_URL', 'http://localhost:5002'),
    'appointment_service_url': os.getenv('APPOINTMENT_SERVICE_URL', 'http://localhost:5003'),
    'medical_service_url': os.getenv('MEDICAL_SERVICE_URL', 'http://localhost:5004'),
    'test_timeout': int(os.getenv('TEST_TIMEOUT', '30')),
    'mongodb_test_uri': os.getenv('MONGODB_TEST_URI', 'mongodb://localhost:27017/'),
}

@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def service_urls():
    """Service URLs fixture."""
    return {
        'user': TEST_CONFIG['user_service_url'],
        'pet': TEST_CONFIG['pet_service_url'],
        'appointment': TEST_CONFIG['appointment_service_url'],
        'medical': TEST_CONFIG['medical_service_url'],
        'frontend': TEST_CONFIG['base_url']
    }

@pytest.fixture
def test_user_data():
    """Test user data fixture."""
    timestamp = int(time.time())
    return {
        'name': f'Test User {timestamp}',
        'email': f'testuser_{timestamp}@example.com',
        'password': 'testpassword123',
        'phone': '+1234567890',
        'address': '123 Test Street, Test City'
    }

@pytest.fixture
def test_pet_data():
    """Test pet data fixture."""
    return {
        'name': 'Test Pet',
        'species': 'Dog',
        'breed': 'Golden Retriever',
        'age': 3,
        'gender': 'Male',
        'weight': 25.5,
        'color': 'Golden',
        'microchip_id': 'TEST123456789',
        'notes': 'Test pet for automated testing'
    }

@pytest.fixture
def test_appointment_data():
    """Test appointment data fixture."""
    from datetime import datetime, timedelta
    future_date = datetime.utcnow() + timedelta(days=7)
    return {
        'appointment_type': 'Check-up',
        'appointment_date': future_date.isoformat(),
        'veterinarian': 'Dr. Test',
        'clinic': 'Test Clinic',
        'reason': 'Test appointment',
        'status': 'scheduled'
    }

@pytest.fixture
def test_medical_data():
    """Test medical record data fixture."""
    from datetime import datetime, timedelta
    past_date = datetime.utcnow() - timedelta(days=30)
    return {
        'record_type': 'vaccination',
        'visit_date': past_date.isoformat(),
        'veterinarian': 'Dr. Test',
        'clinic': 'Test Clinic',
        'diagnosis': 'Annual vaccination',
        'treatment': 'Administered vaccines',
        'medications': 'None',
        'weight': 25.5,
        'temperature': 38.5,
        'notes': 'Test medical record'
    }

@pytest.fixture
def authenticated_user(service_urls, test_user_data):
    """Create and authenticate a test user."""
    # Register user
    response = requests.post(
        f"{service_urls['user']}/api/users/register",
        json=test_user_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 201:
        pytest.skip(f"Failed to register test user: {response.text}")
    
    user_id = response.json()['user_id']
    
    # Login user
    login_data = {
        'email': test_user_data['email'],
        'password': test_user_data['password']
    }
    response = requests.post(
        f"{service_urls['user']}/api/users/login",
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        pytest.skip(f"Failed to login test user: {response.text}")
    
    token = response.json()['token']
    
    yield {
        'user_id': user_id,
        'token': token,
        'user_data': test_user_data,
        'headers': {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    }
    
    # Cleanup: Delete user
    try:
        requests.delete(
            f"{service_urls['user']}/api/users/profile",
            headers={'Authorization': f'Bearer {token}'}
        )
    except:
        pass  # Ignore cleanup errors

@pytest.fixture
def test_pet(service_urls, authenticated_user, test_pet_data):
    """Create a test pet."""
    response = requests.post(
        f"{service_urls['pet']}/api/pets/",
        json=test_pet_data,
        headers=authenticated_user['headers']
    )
    
    if response.status_code != 201:
        pytest.skip(f"Failed to create test pet: {response.text}")
    
    pet_id = response.json()['pet_id']
    
    yield {
        'pet_id': pet_id,
        'pet_data': test_pet_data
    }
    
    # Cleanup: Delete pet
    try:
        requests.delete(
            f"{service_urls['pet']}/api/pets/{pet_id}",
            headers=authenticated_user['headers']
        )
    except:
        pass  # Ignore cleanup errors

@pytest.fixture
def test_appointment(service_urls, authenticated_user, test_pet, test_appointment_data):
    """Create a test appointment."""
    appointment_data = test_appointment_data.copy()
    appointment_data['pet_id'] = test_pet['pet_id']
    
    response = requests.post(
        f"{service_urls['appointment']}/api/appointments/",
        json=appointment_data,
        headers=authenticated_user['headers']
    )
    
    if response.status_code != 201:
        pytest.skip(f"Failed to create test appointment: {response.text}")
    
    appointment_id = response.json()['appointment_id']
    
    yield {
        'appointment_id': appointment_id,
        'appointment_data': appointment_data
    }
    
    # Cleanup: Delete appointment
    try:
        requests.delete(
            f"{service_urls['appointment']}/api/appointments/{appointment_id}",
            headers=authenticated_user['headers']
        )
    except:
        pass  # Ignore cleanup errors

@pytest.fixture
def test_medical_record(service_urls, authenticated_user, test_pet, test_medical_data):
    """Create a test medical record."""
    medical_data = test_medical_data.copy()
    medical_data['pet_id'] = test_pet['pet_id']
    
    response = requests.post(
        f"{service_urls['medical']}/api/medical/",
        json=medical_data,
        headers=authenticated_user['headers']
    )
    
    if response.status_code != 201:
        pytest.skip(f"Failed to create test medical record: {response.text}")
    
    record_id = response.json()['record_id']
    
    yield {
        'record_id': record_id,
        'record_data': medical_data
    }
    
    # Cleanup: Delete medical record
    try:
        requests.delete(
            f"{service_urls['medical']}/api/medical/{record_id}",
            headers=authenticated_user['headers']
        )
    except:
        pass  # Ignore cleanup errors

@pytest.fixture(scope="session")
def check_services_health(service_urls):
    """Check that all services are healthy before running tests."""
    services = [
        ('User Service', f"{service_urls['user']}/health"),
        ('Pet Service', f"{service_urls['pet']}/health"),
        ('Appointment Service', f"{service_urls['appointment']}/health"),
        ('Medical Service', f"{service_urls['medical']}/health"),
    ]
    
    unhealthy_services = []
    
    for service_name, health_url in services:
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code != 200:
                unhealthy_services.append(service_name)
        except requests.exceptions.RequestException:
            unhealthy_services.append(service_name)
    
    if unhealthy_services:
        pytest.skip(f"Unhealthy services: {', '.join(unhealthy_services)}")

# Markers for different test types
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.unit)

# Test data cleanup utilities
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test."""
    yield
    # Cleanup logic can be added here if needed
    pass