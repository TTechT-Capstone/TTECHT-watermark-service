# Database Integration Preparation for Watermark Service

## Overview

The watermark service has been restructured to prepare for database integration. The service is now separated from the image controller and routes, making it easier to integrate with different database systems.

## New Structure

### 1. Separated Controllers and Routes

- **Image Controller** (`controller/image_controller.py`): Handles image processing, watermark embedding, extraction, and detection
- **Watermark Controller** (`controller/watermark_controller.py`): Handles watermark CRUD operations
- **Image Routes** (`routes/image_routes.py`): Image-related API endpoints
- **Watermark Routes** (`routes/watermark_routes.py`): Watermark management API endpoints

### 2. Database Configuration

- **Database Config** (`config/database.py`): Configuration for PostgreSQL, MySQL, and SQLite
- **Database Schema** (`database/schema.sql`): SQL schema for watermark table

### 3. Updated API Endpoints

**Image Processing Endpoints:**
- `POST /api/images/embed-watermark` - Embed watermark into image
- `POST /api/images/extract-watermark` - Extract watermark from image
- `POST /api/images/detect-watermark` - Detect/compare watermarks

**Watermark Management Endpoints:**
- `POST /api/watermarks/` - Create watermark
- `GET /api/watermarks/` - Get all watermarks
- `GET /api/watermarks/<id>` - Get watermark by ID
- `PUT /api/watermarks/<id>` - Update watermark
- `DELETE /api/watermarks/<id>` - Delete watermark
- `GET /api/watermarks/search?q=<query>` - Search watermarks

## Database Integration Steps

### Step 1: Choose Database Type

Set the `DATABASE_TYPE` environment variable in your `.env` file:

```bash
# For PostgreSQL
DATABASE_TYPE=postgresql
POSTGRESQL_HOST=your-db-host.com
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=watermark_service
POSTGRESQL_USER=your_username
POSTGRESQL_PASSWORD=your_password

# For MySQL
DATABASE_TYPE=mysql
MYSQL_HOST=your-db-host.com
MYSQL_PORT=3306
MYSQL_DATABASE=watermark_service
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# For SQLite (local development)
DATABASE_TYPE=sqlite
SQLITE_DATABASE=watermarks.db
```

### Step 2: Install Database Dependencies

Add the appropriate database driver to `requirements.txt`:

```bash
# For PostgreSQL
pip install psycopg2-binary

# For MySQL
pip install mysql-connector-python

# For SQLite (built-in with Python)
# No additional installation needed
```

### Step 3: Update Watermark Service

Replace the file-based storage methods in `service/watermark_service.py` with database operations:

```python
# Example for PostgreSQL with psycopg2
import psycopg2
from config.database import DatabaseConfig

class WatermarkService:
    def __init__(self):
        self.db_config = DatabaseConfig.get_connection_params()
        self.connection = self._get_database_connection()
    
    def _get_database_connection(self):
        return psycopg2.connect(**self.db_config)
    
    def create_watermark(self, store_name: str, watermark_url_image: str) -> Watermark:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO watermarks (store_name, watermark_url_image) VALUES (%s, %s) RETURNING watermark_id",
                (store_name, watermark_url_image)
            )
            watermark_id = cursor.fetchone()[0]
            self.connection.commit()
            
            return Watermark(
                watermark_id=watermark_id,
                store_name=store_name,
                watermark_url_image=watermark_url_image
            )
```

### Step 4: Create Database Tables

Run the SQL schema from `database/schema.sql` on your database:

```bash
# For PostgreSQL
psql -h your-host -U your-user -d your-database -f database/schema.sql

# For MySQL
mysql -h your-host -u your-user -p your-database < database/schema.sql

# For SQLite
sqlite3 watermarks.db < database/schema.sql
```

## Current Status

✅ **Completed:**
- Separated watermark controller and routes
- Database configuration structure
- SQL schema definition
- API endpoint separation
- Updated documentation

🔄 **Next Steps:**
- Provide actual database connection details
- Install database dependencies
- Update watermark service with database operations
- Test database integration

## Benefits of New Structure

1. **Separation of Concerns**: Image processing and watermark management are now separate
2. **Database Agnostic**: Easy to switch between different database types
3. **Scalability**: Database operations can be optimized independently
4. **Maintainability**: Cleaner code organization
5. **Testing**: Easier to test individual components

## Example Database Operations

The watermark service is prepared to handle these database operations:

- **INSERT**: Create new watermarks with auto-incrementing IDs
- **SELECT**: Retrieve watermarks by ID, store name, or search query
- **UPDATE**: Modify existing watermark information
- **DELETE**: Remove watermarks from the database
- **SEARCH**: Case-insensitive search by store name

## Environment Variables

Create a `.env` file in your project root with the appropriate database configuration:

```bash
# Database Configuration
DATABASE_TYPE=postgresql
POSTGRESQL_HOST=your-db-host.com
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=watermark_service
POSTGRESQL_USER=your_username
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_SSLMODE=require

# Existing Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLOUDINARY_UPLOAD_FOLDER=watermark_app/
```

Once you provide the actual database connection details, the service will be ready to use with your database!
