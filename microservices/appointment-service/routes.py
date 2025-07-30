from flask import Blueprint, request, jsonify, current_app
from models import Appointment
from functools import wraps
from datetime import datetime

appointment_bp = Blueprint('appointments', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            appointment_model = Appointment(current_app.db)
            user_id = appointment_model.verify_token(token)
            if not user_id:
                return jsonify({'message': 'Token is invalid!'}), 401
            request.current_user_id = user_id
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    return decorated

@appointment_bp.route('/', methods=['POST'])
@token_required
def create_appointment():
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['pet_id', 'appointment_date', 'appointment_time', 'vet_name', 'reason']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate date and time format
        try:
            datetime.strptime(data['appointment_date'], '%Y-%m-%d')
            datetime.strptime(data['appointment_time'], '%H:%M')
        except ValueError:
            return jsonify({'message': 'Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time'}), 400
        
        # Check if appointment is in the future
        appointment_datetime = datetime.strptime(f"{data['appointment_date']} {data['appointment_time']}", '%Y-%m-%d %H:%M')
        if appointment_datetime <= datetime.now():
            return jsonify({'message': 'Appointment must be scheduled for future date/time'}), 400
        
        # Add user ID
        data['user_id'] = request.current_user_id
        
        appointment_model = Appointment(current_app.db)
        appointment_id = appointment_model.create_appointment(data)
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment_id': appointment_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@appointment_bp.route('/', methods=['GET'])
@token_required
def get_appointments():
    try:
        appointment_model = Appointment(current_app.db)
        appointments = appointment_model.get_appointments_by_user(request.current_user_id)
        
        return jsonify({'appointments': appointments}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@appointment_bp.route('/<appointment_id>', methods=['GET'])
@token_required
def get_appointment(appointment_id):
    try:
        appointment_model = Appointment(current_app.db)
        appointment = appointment_model.get_appointment_by_id(appointment_id)
        
        if not appointment:
            return jsonify({'message': 'Appointment not found'}), 404
        
        # Check if user owns this appointment
        if appointment['user_id'] != request.current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify({'appointment': appointment}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@appointment_bp.route('/pet/<pet_id>', methods=['GET'])
@token_required
def get_appointments_by_pet(pet_id):
    try:
        appointment_model = Appointment(current_app.db)
        appointments = appointment_model.get_appointments_by_pet(pet_id, request.current_user_id)
        
        return jsonify({'appointments': appointments}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@appointment_bp.route('/<appointment_id>', methods=['PUT'])
@token_required
def update_appointment(appointment_id):
    try:
        data = request.get_json()
        
        # Validate date and time format if provided
        if 'appointment_date' in data:
            try:
                datetime.strptime(data['appointment_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if 'appointment_time' in data:
            try:
                datetime.strptime(data['appointment_time'], '%H:%M')
            except ValueError:
                return jsonify({'message': 'Invalid time format. Use HH:MM'}), 400
        
        # Validate status if provided
        if 'status' in data and data['status'] not in ['scheduled', 'confirmed', 'completed', 'cancelled']:
            return jsonify({'message': 'Invalid status. Must be: scheduled, confirmed, completed, or cancelled'}), 400
        
        appointment_model = Appointment(current_app.db)
        success = appointment_model.update_appointment(appointment_id, request.current_user_id, data)
        
        if success:
            return jsonify({'message': 'Appointment updated successfully'}), 200
        else:
            return jsonify({'message': 'Appointment not found or access denied'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@appointment_bp.route('/<appointment_id>', methods=['DELETE'])
@token_required
def delete_appointment(appointment_id):
    try:
        appointment_model = Appointment(current_app.db)
        success = appointment_model.delete_appointment(appointment_id, request.current_user_id)
        
        if success:
            return jsonify({'message': 'Appointment deleted successfully'}), 200
        else:
            return jsonify({'message': 'Appointment not found or access denied'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500