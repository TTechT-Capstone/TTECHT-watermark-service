import json
import os
import tempfile
from typing import List, Dict, Optional
from entity.watermark import Watermark
import uuid

class WatermarkService:
    def __init__(self):
        """Initialize watermark service with storage file"""
        self.storage_file = os.path.join(tempfile.gettempdir(), "watermarks.json")
        self._ensure_storage_exists()
        
        # TODO: Replace with actual database connection
        # self.db_connection = self._get_database_connection()
    
    def _get_database_connection(self):
        """
        Get database connection - to be implemented with actual database
        Example: PostgreSQL, MySQL, SQLite, etc.
        """
        # Placeholder for database connection
        # Example: return psycopg2.connect(DATABASE_URL)
        # Example: return mysql.connector.connect(**DB_CONFIG)
        # Example: return sqlite3.connect('watermarks.db')
        pass
    
    def _ensure_storage_exists(self):
        """Ensure the storage file exists with initial structure"""
        if not os.path.exists(self.storage_file):
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_watermarks(self) -> List[Dict]:
        """Load watermarks from storage file - to be replaced with database query"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_watermarks(self, watermarks: List[Dict]):
        """Save watermarks to storage file - to be replaced with database operations"""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(watermarks, f, ensure_ascii=False, indent=2)
    
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
        
        # TODO: Replace with database INSERT operation
        # Example SQL: INSERT INTO watermarks (store_name, watermark_url_image) VALUES (%s, %s) RETURNING watermark_id
        
        # Load existing watermarks (temporary file-based storage)
        watermarks_data = self._load_watermarks()
        
        # Generate unique watermark ID
        existing_ids = [w.get('watermark_id', 0) for w in watermarks_data]
        watermark_id = max(existing_ids, default=0) + 1
        
        # Create watermark object
        watermark = Watermark(
            watermark_id=watermark_id,
            store_name=store_name.strip(),
            watermark_url_image=watermark_url_image.strip()
        )
        
        # Add to storage (temporary file-based storage)
        watermarks_data.append(watermark.to_dict())
        self._save_watermarks(watermarks_data)
        
        return watermark
    
    def get_watermark_by_id(self, watermark_id: int) -> Optional[Watermark]:
        """
        Get watermark by ID
        
        Args:
            watermark_id: ID of the watermark to retrieve
            
        Returns:
            Watermark: Watermark object if found, None otherwise
        """
        # TODO: Replace with database SELECT operation
        # Example SQL: SELECT watermark_id, store_name, watermark_url_image FROM watermarks WHERE watermark_id = %s
        
        watermarks_data = self._load_watermarks()
        
        for watermark_data in watermarks_data:
            if watermark_data.get('watermark_id') == watermark_id:
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
        # TODO: Replace with database SELECT operation
        # Example SQL: SELECT watermark_id, store_name, watermark_url_image FROM watermarks WHERE store_name = %s
        
        watermarks_data = self._load_watermarks()
        
        for watermark_data in watermarks_data:
            if watermark_data.get('store_name', '').lower() == store_name.lower():
                return Watermark.from_dict(watermark_data)
        
        return None
    
    def get_all_watermarks(self) -> List[Watermark]:
        """
        Get all watermarks
        
        Returns:
            List[Watermark]: List of all watermark objects
        """
        # TODO: Replace with database SELECT operation
        # Example SQL: SELECT watermark_id, store_name, watermark_url_image FROM watermarks ORDER BY watermark_id
        
        watermarks_data = self._load_watermarks()
        return [Watermark.from_dict(w) for w in watermarks_data]
    
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
        
        # TODO: Replace with database UPDATE operation
        # Example SQL: UPDATE watermarks SET store_name = %s, watermark_url_image = %s WHERE watermark_id = %s
        
        watermarks_data = self._load_watermarks()
        
        for i, watermark_data in enumerate(watermarks_data):
            if watermark_data.get('watermark_id') == watermark_id:
                # Update fields if provided
                if store_name is not None:
                    if not store_name.strip():
                        raise ValueError("Store name cannot be empty")
                    watermark_data['store_name'] = store_name.strip()
                
                if watermark_url_image is not None:
                    if not watermark_url_image.strip():
                        raise ValueError("Watermark image URL cannot be empty")
                    watermark_data['watermark_url_image'] = watermark_url_image.strip()
                
                # Save updated data (temporary file-based storage)
                self._save_watermarks(watermarks_data)
                
                # Return updated watermark object
                return Watermark.from_dict(watermark_data)
        
        return None
    
    def delete_watermark(self, watermark_id: int) -> bool:
        """
        Delete a watermark by ID
        
        Args:
            watermark_id: ID of the watermark to delete
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        # TODO: Replace with database DELETE operation
        # Example SQL: DELETE FROM watermarks WHERE watermark_id = %s
        
        watermarks_data = self._load_watermarks()
        
        for i, watermark_data in enumerate(watermarks_data):
            if watermark_data.get('watermark_id') == watermark_id:
                # Remove watermark
                del watermarks_data[i]
                self._save_watermarks(watermarks_data)
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
        
        # TODO: Replace with database LIKE/ILIKE operation
        # Example SQL: SELECT watermark_id, store_name, watermark_url_image FROM watermarks WHERE store_name ILIKE %s
        
        query_lower = query.strip().lower()
        watermarks_data = self._load_watermarks()
        matching_watermarks = []
        
        for watermark_data in watermarks_data:
            store_name = watermark_data.get('store_name', '')
            if query_lower in store_name.lower():
                matching_watermarks.append(Watermark.from_dict(watermark_data))
        
        return matching_watermarks
