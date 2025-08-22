# config/database.py
import os
from typing import Dict, Any

class DatabaseConfig:
    """Database configuration class for watermark service"""
    
    def __init__(self):
        """Initialize config and ensure environment variables are loaded"""
        # Try to load .env file if it exists
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv not installed, use system environment
    
    @property
    def DATABASE_TYPE(self):
        """Get database type from environment"""
        return os.getenv('DATABASE_TYPE', 'postgresql')
    
    @property
    def DATABASE_URL(self):
        """Get database URL from environment"""
        return os.getenv('DATABASE_URL')
    
    # PostgreSQL configuration (fallback if DATABASE_URL not provided)
    POSTGRESQL_CONFIG = {
        'host': os.getenv('POSTGRESQL_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRESQL_PORT', 5432)),
        'database': os.getenv('POSTGRESQL_DATABASE', 'watermark_service'),
        'user': os.getenv('POSTGRESQL_USER', 'postgres'),
        'password': os.getenv('POSTGRESQL_PASSWORD', ''),
        'sslmode': os.getenv('POSTGRESQL_SSLMODE', 'prefer')
    }
    
    # MySQL configuration (fallback if DATABASE_URL not provided)
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'database': os.getenv('MYSQL_DATABASE', 'watermark_service'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    # SQLite configuration (fallback if DATABASE_URL not provided)
    SQLITE_CONFIG = {
        'database': os.getenv('SQLITE_DATABASE', 'watermarks.db'),
        'check_same_thread': False
    }
    
    def get_database_url(self) -> str:
        """Get database connection URL based on environment variables"""
        # If DATABASE_URL is provided, use it directly
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Otherwise, construct URL from individual parameters
        if self.DATABASE_TYPE == 'postgresql':
            user = self.POSTGRESQL_CONFIG['user']
            password = self.POSTGRESQL_CONFIG['password']
            host = self.POSTGRESQL_CONFIG['host']
            port = self.POSTGRESQL_CONFIG['port']
            database = self.POSTGRESQL_CONFIG['database']
            
            if password:
                return f"postgresql://{user}:{password}@{host}:{port}/{database}"
            else:
                return f"postgresql://{user}@{host}:{port}/{database}"
        
        elif self.DATABASE_TYPE == 'mysql':
            user = self.MYSQL_CONFIG['user']
            password = self.MYSQL_CONFIG['password']
            host = self.MYSQL_CONFIG['host']
            port = self.MYSQL_CONFIG['port']
            database = self.MYSQL_CONFIG['database']
            
            if password:
                return f"mysql://{user}:{password}@{host}:{port}/{database}"
            else:
                return f"mysql://{user}@{host}:{port}/{database}"
        
        elif self.DATABASE_TYPE == 'sqlite':
            database = self.SQLITE_CONFIG['database']
            return f"sqlite:///{database}"
        
        else:
            raise ValueError(f"Unsupported database type: {self.DATABASE_TYPE}")
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get database connection parameters based on database type"""
        # If DATABASE_URL is provided, parse it to get connection params
        if self.DATABASE_URL:
            return self._parse_database_url(self.DATABASE_URL)
        
        # Otherwise, use individual parameters
        if self.DATABASE_TYPE == 'postgresql':
            return self.POSTGRESQL_CONFIG
        elif self.DATABASE_TYPE == 'mysql':
            return self.MYSQL_CONFIG
        elif self.DATABASE_TYPE == 'sqlite':
            return self.SQLITE_CONFIG
        else:
            raise ValueError(f"Unsupported database type: {self.DATABASE_TYPE}")
    
    def _parse_database_url(self, database_url: str) -> Dict[str, Any]:
        """Parse DATABASE_URL to extract connection parameters"""
        try:
            from urllib.parse import urlparse
            
            parsed = urlparse(database_url)
            
            if parsed.scheme == 'postgresql':
                return {
                    'host': parsed.hostname or 'localhost',
                    'port': parsed.port or 5432,
                    'database': parsed.path.lstrip('/') or 'watermark_service',
                    'user': parsed.username or 'postgres',
                    'password': parsed.password or '',
                    'sslmode': 'prefer'
                }
            elif parsed.scheme == 'mysql':
                return {
                    'host': parsed.hostname or 'localhost',
                    'port': parsed.port or 3306,
                    'database': parsed.path.lstrip('/') or 'watermark_service',
                    'user': parsed.username or 'root',
                    'password': parsed.password or '',
                    'charset': 'utf8mb4',
                    'autocommit': True
                }
            elif parsed.scheme == 'sqlite':
                return {
                    'database': parsed.path.lstrip('/') or 'watermarks.db',
                    'check_same_thread': False
                }
            else:
                raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
                
        except Exception as e:
            raise ValueError(f"Invalid DATABASE_URL format: {e}")
    
    def get_sql_dialect(self) -> str:
        """Get SQL dialect for the configured database"""
        if self.DATABASE_TYPE == 'postgresql':
            return 'postgresql'
        elif self.DATABASE_TYPE == 'mysql':
            return 'mysql'
        elif self.DATABASE_TYPE == 'sqlite':
            return 'sqlite'
        else:
            raise ValueError(f"Unsupported database type: {self.DATABASE_TYPE}")

# Example environment variables for .env file:
# Option 1: Use DATABASE_URL (recommended)
# DATABASE_URL=postgresql://username:password@host:port/database
# DATABASE_URL=mysql://username:password@host:port/database
# DATABASE_URL=sqlite:///watermarks.db

# Option 2: Use individual parameters (fallback)
# DATABASE_TYPE=postgresql
# POSTGRESQL_HOST=your-db-host.com
# POSTGRESQL_PORT=5432
# POSTGRESQL_DATABASE=watermark_service
# POSTGRESQL_USER=your_username
# POSTGRESQL_PASSWORD=your_password
# POSTGRESQL_SSLMODE=require
