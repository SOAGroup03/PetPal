from flask import Blueprint, request, jsonify
import requests
import os
from models import PetModel
from functools import wraps

pet_bp = Blueprint('pet', __name__)
pet_model = PetModel()

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
        
        return f(user_data['user'], *args, **kwargs)
    return decorated

@pet_bp.route('/', methods=['POST'])
@token_required
def create_pet(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'species', 'breed', 'age']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Convert age to number if it's a string
        try:
            data['age'] = float(data['age'])
        except (ValueError, TypeError):
            return jsonify({'message': 'Age must be a number'}), 400
        
        # Add user_id to pet data
        data['user_id'] = current_user['id']
        
        # Create pet
        pet_id = pet_model.create_pet(data)
        if pet_id:
            return jsonify({
                'message': 'Pet created successfully',
                'pet_id': pet_id
            }), 201
        else:
            return jsonify({'message': 'Failed to create pet'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@pet_bp.route('/', methods=['GET'])
@token_required
def get_pets(current_user):
    try:
        pets = pet_model.get_pets_by_user(current_user['id'])
        return jsonify(pets), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@pet_bp.route('/<pet_id>', methods=['GET'])
@token_required
def get_pet(current_user, pet_id):
    try:
        pet = pet_model.get_pet_by_id_and_user(pet_id, current_user['id'])
        if pet:
            return jsonify(pet), 200
        else:
            return jsonify({'message': 'Pet not found'}), 404
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@pet_bp.route('/<pet_id>', methods=['PUT'])
@token_required
def update_pet(current_user, pet_id):
    try:
        # Verify pet ownership
        pet = pet_model.get_pet_by_id_and_user(pet_id, current_user['id'])
        if not pet:
            return jsonify({'message': 'Pet not found'}), 404
        
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        forbidden_fields = ['_id', 'user_id', 'created_at']
        for field in forbidden_fields:
            data.pop(field, None)
        
        if pet_model.update_pet(pet_id, data):
            return jsonify({'message': 'Pet updated successfully'}), 200
        else:
            return jsonify({'message': 'Failed to update pet'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@pet_bp.route('/<pet_id>', methods=['DELETE'])
@token_required
def delete_pet(current_user, pet_id):
    try:
        # Verify pet ownership
        pet = pet_model.get_pet_by_id_and_user(pet_id, current_user['id'])
        if not pet:
            return jsonify({'message': 'Pet not found'}), 404
        
        if pet_model.delete_pet(pet_id):
            return jsonify({'message': 'Pet deleted successfully'}), 200
        else:
            return jsonify({'message': 'Failed to delete pet'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@pet_bp.route('/verify/<pet_id>', methods=['GET'])
@token_required
def verify_pet_ownership(current_user, pet_id):
    """Verify pet ownership for other services"""
    try:
        pet = pet_model.get_pet_by_id_and_user(pet_id, current_user['id'])
        if pet:
            return jsonify({'valid': True, 'pet': pet}), 200
        else:
            return jsonify({'valid': False}), 404
            
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500