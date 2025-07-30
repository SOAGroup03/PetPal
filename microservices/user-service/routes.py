from flask import Blueprint, request, jsonify, current_app
from models import User
from functools import wraps
import re

user_bp = Blueprint('users', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            user_model = User(current_app.db)
            user_id = user_model.verify_token(token)
            if not user_id:
                return jsonify({'message': 'Token is invalid!'}), 401
            request.current_user_id = user_id
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    return decorated

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['first_name', 'last_name', 'email', 'password', 'phone']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        if not validate_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        if len(data['password']) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        user_model = User(current_app.db)
        
        # Check if user already exists
        existing_user = user_model.get_user_by_email(data['email'])
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409
        
        # Create user
        user_id = user_model.create_user(data)
        token = user_model.generate_token(user_id)
        
        return jsonify({
            'message': 'User created successfully',
            'user_id': user_id,
            'token': token
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'message': 'Email and password are required'}), 400
        
        user_model = User(current_app.db)
        user = user_model.get_user_by_email(data['email'])
        
        if not user or not user_model.verify_password(user, data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        token = user_model.generate_token(user['_id'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    try:
        user_model = User(current_app.db)
        user = user_model.get_user_by_id(request.current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user_data = {
            'id': str(user['_id']),
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'phone': user['phone'],
            'address': user.get('address', ''),
            'created_at': user['created_at'].isoformat()
        }
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    try:
        data = request.get_json()
        user_model = User(current_app.db)
        
        # Remove password from update data for security
        if 'password' in data:
            del data['password']
        
        if 'email' in data and not validate_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        success = user_model.update_user(request.current_user_id, data)
        
        if success:
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@user_bp.route('/profile', methods=['DELETE'])
@token_required
def delete_profile():
    try:
        user_model = User(current_app.db)
        success = user_model.delete_user(request.current_user_id)
        
        if success:
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500