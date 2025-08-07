import os

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://acsujan69:petpal123@petpal.9k6d9qu.mongodb.net/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'petpal_appointments')
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5001')
    PET_SERVICE_URL = os.getenv('PET_SERVICE_URL', 'http://localhost:5002')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')