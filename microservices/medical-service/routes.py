from flask import Blueprint, request, jsonify, current_app
from models import MedicalHistory
from functools import wraps
from datetime import datetime

medical_bp = Blueprint('medical', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            medical_model = MedicalHistory(current_app.db)
            user_id = medical_model.verify_token(token)
            if not user_id:
                return jsonify({'message': 'Token is invalid!'}), 401
            request.current_user_id = user_id
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    return decorated

@medical_bp.route('/', methods=['POST'])
@token_required
def create_medical_record():
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['pet_id', 'visit_date', 'vet_name', 'diagnosis', 'treatment']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate date format
        try:
            datetime.strptime(data['visit_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Add user ID
        data['user_id'] = request.current_user_id
        
        medical_model = MedicalHistory(current_app.db)
        record_id = medical_model.create_medical_record(data)
        
        return jsonify({
            'message': 'Medical record created successfully',
            'record_id': record_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@medical_bp.route('/pet/<pet_id>', methods=['GET'])
@token_required
def get_medical_history_by_pet(pet_id):
    try:
        medical_model = MedicalHistory(current_app.db)
        records = medical_model.get_medical_history_by_pet(pet_id, request.current_user_id)
        
        return jsonify({'medical_records': records}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@medical_bp.route('/', methods=['GET'])
@token_required
def get_all_medical_records():
    try:
        medical_model = MedicalHistory(current_app.db)
        records = medical_model.get_all_medical_records_by_user(request.current_user_id)
        
        return jsonify({'medical_records': records}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@medical_bp.route('/<record_id>', methods=['GET'])
@token_required
def get_medical_record(record_id):
    try:
        medical_model = MedicalHistory(current_app.db)
        record = medical_model.get_medical_record_by_id(record_id)
        
        if not record:
            return jsonify({'message': 'Medical record not found'}), 404
        
        # Check if user owns this record
        if record['user_id'] != request.current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify({'medical_record': record}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@medical_bp.route('/<record_id>', methods=['PUT'])
@token_required
def update_medical_record(record_id):
    try:
        data = request.get_json()
        
        # Validate date format if provided
        if 'visit_date' in data:
            try:
                datetime.strptime(data['visit_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        medical_model = MedicalHistory(current_app.db)
        success = medical_model.update_medical_record(record_id, request.current_user_id, data)
        
        if success:
            return jsonify({'message': 'Medical record updated successfully'}), 200
        else:
            return jsonify({'message': 'Medical record not found or access denied'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@medical_bp.route('/<record_id>', methods=['DELETE'])
@token_required
def delete_medical_record(record_id):
    try:
        medical_model = MedicalHistory(current_app.db)
        success = medical_model.delete_medical_record(record_id, request.current_user_id)
        
        if success:
            return jsonify({'message': 'Medical record deleted successfully'}), 200
        else:
            return jsonify({'message': 'Medical record not found or access denied'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500