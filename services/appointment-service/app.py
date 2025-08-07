from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from config import Config
from routes import appointment_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Enable Prometheus metrics
    PrometheusMetrics(app)
    
    # Register blueprints
    app.register_blueprint(appointment_bp, url_prefix='/api/appointments')
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'appointment-service'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5003, debug=True)