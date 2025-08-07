from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId

class MedicalModel:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME', 'petpal_medical')]
        self.collection = self.db.medical_records
        
        # Create indexes
        self.collection.create_index("user_id")
        self.collection.create_index("pet_id")
        self.collection.create_index("visit_date")
        self.collection.create_index("record_type")
    
    def create_medical_record(self, medical_data):
        """Create a new medical record"""
        medical_data['created_at'] = datetime.utcnow()
        medical_data['updated_at'] = datetime.utcnow()
        
        try:
            result = self.collection.insert_one(medical_data)
            return str(result.inserted_id)
        except Exception as e:
            return None
    
    def get_medical_records_by_user(self, user_id):
        """Get all medical records for a user"""
        records = list(self.collection.find({'user_id': user_id}).sort('visit_date', -1))
        for record in records:
            record['_id'] = str(record['_id'])
        return records
    
    def get_medical_records_by_pet(self, pet_id):
        """Get all medical records for a pet"""
        records = list(self.collection.find({'pet_id': pet_id}).sort('visit_date', -1))
        for record in records:
            record['_id'] = str(record['_id'])
        return records
    
    def get_medical_record_by_id(self, record_id):
        """Get medical record by ID"""
        try:
            record = self.collection.find_one({'_id': ObjectId(record_id)})
            if record:
                record['_id'] = str(record['_id'])
            return record
        except:
            return None
    
    def update_medical_record(self, record_id, update_data):
        """Update medical record information"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(record_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            return False
    
    def delete_medical_record(self, record_id):
        """Delete a medical record"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(record_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def get_medical_record_by_id_and_user(self, record_id, user_id):
        """Get medical record by ID and verify ownership"""
        try:
            record = self.collection.find_one({
                '_id': ObjectId(record_id),
                'user_id': user_id
            })
            if record:
                record['_id'] = str(record['_id'])
            return record
        except:
            return None
    
    def get_records_by_type(self, pet_id, record_type):
        """Get medical records by type for a specific pet"""
        records = list(self.collection.find({
            'pet_id': pet_id,
            'record_type': record_type
        }).sort('visit_date', -1))
        
        for record in records:
            record['_id'] = str(record['_id'])
        return records
    
    def get_vaccination_history(self, pet_id):
        """Get vaccination history for a pet"""
        return self.get_records_by_type(pet_id, 'vaccination')
    
    def get_recent_records(self, user_id, limit=10):
        """Get recent medical records for a user"""
        records = list(self.collection.find({'user_id': user_id})
                      .sort('visit_date', -1)
                      .limit(limit))
        
        for record in records:
            record['_id'] = str(record['_id'])
        return records