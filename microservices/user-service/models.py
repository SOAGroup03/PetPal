from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import jwt
import os

class User:
    def __init__(self, db):
        self.collection = db.users
    
    def create_user(self, user_data):
        user_data['password'] = generate_password_hash(user_data['password'])
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_email(self, email):
        return self.collection.find_one({'email': email})
    
    def get_user_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def update_user(self, user_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_user(self, user_id):
        result = self.collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0
    
    def verify_password(self, user, password):
        return check_password_hash(user['password'], password)
    
    def generate_token(self, user_id):
        payload = {
            'user_id': str(user_id),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, os.environ.get('SECRET_KEY', 'petpal-secret-key-2024'), algorithm='HS256')
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'petpal-secret-key-2024'), algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None