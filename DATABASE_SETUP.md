# Database Setup Guide

This guide explains how to configure the database connection for the watermark service.

## Environment Variables

Create a `.env` file in your project root with the following variables:

### Option 1: DATABASE_URL (Recommended)
This is the simplest and most flexible approach:

```bash
# PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database

# MySQL
DATABASE_URL=mysql://username:password@host:port/database

# SQLite
DATABASE_URL=sqlite:///watermarks.db
```

### Option 2: Individual Parameters (Fallback)
If you prefer separate parameters:

```bash
# Database Type
DATABASE_TYPE=postgresql

# PostgreSQL Configuration
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=watermark_service
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password_here
POSTGRESQL_SSLMODE=prefer

# MySQL Configuration
# DATABASE_TYPE=mysql
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_DATABASE=watermark_service
# MYSQL_USER=root
# MYSQL_PASSWORD=your_password_here

# SQLite Configuration
# DATABASE_TYPE=sqlite
# SQLITE_DATABASE=watermarks.db
```

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup

#### PostgreSQL
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Create database
createdb watermark_service

# Or connect to PostgreSQL and run:
# CREATE DATABASE watermark_service;
```

#### MySQL
```bash
# Install MySQL driver
pip install mysql-connector-python

# Create database
mysql -u root -p
CREATE DATABASE watermark_service;
```

#### SQLite
```bash
# No additional setup needed - SQLite is built into Python
# Database file will be created automatically
```

## Usage Examples

### 1. Basic Setup
The service will automatically:
- Connect to the configured database
- Create the `watermarks` table if it doesn't exist
- Fall back to file-based storage if database connection fails

### 2. Test Database Connection
```python
from config.database_manager import DatabaseManager

# Test connection
db_manager = DatabaseManager()
try:
    if db_manager.test_connection():
        print("Database connection successful!")
        db_manager.create_tables()
        print("Tables created/verified successfully!")
    else:
        print("Database connection failed!")
except Exception as e:
    print(f"Database error: {e}")
```

### 3. Environment File Examples

#### PostgreSQL with DATABASE_URL
```bash
# .env
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/watermark_service
```

#### MySQL with DATABASE_URL
```bash
# .env
DATABASE_URL=mysql://root:mypassword@localhost:3306/watermark_service
```

#### SQLite with DATABASE_URL
```bash
# .env
DATABASE_URL=sqlite:///watermarks.db
```

#### PostgreSQL with individual parameters
```bash
# .env
DATABASE_TYPE=postgresql
POSTGRESQL_HOST=your-db-host.com
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=watermark_service
POSTGRESQL_USER=your_username
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_SSLMODE=require
```

## Database Schema

The service automatically creates this table structure:

```sql
CREATE TABLE watermarks (
    watermark_id SERIAL PRIMARY KEY,  -- PostgreSQL
    -- watermark_id INT AUTO_INCREMENT PRIMARY KEY,  -- MySQL
    -- watermark_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    
    store_name VARCHAR(255) NOT NULL,
    watermark_url_image TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_watermarks_store_name ON watermarks(store_name);
```

## Troubleshooting

### Connection Issues
1. Check if database server is running
2. Verify connection parameters in `.env` file
3. Ensure database exists
4. Check user permissions

### Driver Issues
1. Install correct database driver:
   - PostgreSQL: `psycopg2-binary`
   - MySQL: `mysql-connector-python`
   - SQLite: Built-in (no driver needed)

### Fallback Mode
If database connection fails, the service automatically falls back to file-based storage in the system's temporary directory. Check console output for warnings.

### DATABASE_URL Format Issues
- **PostgreSQL**: `postgresql://user:pass@host:port/db`
- **MySQL**: `mysql://user:pass@host:port/db`
- **SQLite**: `sqlite:///path/to/file.db`

## Security Notes

1. Never commit `.env` files to version control
2. Use strong passwords for database users
3. Consider using connection pooling for production
4. Enable SSL for remote database connections
5. DATABASE_URL is parsed securely with proper URL parsing
