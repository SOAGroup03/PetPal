from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId

class PetModel:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME', 'petpal_pets')]
        self.collection = self.db.pets
        
        # Create index for user_id
        self.collection.create_index("user_id")
    
    def create_pet(self, pet_data):
        """Create a new pet"""
        pet_data['created_at'] = datetime.utcnow()
        pet_data['updated_at'] = datetime.utcnow()
        
        try:
            result = self.collection.insert_one(pet_data)
            return str(result.inserted_id)
        except Exception as e:
            return None
    
    def get_pets_by_user(self, user_id):
        """Get all pets for a user"""
        pets = list(self.collection.find({'user_id': user_id}))
        for pet in pets:
            pet['_id'] = str(pet['_id'])
        return pets
    
    def get_pet_by_id(self, pet_id):
        """Get pet by ID"""
        try:
            pet = self.collection.find_one({'_id': ObjectId(pet_id)})
            if pet:
                pet['_id'] = str(pet['_id'])
            return pet
        except:
            return None
    
    def update_pet(self, pet_id, update_data):
        """Update pet information"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(pet_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_pet(self, pet_id):
        """Delete a pet"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(pet_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def get_pet_by_id_and_user(self, pet_id, user_id):
        """Get pet by ID and verify ownership"""
        try:
            pet = self.collection.find_one({
                '_id': ObjectId(pet_id),
                'user_id': user_id
            })
            if pet:
                pet['_id'] = str(pet['_id'])
            return pet
        except:
            return None