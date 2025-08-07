from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from bson import ObjectId

class UserModel:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME', 'petpal_users')]
        self.collection = self.db.users
        
        # Create index for email uniqueness
        self.collection.create_index("email", unique=True)
    
    def create_user(self, user_data):
        """Create a new user"""
        user_data['password'] = generate_password_hash(user_data['password'])
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        
        try:
            result = self.collection.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        user = self.collection.find_one({'email': email})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except:
            return None
    
    def update_user(self, user_id, update_data):
        """Update user information"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_user(self, user_id):
        """Delete a user"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def verify_password(self, email, password):
        """Verify user password"""
        user = self.get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            return user
        return None
    
    def get_all_users(self):
        """Get all users (admin function)"""
        users = list(self.collection.find({}, {'password': 0}))
        for user in users:
            user['_id'] = str(user['_id'])
        return users