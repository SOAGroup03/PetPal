from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from config import Config
from routes import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Enable Prometheus metrics
    PrometheusMetrics(app)
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'user-service'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)