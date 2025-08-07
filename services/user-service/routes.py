from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
import os
from models import UserModel
from functools import wraps

user_bp = Blueprint('user', __name__)
user_model = UserModel()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, os.getenv('JWT_SECRET', 'secret'), algorithms=['HS256'])
            current_user = user_model.get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Check if user already exists
        if user_model.get_user_by_email(data['email']):
            return jsonify({'message': 'User already exists'}), 400
        
        # Create user
        user_id = user_model.create_user(data)
        if user_id:
            return jsonify({
                'message': 'User created successfully',
                'user_id': user_id
            }), 201
        else:
            return jsonify({'message': 'Failed to create user'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        user = user_model.verify_password(email, password)
        if user:
            # Generate JWT token
            token = jwt.encode({
                'user_id': user['_id'],
                'email': user['email'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, os.getenv('JWT_SECRET', 'secret'), algorithm='HS256')
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user['_id'],
                    'name': user['name'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        # Remove password from response
        user_data = {key: value for key, value in current_user.items() if key != 'password'}
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        forbidden_fields = ['_id', 'email', 'password', 'created_at']
        for field in forbidden_fields:
            data.pop(field, None)
        
        if user_model.update_user(current_user['_id'], data):
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'message': 'Failed to update profile'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/profile', methods=['DELETE'])
@token_required
def delete_profile(current_user):
    try:
        if user_model.delete_user(current_user['_id']):
            return jsonify({'message': 'Profile deleted successfully'}), 200
        else:
            return jsonify({'message': 'Failed to delete profile'}), 500
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    try:
        user = user_model.get_user_by_id(user_id)
        if user:
            # Remove password from response
            user_data = {key: value for key, value in user.items() if key != 'password'}
            return jsonify(user_data), 200
        else:
            return jsonify({'message': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/verify-token', methods=['POST'])
def verify_token():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'valid': False}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
            
        data = jwt.decode(token, os.getenv('JWT_SECRET', 'secret'), algorithms=['HS256'])
        user = user_model.get_user_by_id(data['user_id'])
        
        if user:
            return jsonify({
                'valid': True,
                'user': {
                    'id': user['_id'],
                    'name': user['name'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'valid': False}), 401
            
    except:
        return jsonify({'valid': False}), 401