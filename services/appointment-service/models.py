from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId

class AppointmentModel:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME', 'petpal_appointments')]
        self.collection = self.db.appointments
        
        # Create indexes
        self.collection.create_index("user_id")
        self.collection.create_index("pet_id")
        self.collection.create_index("appointment_date")
    
    def create_appointment(self, appointment_data):
        """Create a new appointment"""
        appointment_data['created_at'] = datetime.utcnow()
        appointment_data['updated_at'] = datetime.utcnow()
        appointment_data['status'] = appointment_data.get('status', 'scheduled')
        
        try:
            result = self.collection.insert_one(appointment_data)
            return str(result.inserted_id)
        except Exception as e:
            return None
    
    def get_appointments_by_user(self, user_id):
        """Get all appointments for a user"""
        appointments = list(self.collection.find({'user_id': user_id}).sort('appointment_date', -1))
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
        return appointments
    
    def get_appointments_by_pet(self, pet_id):
        """Get all appointments for a pet"""
        appointments = list(self.collection.find({'pet_id': pet_id}).sort('appointment_date', -1))
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
        return appointments
    
    def get_appointment_by_id(self, appointment_id):
        """Get appointment by ID"""
        try:
            appointment = self.collection.find_one({'_id': ObjectId(appointment_id)})
            if appointment:
                appointment['_id'] = str(appointment['_id'])
            return appointment
        except:
            return None
    
    def update_appointment(self, appointment_id, update_data):
        """Update appointment information"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(appointment_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_appointment(self, appointment_id):
        """Delete an appointment"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(appointment_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def get_appointment_by_id_and_user(self, appointment_id, user_id):
        """Get appointment by ID and verify ownership"""
        try:
            appointment = self.collection.find_one({
                '_id': ObjectId(appointment_id),
                'user_id': user_id
            })
            if appointment:
                appointment['_id'] = str(appointment['_id'])
            return appointment
        except:
            return None
    
    def get_upcoming_appointments(self, user_id):
        """Get upcoming appointments for a user"""
        current_date = datetime.utcnow()
        appointments = list(self.collection.find({
            'user_id': user_id,
            'appointment_date': {'$gte': current_date},
            'status': {'$in': ['scheduled', 'confirmed']}
        }).sort('appointment_date', 1))
        
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
        return appointments