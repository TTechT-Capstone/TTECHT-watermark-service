# app.py
from flask import Flask
import cloudinary
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
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
        app.register_blueprint(image_bp)
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