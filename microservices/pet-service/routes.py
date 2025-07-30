from flask import Blueprint, request, jsonify, current_app
from models import Pet
from functools import wraps
from datetime import datetime

pet_bp = Blueprint('pets', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            pet_model = Pet(current_app.db)
            user_id = pet_model.verify_token(token)
            if not user_id:
                return jsonify({'message': 'Token is invalid!'}), 401
            request.current_user_id = user_id
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    return decorated

@pet_bp.route('/', methods=['POST'])
@token_required
def create_pet():
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'species', 'breed', 'date_of_birth']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate date of birth
        try:
            datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Add owner ID
        data['owner_id'] = request.current_user_id
        
        pet_model = Pet(current_app.db)
        pet_id = pet_model.create_pet(data)
        
        return jsonify({
            'message': 'Pet created successfully',
            'pet_id': pet_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@pet_bp.route('/', methods=['GET'])
@token_required
def get_pets():
    try:
        pet_model = Pet(current_app.db)
        pets = pet_model.get_pets_by_owner(request.current_user_id)
        
        return jsonify({'pets': pets}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@pet_bp.route('/<pet_id>', methods=['GET'])
@token_required
def get_pet(pet_id):
    try:
        pet_model = Pet(current_app.db)
        pet = pet_model.get_pet_by_id(pet_id)
        
        if not pet:
            return jsonify({'message': 'Pet not found'}), 404
        
        # Check if user owns this pet
        if pet['owner_id'] != request.current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify({'pet': pet}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@pet_bp.route('/<pet_id>', methods=['PUT'])
@token_required
def update_pet(pet_id):
    try:
        data = request.get_json()
        
        # Validate date of birth if provided
        if 'date_of_birth' in data:
            try:
                datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        pet_model = Pet(current_app.db)
        success = pet_model.update_pet(pet_id, request.current_user_id, data)
        
        if success:
            return jsonify({'message': 'Pet updated successfully'}), 200
        else:
            return jsonify({'message': 'Pet not found or access denied'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@pet_bp.route('/<pet_id>', methods=['DELETE'])
@token_required
def delete_pet(pet_id):
    try:
        pet_model = Pet(current_app.db)
        success = pet_model.delete_pet(pet_id, request.current_user_id)
        
        if success:
            return jsonify({'message': 'Pet deleted successfully'}), 200
        else:
            return jsonify({'message': 'Pet not found or access denied'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500