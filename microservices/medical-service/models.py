from datetime import datetime
from bson import ObjectId
import jwt
import os

class MedicalHistory:
    def __init__(self, db):
        self.collection = db.medical_history
    
    def create_medical_record(self, medical_data):
        medical_data['created_at'] = datetime.utcnow()
        medical_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.insert_one(medical_data)
        return str(result.inserted_id)
    
    def get_medical_history_by_pet(self, pet_id, user_id):
        records = list(self.collection.find({'pet_id': pet_id, 'user_id': user_id}).sort('visit_date', -1))
        for record in records:
            record['_id'] = str(record['_id'])
        return records
    
    def get_medical_record_by_id(self, record_id):
        record = self.collection.find_one({'_id': ObjectId(record_id)})
        if record:
            record['_id'] = str(record['_id'])
        return record
    
    def update_medical_record(self, record_id, user_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(record_id), 'user_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_medical_record(self, record_id, user_id):
        result = self.collection.delete_one({'_id': ObjectId(record_id), 'user_id': user_id})
        return result.deleted_count > 0
    
    def get_all_medical_records_by_user(self, user_id):
        records = list(self.collection.find({'user_id': user_id}).sort('visit_date', -1))
        for record in records:
            record['_id'] = str(record['_id'])
        return records
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'petpal-secret-key-2024'), algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None