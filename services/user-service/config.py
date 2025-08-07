import os

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://acsujan69:petpal123@petpal.9k6d9qu.mongodb.net/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'petpal_users')
    JWT_SECRET = os.getenv('JWT_SECRET', 'your_jwt_secret_key_here')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')