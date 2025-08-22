# config/database_manager.py
import os
import sqlite3
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from config.database import DatabaseConfig

class DatabaseManager:
    """Database connection and operation manager"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.db_type = self.config.DATABASE_TYPE
        self.db_url = self.config.DATABASE_URL
        
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager for automatic cleanup"""
        connection = None
        try:
            if self.db_type == 'postgresql':
                import psycopg2
                if self.db_url:
                    # Use DATABASE_URL directly
                    connection = psycopg2.connect(self.db_url)
                else:
                    # Use parsed parameters
                    connection = psycopg2.connect(**self.config.get_connection_params())
                    
            elif self.db_type == 'mysql':
                import mysql.connector
                if self.db_url:
                    # Parse DATABASE_URL for MySQL
                    params = self.config._parse_database_url(self.db_url)
                    connection = mysql.connector.connect(**params)
                else:
                    # Use parsed parameters
                    connection = mysql.connector.connect(**self.config.get_connection_params())
                    
            elif self.db_type == 'sqlite':
                if self.db_url:
                    # Parse DATABASE_URL for SQLite
                    params = self.config._parse_database_url(self.db_url)
                    connection = sqlite3.connect(**params)
                else:
                    # Use parsed parameters
                    connection = sqlite3.connect(**self.config.get_connection_params())
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            yield connection
        except Exception as e:
            if connection:
                try:
                    connection.rollback()
                except:
                    pass
            raise e
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Execute a database query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch:
                    if self.db_type == 'sqlite':
                        # SQLite doesn't have column names in cursor.description
                        columns = [description[0] for description in cursor.description]
                        results = []
                        for row in cursor.fetchall():
                            results.append(dict(zip(columns, row)))
                        return results
                    else:
                        # PostgreSQL and MySQL have column names
                        columns = [desc[0] for desc in cursor.description]
                        results = []
                        for row in cursor.fetchall():
                            results.append(dict(zip(columns, row)))
                        return results
                else:
                    conn.commit()
                    return None
            finally:
                cursor.close()
    
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute multiple queries with different parameters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(query, params_list)
                conn.commit()
            finally:
                cursor.close()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        if self.db_type == 'postgresql':
            query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """
        elif self.db_type == 'mysql':
            query = """
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            """
        elif self.db_type == 'sqlite':
            query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """
        
        result = self.execute_query(query, (table_name,))
        if self.db_type == 'sqlite':
            return len(result) > 0
        else:
            return result[0]['exists'] if result else False
    
    def create_tables(self):
        """Create watermark tables if they don't exist"""
        if not self.table_exists('watermarks'):
            if self.db_type == 'postgresql':
                query = """
                    CREATE TABLE watermarks (
                        watermark_id SERIAL PRIMARY KEY,
                        store_name VARCHAR(255) NOT NULL,
                        watermark_url_image TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX idx_watermarks_store_name ON watermarks(store_name);
                """
            elif self.db_type == 'mysql':
                query = """
                    CREATE TABLE watermarks (
                        watermark_id INT AUTO_INCREMENT PRIMARY KEY,
                        store_name VARCHAR(255) NOT NULL,
                        watermark_url_image TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    );
                    CREATE INDEX idx_watermarks_store_name ON watermarks(store_name);
                """
            elif self.db_type == 'sqlite':
                query = """
                    CREATE TABLE watermarks (
                        watermark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        store_name TEXT NOT NULL,
                        watermark_url_image TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX idx_watermarks_store_name ON watermarks(store_name);
                """
            
            self.execute_query(query, fetch=False)
            print(f"Created watermarks table in {self.db_type} database")
    
    def get_last_insert_id(self, cursor) -> int:
        """Get the last inserted ID based on database type"""
        if self.db_type == 'postgresql':
            return cursor.fetchone()[0]
        elif self.db_type == 'mysql':
            return cursor.lastrowid
        elif self.db_type == 'sqlite':
            return cursor.lastrowid
        return None
    
    def test_connection(self) -> bool:
        """Test database connection and return True if successful"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if self.db_type == 'postgresql':
                    cursor.execute("SELECT 1")
                elif self.db_type == 'mysql':
                    cursor.execute("SELECT 1")
                elif self.db_type == 'sqlite':
                    cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False
