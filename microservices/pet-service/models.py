from datetime import datetime
from bson import ObjectId
import jwt
import os

class Pet:
    def __init__(self, db):
        self.collection = db.pets
    
    def create_pet(self, pet_data):
        pet_data['created_at'] = datetime.utcnow()
        pet_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.insert_one(pet_data)
        return str(result.inserted_id)
    
    def get_pets_by_owner(self, owner_id):
        pets = list(self.collection.find({'owner_id': owner_id}))
        for pet in pets:
            pet['_id'] = str(pet['_id'])
        return pets
    
    def get_pet_by_id(self, pet_id):
        pet = self.collection.find_one({'_id': ObjectId(pet_id)})
        if pet:
            pet['_id'] = str(pet['_id'])
        return pet
    
    def update_pet(self, pet_id, owner_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(pet_id), 'owner_id': owner_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_pet(self, pet_id, owner_id):
        result = self.collection.delete_one({'_id': ObjectId(pet_id), 'owner_id': owner_id})
        return result.deleted_count > 0
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'petpal-secret-key-2024'), algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
