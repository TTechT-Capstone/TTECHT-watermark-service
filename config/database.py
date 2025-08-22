# config/database.py
import os
from typing import Dict, Any

class DatabaseConfig:
    """Database configuration class for watermark service"""
    
    # Database type - change this based on your database choice
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'postgresql')  # postgresql, mysql, sqlite
    
    # PostgreSQL configuration
    POSTGRESQL_CONFIG = {
        'host': os.getenv('POSTGRESQL_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRESQL_PORT', 5432)),
        'database': os.getenv('POSTGRESQL_DATABASE', 'watermark_service'),
        'user': os.getenv('POSTGRESQL_USER', 'postgres'),
        'password': os.getenv('POSTGRESQL_PASSWORD', ''),
        'sslmode': os.getenv('POSTGRESQL_SSLMODE', 'prefer')
    }
    
    # MySQL configuration
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'database': os.getenv('MYSQL_DATABASE', 'watermark_service'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    # SQLite configuration
    SQLITE_CONFIG = {
        'database': os.getenv('SQLITE_DATABASE', 'watermarks.db'),
        'check_same_thread': False
    }
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database connection URL based on environment variables"""
        if cls.DATABASE_TYPE == 'postgresql':
            user = cls.POSTGRESQL_CONFIG['user']
            password = cls.POSTGRESQL_CONFIG['password']
            host = cls.POSTGRESQL_CONFIG['host']
            port = cls.POSTGRESQL_CONFIG['port']
            database = cls.POSTGRESQL_CONFIG['database']
            
            if password:
                return f"postgresql://{user}:{password}@{host}:{port}/{database}"
            else:
                return f"postgresql://{user}@{host}:{port}/{database}"
        
        elif cls.DATABASE_TYPE == 'mysql':
            user = cls.MYSQL_CONFIG['user']
            password = cls.MYSQL_CONFIG['password']
            host = cls.MYSQL_CONFIG['host']
            port = cls.MYSQL_CONFIG['port']
            database = cls.MYSQL_CONFIG['database']
            
            if password:
                return f"mysql://{user}:{password}@{host}:{port}/{database}"
            else:
                return f"mysql://{user}@{host}:{port}/{database}"
        
        elif cls.DATABASE_TYPE == 'sqlite':
            database = cls.SQLITE_CONFIG['database']
            return f"sqlite:///{database}"
        
        else:
            raise ValueError(f"Unsupported database type: {cls.DATABASE_TYPE}")
    
    @classmethod
    def get_connection_params(cls) -> Dict[str, Any]:
        """Get database connection parameters based on database type"""
        if cls.DATABASE_TYPE == 'postgresql':
            return cls.POSTGRESQL_CONFIG
        elif cls.DATABASE_TYPE == 'mysql':
            return cls.MYSQL_CONFIG
        elif cls.DATABASE_TYPE == 'sqlite':
            return cls.SQLITE_CONFIG
        else:
            raise ValueError(f"Unsupported database type: {cls.DATABASE_TYPE}")
    
    @classmethod
    def get_sql_dialect(cls) -> str:
        """Get SQL dialect for the configured database"""
        if cls.DATABASE_TYPE == 'postgresql':
            return 'postgresql'
        elif cls.DATABASE_TYPE == 'mysql':
            return 'mysql'
        elif cls.DATABASE_TYPE == 'sqlite':
            return 'sqlite'
        else:
            raise ValueError(f"Unsupported database type: {cls.DATABASE_TYPE}")

# Example environment variables for .env file:
# DATABASE_TYPE=postgresql
# POSTGRESQL_HOST=your-db-host.com
# POSTGRESQL_PORT=5432
# POSTGRESQL_DATABASE=watermark_service
# POSTGRESQL_USER=your_username
# POSTGRESQL_PASSWORD=your_password
# POSTGRESQL_SSLMODE=require
