import pytest
import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE_URL = "http://localhost:5000/api"

class TestE2EUserJourney:
    """End-to-end tests for complete user journeys."""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Set up Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    @pytest.fixture(autouse=True)
    def wait_for_services(self):
        """Wait for all services to be ready before running tests."""
        services = [
            "http://localhost:5001/health",  # user-service
            "http://localhost:5002/health",  # pet-service
            "http://localhost:5003/health",  # appointment-service
            "http://localhost:5004/health",  # medical-service
            "http://localhost:5000/health"   # frontend
        ]
        
        for service in services:
            for _ in range(30):  # Wait up to 30 seconds per service
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        break
                except:
                    pass
                time.sleep(1)
            else:
                pytest.fail(f"Service {service} is not ready")
    
    def test_complete_user_registration_and_login(self, driver):
        """Test complete user registration and login flow."""
        # Navigate to homepage
        driver.get(BASE_URL)
        assert "PetPal" in driver.title
        
        # Click on register link
        register_link = driver.find_element(By.LINK_TEXT, "Register")
        register_link.click()
        
        # Fill out registration form
        driver.find_element(By.ID, "firstName").send_keys("John")
        driver.find_element(By.ID, "lastName").send_keys("Doe")
        driver.find_element(By.ID, "username").send_keys(f"testuser_{int(time.time())}")
        driver.find_element(By.ID, "email").send_keys(f"test_{int(time.time())}@example.com")
        driver.find_element(By.ID, "phone").send_keys("123-456-7890")
        driver.find_element(By.ID, "password").send_keys("testpass123")
        driver.find_element(By.ID, "confirmPassword").send_keys("testpass123")
        driver.find_element(By.ID, "agreeTerms").click()
        
        # Submit registration
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        # Navigate to login page
        driver.get(f"{BASE_URL}/login")
        
        # Fill out login form
        driver.find_element(By.ID, "email").send_keys(f"test_{int(time.time())}@example.com")
        driver.find_element(By.ID, "password").send_keys("testpass123")
        
        # Submit login
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        # Verify we're on the dashboard
        assert "/dashboard" in driver.current_url
        assert "Welcome back" in driver.page_source
    
    def test_pet_management_flow(self, driver):
        """Test complete pet management flow."""
        # First, we need to be logged in
        self._login_test_user(driver)
        
        # Navigate to pets page
        driver.get(f"{BASE_URL}/pets")
        
        # Click add new pet button
        add_pet_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add New Pet')]")
        add_pet_btn.click()
        
        # Wait for modal to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "petModal"))
        )
        
        # Fill out pet form
        driver.find_element(By.ID, "petName").send_keys("Buddy")
        driver.find_element(By.ID, "petSpecies").send_keys("Dog")
        driver.find_element(By.ID, "petBreed").send_keys("Golden Retriever")
        driver.find_element(By.ID, "petAge").send_keys("3")
        driver.find_element(By.ID, "petWeight").send_keys("65")
        driver.find_element(By.ID, "petGender").send_keys("Male")
        driver.find_element(By.ID, "petColor").send_keys("Golden")
        
        # Submit pet form
        driver.find_element(By.CSS_SELECTOR, "#petModal button[type='submit']").click()
        
        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        # Verify pet appears in the list
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h5[contains(text(), 'Buddy')]"))
        )
        
        # Click on the pet to view details
        pet_card = driver.find_element(By.XPATH, "//h5[contains(text(), 'Buddy')]/..")
        pet_card.click()
        
        # Wait for detail modal
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "petDetailModal"))
        )
        
        # Verify pet details
        assert "Buddy" in driver.page_source
        assert "Golden Retriever" in driver.page_source
    
    def test_appointment_scheduling_flow(self, driver):
        """Test appointment scheduling flow."""
        # Login and ensure we have a pet
        self._login_test_user(driver)
        self._ensure_test_pet_exists()
        
        # Navigate to appointments page
        driver.get(f"{BASE_URL}/appointments")
        
        # Add appointment logic would go here
        # This is a simplified version
        assert "Appointments" in driver.title or "Appointments" in driver.page_source
    
    def _login_test_user(self, driver):
        """Helper method to log in a test user."""
        # Create test user via API first
        test_user = {
            "username": "e2e_test_user",
            "email": "e2e_test@example.com",
            "password": "testpass123",
            "first_name": "E2E",
            "last_name": "Test"
        }
        
        # Try to register (ignore if already exists)
        try:
            requests.post(f"{API_BASE_URL}/auth/register", json=test_user)
        except:
            pass
        
        # Login via web interface
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.ID, "email").send_keys("e2e_test@example.com")
        driver.find_element(By.ID, "password").send_keys("testpass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
    
    def _ensure_test_pet_exists(self):
        """Helper method to ensure a test pet exists."""
        # Login to get token
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": "e2e_test@example.com",
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Check if pet already exists
            pets_response = requests.get(f"{API_BASE_URL}/pets", headers=headers)
            if pets_response.status_code == 200 and len(pets_response.json()) == 0:
                # Create test pet
                test_pet = {
                    "name": "E2E Test Pet",
                    "species": "Dog",
                    "breed": "Test Breed",
                    "age": 5,
                    "weight": 50
                }
                requests.post(f"{API_BASE_URL}/pets", json=test_pet, headers=headers)

class TestAPIEndpoints:
    """Test API endpoints directly."""
    
    def test_health_endpoints(self):
        """Test health endpoints for all services."""
        endpoints = [
            f"{BASE_URL}/health",
            "http://localhost:5001/health",
            "http://localhost:5002/health", 
            "http://localhost:5003/health",
            "http://localhost:5004/health"
        ]
        
        for endpoint in endpoints:
            response = requests.get(endpoint, timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    def test_user_registration_api(self):
        """Test user registration API."""
        test_user = {
            "username": f"api_test_user_{int(time.time())}",
            "email": f"api_test_{int(time.time())}@example.com",
            "password": "testpass123",
            "first_name": "API",
            "last_name": "Test"
        }
        
        response = requests.post(f"{API_BASE_URL}/auth/register", json=test_user)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert "user_id" in data
    
    def test_user_login_api(self):
        """Test user login API."""
        # First register a user
        test_user = {
            "username": f"login_test_user_{int(time.time())}",
            "email": f"login_test_{int(time.time())}@example.com",
            "password": "testpass123",
            "first_name": "Login",
            "last_name": "Test"
        }
        
        # Register
        register_response = requests.post(f"{API_BASE_URL}/auth/register", json=test_user)
        assert register_response.status_code == 201
        
        # Login
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        assert login_response.status_code == 200
        data = login_response.json()
        assert data["message"] == "Login successful"
        assert "token" in data
        assert "user" in data
    
    def test_pet_crud_operations(self):
        """Test CRUD operations for pets."""
        # First login to get token
        test_user = {
            "username": f"pet_test_user_{int(time.time())}",
            "email": f"pet_test_{int(time.time())}@example.com",
            "password": "testpass123",
            "first_name": "Pet",
            "last_name": "Test"
        }
        
        # Register and login
        requests.post(f"{API_BASE_URL}/auth/register", json=test_user)
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create pet
        test_pet = {
            "name": "API Test Pet",
            "species": "Cat",
            "breed": "Persian",
            "age": 2,
            "weight": 10
        }
        
        create_response = requests.post(f"{API_BASE_URL}/pets", json=test_pet, headers=headers)
        assert create_response.status_code == 201
        pet_id = create_response.json()["pet_id"]
        
        # Read pet
        get_response = requests.get(f"{API_BASE_URL}/pets/{pet_id}", headers=headers)
        assert get_response.status_code == 200
        pet_data = get_response.json()
        assert pet_data["name"] == "API Test Pet"
        
        # Update pet
        update_data = {"name": "Updated Pet Name"}
        update_response = requests.put(f"{API_BASE_URL}/pets/{pet_id}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        # Verify update
        get_updated_response = requests.get(f"{API_BASE_URL}/pets/{pet_id}", headers=headers)
        updated_pet = get_updated_response.json()
        assert updated_pet["name"] == "Updated Pet Name"
        
        # Delete pet
        delete_response = requests.delete(f"{API_BASE_URL}/pets/{pet_id}", headers=headers)
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_deleted_response = requests.get(f"{API_BASE_URL}/pets/{pet_id}", headers=headers)
        assert get_deleted_response.status_code == 404

class TestPerformanceAndLoad:
    """Basic performance and load tests."""
    
    def test_concurrent_health_checks(self):
        """Test concurrent health check requests."""
        import concurrent.futures
        import threading
        
        def make_request():
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        # Make 20 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # At least 80% should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"Success rate {success_rate} is below 80%"
    
    def test_response_time_baseline(self):
        """Test baseline response times."""
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 2.0, f"Response time {response_time}s exceeds 2s threshold"
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])