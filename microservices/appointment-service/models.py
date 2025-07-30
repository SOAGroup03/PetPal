from datetime import datetime
from bson import ObjectId
import jwt
import os

class Appointment:
    def __init__(self, db):
        self.collection = db.appointments
    
    def create_appointment(self, appointment_data):
        appointment_data['created_at'] = datetime.utcnow()
        appointment_data['updated_at'] = datetime.utcnow()
        appointment_data['status'] = 'scheduled'  # Default status
        
        result = self.collection.insert_one(appointment_data)
        return str(result.inserted_id)
    
    def get_appointments_by_user(self, user_id):
        appointments = list(self.collection.find({'user_id': user_id}))
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
        return appointments
    
    def get_appointment_by_id(self, appointment_id):
        appointment = self.collection.find_one({'_id': ObjectId(appointment_id)})
        if appointment:
            appointment['_id'] = str(appointment['_id'])
        return appointment
    
    def update_appointment(self, appointment_id, user_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(appointment_id), 'user_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_appointment(self, appointment_id, user_id):
        result = self.collection.delete_one({'_id': ObjectId(appointment_id), 'user_id': user_id})
        return result.deleted_count > 0
    
    def get_appointments_by_pet(self, pet_id, user_id):
        appointments = list(self.collection.find({'pet_id': pet_id, 'user_id': user_id}))
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
        return appointments
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY', 'petpal-secret-key-2024'), algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None