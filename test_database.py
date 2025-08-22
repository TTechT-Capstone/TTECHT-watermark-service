#!/usr/bin/env python3
"""
Test script for database connection and watermark service
"""

import os
from dotenv import load_dotenv
from config.database_manager import DatabaseManager
from service.watermark_service import WatermarkService
from entity.watermark import Watermark

def test_database_connection():
    """Test basic database connection"""
    print("Testing database connection...")
    
    try:
        # Debug: Check DatabaseConfig first
        from config.database import DatabaseConfig
        config = DatabaseConfig()
        print(f"✓ DatabaseConfig.DATABASE_URL: {config.DATABASE_URL}")
        print(f"✓ DatabaseConfig.DATABASE_TYPE: {config.DATABASE_TYPE}")
        
        # Debug: Show connection parameters
        try:
            params = config.get_connection_params()
            # Hide password for security
            safe_params = params.copy()
            if 'password' in safe_params:
                safe_params['password'] = '***'
            print(f"✓ Connection params: {safe_params}")
        except Exception as e:
            print(f"✗ Error getting connection params: {e}")
            return False
        
        db_manager = DatabaseManager()
        print(f"✓ Database type: {db_manager.db_type}")
        
        if db_manager.db_url:
            # Show more details about the URL
            try:
                from urllib.parse import urlparse
                parsed = urlparse(db_manager.db_url)
                print(f"✓ Using DATABASE_URL:")
                print(f"   Scheme: {parsed.scheme}")
                print(f"   Host: {parsed.hostname}")
                print(f"   Port: {parsed.port}")
                print(f"   Database: {parsed.path.lstrip('/')}")
                print(f"   Username: {parsed.username}")
            except Exception as e:
                print(f"✗ Error parsing URL: {e}")
                print(f"✓ Raw URL (masked): {db_manager.db_url.split('@')[0]}@***")
        else:
            print("✓ Using individual connection parameters")
        
        # Test connection with detailed error reporting
        print("Attempting database connection...")
        try:
            if db_manager.test_connection():
                print("✓ Database connection successful")
            else:
                print("✗ Database connection failed (test_connection returned False)")
                return False
        except Exception as e:
            print(f"✗ Database connection exception: {e}")
            print(f"   Exception type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
        
        # Test table creation
        try:
            db_manager.create_tables()
            print("✓ Tables created/verified successfully")
        except Exception as e:
            print(f"✗ Table creation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        import traceback
        print(f"   Full traceback: {traceback.format_exc()}")
        return False

def test_watermark_service():
    """Test watermark service operations"""
    print("\nTesting watermark service...")
    
    try:
        service = WatermarkService()
        print("✓ Watermark service initialized")
        
        # Test create watermark
        watermark = service.create_watermark(
            store_name="Test Store",
            watermark_url_image="https://example.com/test-logo.png"
        )
        print(f"✓ Created watermark with ID: {watermark.watermark_id}")
        
        # Test get watermark by ID
        retrieved = service.get_watermark_by_id(watermark.watermark_id)
        if retrieved:
            print(f"✓ Retrieved watermark: {retrieved.store_name}")
        else:
            print("✗ Failed to retrieve watermark")
        
        # Test get all watermarks
        all_watermarks = service.get_all_watermarks()
        print(f"✓ Total watermarks: {len(all_watermarks)}")
        
        # Test search
        search_results = service.search_watermarks("Test")
        print(f"✓ Search results: {len(search_results)}")
        
        # Test update
        updated = service.update_watermark(
            watermark.watermark_id,
            store_name="Updated Test Store"
        )
        if updated:
            print(f"✓ Updated watermark: {updated.store_name}")
        
        # Test delete
        deleted = service.delete_watermark(watermark.watermark_id)
        if deleted:
            print("✓ Deleted watermark successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Watermark service test failed: {e}")
        return False

def show_environment_info():
    """Show current environment configuration"""
    print("\nEnvironment Configuration:")
    print("-" * 30)
    
    # Check for DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print(f"✓ DATABASE_URL found: {db_url.split('@')[0]}@***")
        # Parse to show database type
        try:
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            print(f"  Database type: {parsed.scheme}")
            print(f"  Host: {parsed.hostname}")
            print(f"  Port: {parsed.port}")
            print(f"  Database: {parsed.path.lstrip('/')}")
        except:
            print("  Could not parse DATABASE_URL")
    else:
        print("✗ DATABASE_URL not found")
        
        # Check for individual parameters
        db_type = os.getenv('DATABASE_TYPE')
        if db_type:
            print(f"✓ DATABASE_TYPE: {db_type}")
        else:
            print("✗ DATABASE_TYPE not set")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✓ .env file found")
    else:
        print("✗ .env file not found")

def main():
    """Main test function"""
    print("=" * 50)
    print("DATABASE CONNECTION TEST")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Show environment info
    show_environment_info()
    
    # Test database connection
    db_success = test_database_connection()
    
    if db_success:
        # Test watermark service
        service_success = test_watermark_service()
        
        if service_success:
            print("\n" + "=" * 50)
            print("✓ ALL TESTS PASSED!")
            print("✓ Database connection working")
            print("✓ Watermark service working")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("✗ SERVICE TESTS FAILED")
            print("✓ Database connection working")
            print("✗ Watermark service has issues")
            print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("✗ DATABASE CONNECTION FAILED")
        print("✗ Check your .env file and database settings")
        print("=" * 50)
        print("\nMake sure you have:")
        print("1. Created a .env file with database configuration")
        print("2. Installed the correct database driver")
        print("3. Database server is running")
        print("4. Database exists and is accessible")
        print("\nExample .env file:")
        print("DATABASE_URL=postgresql://username:password@localhost:5432/watermark_service")
        print("# or")
        print("DATABASE_TYPE=postgresql")
        print("POSTGRESQL_HOST=localhost")
        print("POSTGRESQL_PORT=5432")
        print("POSTGRESQL_DATABASE=watermark_service")
        print("POSTGRESQL_USER=username")
        print("POSTGRESQL_PASSWORD=password")

if __name__ == "__main__":
    main()
