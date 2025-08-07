from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

# Service URLs
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5001')
PET_SERVICE_URL = os.getenv('PET_SERVICE_URL', 'http://localhost:5002')
APPOINTMENT_SERVICE_URL = os.getenv('APPOINTMENT_SERVICE_URL', 'http://localhost:5003')
MEDICAL_SERVICE_URL = os.getenv('MEDICAL_SERVICE_URL', 'http://localhost:5004')

def get_headers():
    """Get authorization headers"""
    token = session.get('token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}

def is_authenticated():
    """Check if user is authenticated"""
    return 'token' in session and 'user' in session

@app.route('/')
def index():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        try:
            response = requests.post(f'{USER_SERVICE_URL}/api/users/login', json=data)
            if response.status_code == 200:
                result = response.json()
                session['token'] = result['token']
                session['user'] = result['user']
                return jsonify({'success': True, 'redirect': '/dashboard'})
            else:
                return jsonify({'success': False, 'message': response.json().get('message', 'Login failed')})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Service unavailable'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        try:
            response = requests.post(f'{USER_SERVICE_URL}/api/users/register', json=data)
            if response.status_code == 201:
                return jsonify({'success': True, 'message': 'Registration successful'})
            else:
                return jsonify({'success': False, 'message': response.json().get('message', 'Registration failed')})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Service unavailable'})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    try:
        headers = get_headers()
        
        # Get user's pets
        pets_response = requests.get(f'{PET_SERVICE_URL}/api/pets/', headers=headers)
        pets = pets_response.json() if pets_response.status_code == 200 else []
        
        # Get upcoming appointments
        appointments_response = requests.get(f'{APPOINTMENT_SERVICE_URL}/api/appointments/upcoming', headers=headers)
        appointments = appointments_response.json() if appointments_response.status_code == 200 else []
        
        # Get recent medical records
        medical_response = requests.get(f'{MEDICAL_SERVICE_URL}/api/medical/recent?limit=5', headers=headers)
        medical_records = medical_response.json() if medical_response.status_code == 200 else []
        
        return render_template('dashboard.html', 
                             pets=pets, 
                             appointments=appointments, 
                             medical_records=medical_records)
    except Exception as e:
        return render_template('dashboard.html', 
                             pets=[], 
                             appointments=[], 
                             medical_records=[])

@app.route('/pets')
def pets():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('pets.html')

@app.route('/appointments')
def appointments():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('appointments.html')

@app.route('/medical')
def medical():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('medical.html')

# API proxy endpoints
@app.route('/api/users/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_users(path):
    headers = get_headers()
    headers['Content-Type'] = 'application/json'
    
    if request.method == 'POST':
        response = requests.post(f'{USER_SERVICE_URL}/api/users/{path}', 
                               json=request.get_json(), headers=headers)
    elif request.method == 'PUT':
        response = requests.put(f'{USER_SERVICE_URL}/api/users/{path}', 
                              json=request.get_json(), headers=headers)
    elif request.method == 'DELETE':
        response = requests.delete(f'{USER_SERVICE_URL}/api/users/{path}', headers=headers)
    else:
        response = requests.get(f'{USER_SERVICE_URL}/api/users/{path}', headers=headers)
    
    return jsonify(response.json()), response.status_code

@app.route('/api/pets/', methods=['GET', 'POST'])
@app.route('/api/pets/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_pets(path=''):
    headers = get_headers()
    if not headers.get('Authorization'):
        return jsonify({'message': 'Authentication required'}), 401
        
    headers['Content-Type'] = 'application/json'
    
    try:
        if request.method == 'POST':
            response = requests.post(f'{PET_SERVICE_URL}/api/pets/{path}', 
                                   json=request.get_json(), headers=headers)
        elif request.method == 'PUT':
            response = requests.put(f'{PET_SERVICE_URL}/api/pets/{path}', 
                                  json=request.get_json(), headers=headers)
        elif request.method == 'DELETE':
            response = requests.delete(f'{PET_SERVICE_URL}/api/pets/{path}', headers=headers)
        else:
            response = requests.get(f'{PET_SERVICE_URL}/api/pets/{path}', headers=headers)
        
        return response.json(), response.status_code
        
    except Exception as e:
        return jsonify({'message': 'Service error'}), 500

@app.route('/api/appointments/', methods=['GET', 'POST'])
@app.route('/api/appointments/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_appointments(path=''):
    headers = get_headers()
    if not headers.get('Authorization'):
        return jsonify({'message': 'Authentication required'}), 401
        
    headers['Content-Type'] = 'application/json'
    
    try:
        if request.method == 'POST':
            response = requests.post(f'{APPOINTMENT_SERVICE_URL}/api/appointments/{path}', 
                                   json=request.get_json(), headers=headers)
        elif request.method == 'PUT':
            response = requests.put(f'{APPOINTMENT_SERVICE_URL}/api/appointments/{path}', 
                                  json=request.get_json(), headers=headers)
        elif request.method == 'DELETE':
            response = requests.delete(f'{APPOINTMENT_SERVICE_URL}/api/appointments/{path}', headers=headers)
        else:
            response = requests.get(f'{APPOINTMENT_SERVICE_URL}/api/appointments/{path}', headers=headers)
        
        return response.json(), response.status_code
        
    except Exception as e:
        return jsonify({'message': 'Service error'}), 500

@app.route('/api/medical/', methods=['GET', 'POST'])
@app.route('/api/medical/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_medical(path=''):
    headers = get_headers()
    if not headers.get('Authorization'):
        return jsonify({'message': 'Authentication required'}), 401
        
    headers['Content-Type'] = 'application/json'
    
    try:
        if request.method == 'POST':
            response = requests.post(f'{MEDICAL_SERVICE_URL}/api/medical/{path}', 
                                   json=request.get_json(), headers=headers)
        elif request.method == 'PUT':
            response = requests.put(f'{MEDICAL_SERVICE_URL}/api/medical/{path}', 
                                  json=request.get_json(), headers=headers)
        elif request.method == 'DELETE':
            response = requests.delete(f'{MEDICAL_SERVICE_URL}/api/medical/{path}', headers=headers)
        else:
            response = requests.get(f'{MEDICAL_SERVICE_URL}/api/medical/{path}', headers=headers)
        
        return response.json(), response.status_code
        
    except Exception as e:
        return jsonify({'message': 'Service error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)