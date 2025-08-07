import pytest
import requests
import json
import time
from datetime import datetime, timedelta

# Base URLs for services (adjust based on your deployment)
BASE_URL = "http://localhost"
FRONTEND_URL = f"{BASE_URL}:3000"
USER_SERVICE_URL = f"{BASE_URL}:5001"
PET_SERVICE_URL = f"{BASE_URL}:5002"
APPOINTMENT_SERVICE_URL = f"{BASE_URL}:5003"
MEDICAL_SERVICE_URL = f"{BASE_URL}:5004"

class TestIntegration:
    """Integration tests for PetPal services."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.test_user = {
            'name': 'Integration Test User',
            'email': f'integrationtest_{int(time.time())}@example.com',
            'password': 'testpass123',
            'phone': '+1234567890',
            'address': '123 Test Street, Test City'
        }
        self.token = None
        self.user_id = None
        self.pet_id = None
        self.appointment_id = None
        self.medical_record_id = None

    def test_service_health_checks(self):
        """Test that all services are healthy."""
        services = [
            (USER_SERVICE_URL, 'user-service'),
            (PET_SERVICE_URL, 'pet-service'),
            (APPOINTMENT_SERVICE_URL, 'appointment-service'),
            (MEDICAL_SERVICE_URL, 'medical-service')
        ]
        
        for url, service_name in services:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                assert response.status_code == 200
                data = response.json()
                assert data['status'] == 'healthy'
                assert data['service'] == service_name
            except requests.exceptions.RequestException:
                pytest.fail(f"{service_name} is not responding")

    def test_user_registration_and_login_flow(self):
        """Test complete user registration and login flow."""
        # Test user registration
        response = requests.post(
            f"{USER_SERVICE_URL}/api/users/register",
            json=self.test_user,
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 201
        data = response.json()
        assert 'user_id' in data
        self.user_id = data['user_id']
        
        # Test user login
        login_data = {
            'email': self.test_user['email'],
            'password': self.test_user['password']
        }
        response = requests.post(
            f"{USER_SERVICE_URL}/api/users/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert 'user' in data
        self.token = data['token']
        
        # Test token verification
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{USER_SERVICE_URL}/api/users/verify-token",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True

    def test_pet_management_flow(self):
        """Test complete pet management flow."""
        if not self.token:
            self.test_user_registration_and_login_flow()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Create a pet
        pet_data = {
            'name': 'Integration Test Pet',
            'species': 'Dog',
            'breed': 'Golden Retriever',
            'age': 3,
            'gender': 'Male',
            'weight': 25.5,
            'color': 'Golden',
            'microchip_id': 'INT123456789',
            'notes': 'Integration test pet'
        }
        response = requests.post(
            f"{PET_SERVICE_URL}/api/pets/",
            json=pet_data,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert 'pet_id' in data
        self.pet_id = data['pet_id']
        
        # Get all pets
        response = requests.get(
            f"{PET_SERVICE_URL}/api/pets/",
            headers=headers
        )
        assert response.status_code == 200
        pets = response.json()
        assert len(pets) == 1
        assert pets[0]['name'] == 'Integration Test Pet'
        
        # Get specific pet
        response = requests.get(
            f"{PET_SERVICE_URL}/api/pets/{self.pet_id}",
            headers=headers
        )
        assert response.status_code == 200
        pet = response.json()
        assert pet['name'] == 'Integration Test Pet'
        
        # Update pet
        update_data = {
            'age': 4,
            'weight': 26.0,
            'notes': 'Updated integration test pet'
        }
        response = requests.put(
            f"{PET_SERVICE_URL}/api/pets/{self.pet_id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200

    def test_appointment_management_flow(self):
        """Test complete appointment management flow."""
        if not self.token or not self.pet_id:
            self.test_pet_management_flow()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Create an appointment
        future_date = datetime.utcnow() + timedelta(days=7)
        appointment_data = {
            'pet_id': self.pet_id,
            'appointment_type': 'Check-up',
            'appointment_date': future_date.isoformat(),
            'veterinarian': 'Dr. Integration Test',
            'clinic': 'Integration Test Clinic',
            'reason': 'Integration test appointment',
            'status': 'scheduled'
        }
        response = requests.post(
            f"{APPOINTMENT_SERVICE_URL}/api/appointments/",
            json=appointment_data,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert 'appointment_id' in data
        self.appointment_id = data['appointment_id']
        
        # Get all appointments
        response = requests.get(
            f"{APPOINTMENT_SERVICE_URL}/api/appointments/",
            headers=headers
        )
        assert response.status_code == 200
        appointments = response.json()
        assert len(appointments) == 1
        
        # Get upcoming appointments
        response = requests.get(
            f"{APPOINTMENT_SERVICE_URL}/api/appointments/upcoming",
            headers=headers
        )
        assert response.status_code == 200
        upcoming = response.json()
        assert len(upcoming) == 1
        
        # Update appointment
        update_data = {
            'status': 'confirmed',
            'reason': 'Updated integration test appointment'
        }
        response = requests.put(
            f"{APPOINTMENT_SERVICE_URL}/api/appointments/{self.appointment_id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200

    def test_medical_records_flow(self):
        """Test complete medical records management flow."""
        if not self.token or not self.pet_id:
            self.test_pet_management_flow()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Create a medical record
        visit_date = datetime.utcnow() - timedelta(days=30)
        medical_data = {
            'pet_id': self.pet_id,
            'record_type': 'vaccination',
            'visit_date': visit_date.isoformat(),
            'veterinarian': 'Dr. Integration Test',
            'clinic': 'Integration Test Clinic',
            'diagnosis': 'Annual vaccination - Integration test',
            'treatment': 'Administered vaccinations',
            'medications': 'None',
            'weight': 25.5,
            'temperature': 38.5,
            'notes': 'Integration test medical record'
        }
        response = requests.post(
            f"{MEDICAL_SERVICE_URL}/api/medical/",
            json=medical_data,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert 'record_id' in data
        self.medical_record_id = data['record_id']
        
        # Get all medical records
        response = requests.get(
            f"{MEDICAL_SERVICE_URL}/api/medical/",
            headers=headers
        )
        assert response.status_code == 200
        records = response.json()
        assert len(records) == 1
        
        # Get recent medical records
        response = requests.get(
            f"{MEDICAL_SERVICE_URL}/api/medical/recent?limit=5",
            headers=headers
        )
        assert response.status_code == 200
        recent = response.json()
        assert len(recent) == 1
        
        # Get medical records by pet
        response = requests.get(
            f"{MEDICAL_SERVICE_URL}/api/medical/pet/{self.pet_id}",
            headers=headers
        )
        assert response.status_code == 200
        pet_records = response.json()
        assert len(pet_records) == 1
        
        # Update medical record
        update_data = {
            'notes': 'Updated integration test medical record',
            'treatment': 'Updated treatment plan'
        }
        response = requests.put(
            f"{MEDICAL_SERVICE_URL}/api/medical/{self.medical_record_id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200

    def test_service_communication(self):
        """Test inter-service communication."""
        if not self.token or not self.pet_id:
            self.test_pet_management_flow()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Test pet ownership verification (used by other services)
        response = requests.get(
            f"{PET_SERVICE_URL}/api/pets/verify/{self.pet_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True
        assert 'pet' in data

    def test_frontend_accessibility(self):
        """Test that frontend is accessible."""
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            assert response.status_code == 200
            assert 'PetPal' in response.text
        except requests.exceptions.RequestException:
            pytest.fail("Frontend is not accessible")

    def test_error_handling(self):
        """Test error handling across services."""
        if not self.token:
            self.test_user_registration_and_login_flow()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Test accessing non-existent pet
        response = requests.get(
            f"{PET_SERVICE_URL}/api/pets/nonexistent_id",
            headers=headers
        )
        assert response.status_code == 404
        
        # Test accessing non-existent appointment
        response = requests.get(
            f"{APPOINTMENT_SERVICE_URL}/api/appointments/nonexistent_id",
            headers=headers
        )
        assert response.status_code == 404
        
        # Test accessing non-existent medical record
        response = requests.get(
            f"{MEDICAL_SERVICE_URL}/api/medical/nonexistent_id",
            headers=headers
        )
        assert response.status_code == 404

    def test_authentication_flow(self):
        """Test authentication across all services."""
        # Test accessing protected endpoints without token
        services_endpoints = [
            f"{PET_SERVICE_URL}/api/pets/",
            f"{APPOINTMENT_SERVICE_URL}/api/appointments/",
            f"{MEDICAL_SERVICE_URL}/api/medical/"
        ]
        
        for endpoint in services_endpoints:
            response = requests.get(endpoint)
            assert response.status_code == 401

    def teardown_method(self):
        """Clean up test data."""
        if not self.token:
            return
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Clean up in reverse order of dependencies
        if self.medical_record_id:
            requests.delete(
                f"{MEDICAL_SERVICE_URL}/api/medical/{self.medical_record_id}",
                headers=headers
            )
        
        if self.appointment_id:
            requests.delete(
                f"{APPOINTMENT_SERVICE_URL}/api/appointments/{self.appointment_id}",
                headers=headers
            )
        
        if self.pet_id:
            requests.delete(
                f"{PET_SERVICE_URL}/api/pets/{self.pet_id}",
                headers=headers
            )
        
        if self.user_id:
            requests.delete(
                f"{USER_SERVICE_URL}/api/users/profile",
                headers=headers
            )