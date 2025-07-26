# debug.py
import sys
import traceback

print("Python version:", sys.version)
print("Python path:", sys.path)

try:
    print("Testing imports...")
    
    print("1. Testing Flask import...")
    from flask import Flask
    print("   ✓ Flask imported successfully")
    
    print("2. Testing Cloudinary import...")
    import cloudinary
    print("   ✓ Cloudinary imported successfully")
    
    print("3. Testing PIL import...")
    from PIL import Image
    print("   ✓ PIL imported successfully")
    
    print("4. Testing service import...")
    from service.image_service import ImageService
    print("   ✓ ImageService imported successfully")
    
    print("5. Testing controller import...")
    from controller.image_controller import ImageController
    print("   ✓ ImageController imported successfully")
    
    print("6. Testing routes import...")
    from routes.image_routes import image_bp
    print("   ✓ Routes imported successfully")
    
    print("7. Testing app creation...")
    from app import app
    print("   ✓ App created successfully")
    
    print("8. Testing app context...")
    with app.app_context():
        print("   ✓ App context works")
    
    print("\n✅ All imports successful! The app should work.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    
    print(f"\nError type: {type(e)}")
    print(f"Error args: {e.args}")