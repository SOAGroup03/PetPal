from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from config import Config
from routes import medical_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Enable Prometheus metrics
    PrometheusMetrics(app)
    
    # Register blueprints
    app.register_blueprint(medical_bp, url_prefix='/api/medical')
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'medical-service'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5004, debug=True)