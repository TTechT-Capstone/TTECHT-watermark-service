import json
import os
import tempfile
from typing import List, Dict, Optional
from entity.watermark import Watermark
import uuid
from config.database_manager import DatabaseManager

class WatermarkService:
    def __init__(self):
        """Initialize watermark service with database connection"""
        # Initialize database manager
        try:
            self.db_manager = DatabaseManager()
            
            # Create tables if they don't exist
            try:
                self.db_manager.create_tables()
                print("✓ Database connection successful")
            except Exception as e:
                print(f"✗ Database table creation failed: {e}")
                raise Exception(f"Database initialization failed: {e}")
                
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            raise Exception(f"Database connection failed: {e}")
    

    
    def create_watermark(self, store_name: str, watermark_url_image: str) -> Watermark:
        """
        Create a new watermark
        
        Args:
            store_name: Name of the store/brand
            watermark_url_image: URL or path to watermark image
            
        Returns:
            Watermark: Created watermark object
            
        Raises:
            ValueError: If store_name is empty or watermark_url_image is invalid
        """
        if not store_name or not store_name.strip():
            raise ValueError("Store name cannot be empty")
        
        if not watermark_url_image or not watermark_url_image.strip():
            raise ValueError("Watermark image URL cannot be empty")
        
        # Use database only
        if self.db_manager.db_type == 'postgresql':
            # PostgreSQL needs RETURNING clause to get the generated ID
            query = """
                INSERT INTO watermarks (store_name, watermark_url_image) 
                VALUES (%s, %s)
                RETURNING watermark_id
            """
        else:
            # MySQL and SQLite don't need RETURNING
            query = """
                INSERT INTO watermarks (store_name, watermark_url_image) 
                VALUES (%s, %s)
            """
        
        if self.db_manager.db_type == 'sqlite':
            query = query.replace('%s', '?')
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (store_name.strip(), watermark_url_image.strip()))
            
            if self.db_manager.db_type == 'postgresql':
                # PostgreSQL returns the ID via RETURNING clause
                result = cursor.fetchone()
                if result:
                    watermark_id = result[0]
                else:
                    raise Exception("Failed to get generated watermark ID from PostgreSQL")
            else:
                # MySQL and SQLite use lastrowid
                watermark_id = cursor.lastrowid
            
            conn.commit()
        
        # Create and return watermark object
        watermark = Watermark(
            watermark_id=watermark_id,
            store_name=store_name.strip(),
            watermark_url_image=watermark_url_image.strip()
        )
        return watermark
    
    def get_watermark_by_id(self, watermark_id: int) -> Optional[Watermark]:
        """
        Get watermark by ID
        
        Args:
            watermark_id: ID of the watermark to retrieve
            
        Returns:
            Watermark: Watermark object if found, None otherwise
        """
        # Use database only
        query = """
            SELECT watermark_id, store_name, watermark_url_image 
            FROM watermarks 
            WHERE watermark_id = %s
        """
        
        if self.db_manager.db_type == 'sqlite':
            query = query.replace('%s', '?')
        
        result = self.db_manager.execute_query(query, (watermark_id,))
        
        if result and len(result) > 0:
            watermark_data = result[0]
            return Watermark.from_dict(watermark_data)
        
        return None
    
    def get_watermark_by_store_name(self, store_name: str) -> Optional[Watermark]:
        """
        Get watermark by store name
        
        Args:
            store_name: Name of the store to search for
            
        Returns:
            Watermark: Watermark object if found, None otherwise
        """
        # Use database only
        query = """
            SELECT watermark_id, store_name, watermark_url_image 
            FROM watermarks 
            WHERE store_name = %s
        """
        
        if self.db_manager.db_type == 'sqlite':
            query = query.replace('%s', '?')
        
        result = self.db_manager.execute_query(query, (store_name,))
        
        if result and len(result) > 0:
            watermark_data = result[0]
            return Watermark.from_dict(watermark_data)
        
        return None
    
    def get_all_watermarks(self) -> List[Watermark]:
        """
        Get all watermarks
        
        Returns:
            List[Watermark]: List of all watermark objects
        """
        # Use database only
        query = """
            SELECT watermark_id, store_name, watermark_url_image 
            FROM watermarks 
            ORDER BY watermark_id
        """
        
        result = self.db_manager.execute_query(query)
        
        if result:
            return [Watermark.from_dict(w) for w in result]
        
        return []
    
    def update_watermark(self, watermark_id: int, store_name: str = None, 
                        watermark_url_image: str = None) -> Optional[Watermark]:
        """
        Update an existing watermark
        
        Args:
            watermark_id: ID of the watermark to update
            store_name: New store name (optional)
            watermark_url_image: New watermark image URL (optional)
            
        Returns:
            Watermark: Updated watermark object if found, None otherwise
            
        Raises:
            ValueError: If both store_name and watermark_url_image are None
        """
        if store_name is None and watermark_url_image is None:
            raise ValueError("At least one field must be provided for update")
        
        # Use database only
        # Build dynamic update query
        update_fields = []
        params = []
        
        if store_name is not None:
            if not store_name.strip():
                raise ValueError("Store name cannot be empty")
            update_fields.append("store_name = %s")
            params.append(store_name.strip())
        
        if watermark_url_image is not None:
            if not watermark_url_image.strip():
                raise ValueError("Watermark image URL cannot be empty")
            update_fields.append("watermark_url_image = %s")
            params.append(watermark_url_image.strip())
        
        # Add timestamp update
        if self.db_manager.db_type == 'postgresql':
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
        elif self.db_manager.db_type == 'mysql':
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
        elif self.db_manager.db_type == 'sqlite':
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"""
            UPDATE watermarks 
            SET {', '.join(update_fields)}
            WHERE watermark_id = %s
        """
        
        if self.db_manager.db_type == 'sqlite':
            query = query.replace('%s', '?')
        
        params.append(watermark_id)
        
        # Execute update
        self.db_manager.execute_query(query, tuple(params), fetch=False)
        
        # Get updated watermark
        return self.get_watermark_by_id(watermark_id)
    
    def delete_watermark(self, watermark_id: int) -> bool:
        """
        Delete a watermark by ID
        
        Args:
            watermark_id: ID of the watermark to delete
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        # Use database only
        query = """
            DELETE FROM watermarks 
            WHERE watermark_id = %s
        """
        
        if self.db_manager.db_type == 'sqlite':
            query = query.replace('%s', '?')
        
        # Check if watermark exists first
        existing = self.get_watermark_by_id(watermark_id)
        if existing:
            self.db_manager.execute_query(query, (watermark_id,), fetch=False)
            return True
        return False
    
    def search_watermarks(self, query: str) -> List[Watermark]:
        """
        Search watermarks by store name (case-insensitive partial match)
        
        Args:
            query: Search query string
            
        Returns:
            List[Watermark]: List of matching watermark objects
        """
        if not query or not query.strip():
            return []
        
        # Use database only
        if self.db_manager.db_type == 'postgresql':
            search_query = """
                SELECT watermark_id, store_name, watermark_url_image 
                FROM watermarks 
                WHERE store_name ILIKE %s
                ORDER BY watermark_id
            """
        elif self.db_manager.db_type == 'mysql':
            search_query = """
                SELECT watermark_id, store_name, watermark_url_image 
                FROM watermarks 
                WHERE store_name LIKE %s
                ORDER BY watermark_id
            """
        else:  # SQLite
            search_query = """
                SELECT watermark_id, store_name, watermark_url_image 
                FROM watermarks 
                WHERE store_name LIKE ?
                ORDER BY watermark_id
            """
        
        search_pattern = f"%{query.strip()}%"
        
        if self.db_manager.db_type == 'sqlite':
            result = self.db_manager.execute_query(search_query, (search_pattern,))
        else:
            result = self.db_manager.execute_query(search_query, (search_pattern,))
        
        if result:
            return [Watermark.from_dict(w) for w in result]
        
        return []
