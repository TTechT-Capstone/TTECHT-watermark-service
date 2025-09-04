# app.py
from flask import Flask
from flask_cors import CORS
import cloudinary
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configure CORS
    # Get allowed origins from environment variable
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080,https://www.origity.store').split(',')
    
    # Clean up origins (remove whitespace and empty strings)
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    
    print(f"🔒 CORS allowed origins: {allowed_origins}")
    
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True
        },
        r"/health": {
            "origins": allowed_origins,
            "methods": ["GET"]
        }
    })
    
    # Configure Flask
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    app.config['JSON_SORT_KEYS'] = False
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )
    
    # Import and register blueprints after app creation to avoid circular imports
    try:
        from routes.image_routes import image_bp
        from routes.watermark_routes import watermark_bp
        from routes.direct_api_routes import direct_api_bp
        app.register_blueprint(image_bp)
        app.register_blueprint(watermark_bp)
        app.register_blueprint(direct_api_bp)
    except ImportError as e:
        print(f"Error importing routes: {e}")
        raise
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Endpoint not found',
            'code': 'NOT_FOUND'
        }, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            'error': 'Method not allowed',
            'code': 'METHOD_NOT_ALLOWED'
        }, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }, 500
    
    # Add a simple health check route
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)