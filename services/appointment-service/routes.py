from flask import Blueprint, request, jsonify
import requests
import os
from datetime import datetime
from models import AppointmentModel
from functools import wraps

appointment_bp = Blueprint('appointment', __name__)
appointment_model = AppointmentModel()

def verify_token(token):
    """Verify token with user service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(
            f"{os.getenv('USER_SERVICE_URL')}/api/users/verify-token",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def verify_pet_ownership(pet_id, token):
    """Verify pet ownership with pet service"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f"{os.getenv('PET_SERVICE_URL')}/api/pets/verify/{pet_id}",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_data = verify_token(token)
        if not user_data or not user_data.get('valid'):
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(user_data['user'], token, *args, **kwargs)
    return decorated

@appointment_bp.route('/', methods=['POST'])
@token_required
def create_appointment(current_user, token):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['pet_id', 'appointment_date', 'appointment_type', 'veterinarian']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Verify pet ownership
        pet_verification = verify_pet_ownership(data['pet_id'], token)
        if not pet_verification or not pet_verification.get('valid'):
            return jsonify({'message': 'Pet not found or access denied'}), 404
        
        # Parse appointment date
        try:
            appointment_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00'))
            data['appointment_date'] = appointment_date
        except:
            return jsonify({'message': 'Invalid appointment date format'}), 400
        
        # Add user_id to appointment data
        data['user_id'] = current_user['id']
        
        # Create appointment
        appointment_id = appointment_model.create_appointment(data)
        if appointment_id:
            return jsonify({
                'message': 'Appointment created successfully',
                'appointment_id': appointment_id
            }), 201
        else:
            return jsonify({'message': 'Failed to create appointment'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@appointment_bp.route('/', methods=['GET'])
@token_required
def get_appointments(current_user, token):
    try:
        appointments = appointment_model.get_appointments_by_user(current_user['id'])
        
        # Convert datetime objects to ISO strings
        for appointment in appointments:
            if 'appointment_date' in appointment:
                appointment['appointment_date'] = appointment['appointment_date'].isoformat()
            if 'created_at' in appointment:
                appointment['created_at'] = appointment['created_at'].isoformat()
            if 'updated_at' in appointment:
                appointment['updated_at'] = appointment['updated_at'].isoformat()
        
        return jsonify(appointments), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@appointment_bp.route('/upcoming', methods=['GET'])
@token_required
def get_upcoming_appointments(current_user, token):
    try:
        appointments = appointment_model.get_upcoming_appointments(current_user['id'])
        
        # Convert datetime objects to ISO strings
        for appointment in appointments:
            if 'appointment_date' in appointment:
                appointment['appointment_date'] = appointment['appointment_date'].isoformat()
            if 'created_at' in appointment:
                appointment['created_at'] = appointment['created_at'].isoformat()
            if 'updated_at' in appointment:
                appointment['updated_at'] = appointment['updated_at'].isoformat()
        
        return jsonify(appointments), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@appointment_bp.route('/<appointment_id>', methods=['GET'])
@token_required
def get_appointment(current_user, token, appointment_id):
    try:
        appointment = appointment_model.get_appointment_by_id_and_user(appointment_id, current_user['id'])
        if appointment:
            # Convert datetime objects to ISO strings
            if 'appointment_date' in appointment:
                appointment['appointment_date'] = appointment['appointment_date'].isoformat()
            if 'created_at' in appointment:
                appointment['created_at'] = appointment['created_at'].isoformat()
            if 'updated_at' in appointment:
                appointment['updated_at'] = appointment['updated_at'].isoformat()
            
            return jsonify(appointment), 200
        else:
            return jsonify({'message': 'Appointment not found'}), 404
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@appointment_bp.route('/<appointment_id>', methods=['PUT'])
@token_required
def update_appointment(current_user, token, appointment_id):
    try:
        # Verify appointment ownership
        appointment = appointment_model.get_appointment_by_id_and_user(appointment_id, current_user['id'])
        if not appointment:
            return jsonify({'message': 'Appointment not found'}), 404
        
        data = request.get_json()
        
        # Handle appointment date update
        if 'appointment_date' in data:
            try:
                appointment_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00'))
                data['appointment_date'] = appointment_date
            except:
                return jsonify({'message': 'Invalid appointment date format'}), 400
        
        # Remove fields that shouldn't be updated
        forbidden_fields = ['_id', 'user_id', 'created_at']
        for field in forbidden_fields:
            data.pop(field, None)
        
        if appointment_model.update_appointment(appointment_id, data):
            return jsonify({'message': 'Appointment updated successfully'}), 200
        else:
            return jsonify({'message': 'Failed to update appointment'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@appointment_bp.route('/<appointment_id>', methods=['DELETE'])
@token_required
def delete_appointment(current_user, token, appointment_id):
    try:
        # Verify appointment ownership
        appointment = appointment_model.get_appointment_by_id_and_user(appointment_id, current_user['id'])
        if not appointment:
            return jsonify({'message': 'Appointment not found'}), 404
        
        if appointment_model.delete_appointment(appointment_id):
            return jsonify({'message': 'Appointment deleted successfully'}), 200
        else:
            return jsonify({'message': 'Failed to delete appointment'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@appointment_bp.route('/pet/<pet_id>', methods=['GET'])
@token_required
def get_appointments_by_pet(current_user, token, pet_id):
    try:
        # Verify pet ownership
        pet_verification = verify_pet_ownership(pet_id, token)
        if not pet_verification or not pet_verification.get('valid'):
            return jsonify({'message': 'Pet not found or access denied'}), 404
        
        appointments = appointment_model.get_appointments_by_pet(pet_id)
        
        # Convert datetime objects to ISO strings
        for appointment in appointments:
            if 'appointment_date' in appointment:
                appointment['appointment_date'] = appointment['appointment_date'].isoformat()
            if 'created_at' in appointment:
                appointment['created_at'] = appointment['created_at'].isoformat()
            if 'updated_at' in appointment:
                appointment['updated_at'] = appointment['updated_at'].isoformat()
        
        return jsonify(appointments), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500