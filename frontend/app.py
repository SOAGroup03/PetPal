# frontend/app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'petpal-secret-key-2024')

# Microservice URLs - Updated for Google Cloud Run or local development
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5001')
PET_SERVICE_URL = os.environ.get('PET_SERVICE_URL', 'http://localhost:5002')
APPOINTMENT_SERVICE_URL = os.environ.get('APPOINTMENT_SERVICE_URL', 'http://localhost:5003')
MEDICAL_SERVICE_URL = os.environ.get('MEDICAL_SERVICE_URL', 'http://localhost:5004')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/pets')
def pets():
    return render_template('pets.html')

@app.route('/appointments')
def appointments():
    return render_template('appointments.html')

@app.route('/medical-history')
def medical_history():
    return render_template('medical_history.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'frontend'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)