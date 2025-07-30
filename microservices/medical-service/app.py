from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import os
from routes import medical_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'petpal-secret-key-2024')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb+srv://acsujan69:petpal123@petpal.9k6d9qu.mongodb.net/petpal')

CORS(app)

# MongoDB connection
client = MongoClient(app.config['MONGO_URI'])
db = client.petpal
app.db = db

# Register blueprints
app.register_blueprint(medical_bp, url_prefix='/api/medical')

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'medical-service'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    app.run(host='0.0.0.0', port=port, debug=True)