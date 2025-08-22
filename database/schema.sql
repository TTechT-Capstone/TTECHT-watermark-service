-- database/schema.sql
-- Database schema for watermark service

-- PostgreSQL/MySQL Schema
CREATE TABLE IF NOT EXISTS watermarks (
    watermark_id SERIAL PRIMARY KEY,  -- PostgreSQL: SERIAL, MySQL: INT AUTO_INCREMENT
    store_name VARCHAR(255) NOT NULL,
    watermark_url_image TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_watermarks_store_name ON watermarks(store_name);
CREATE INDEX IF NOT EXISTS idx_watermarks_created_at ON watermarks(created_at);

-- SQLite Schema (alternative)
-- CREATE TABLE IF NOT EXISTS watermarks (
--     watermark_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     store_name TEXT NOT NULL,
--     watermark_url_image TEXT NOT NULL,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
-- );

-- Create a view for easy watermark retrieval
CREATE OR REPLACE VIEW watermark_summary AS
SELECT 
    watermark_id,
    store_name,
    watermark_url_image,
    created_at,
    updated_at
FROM watermarks
ORDER BY created_at DESC;

-- Sample data insertion (optional)
-- INSERT INTO watermarks (store_name, watermark_url_image) VALUES 
--     ('Sample Store', 'https://example.com/sample-logo.png'),
--     ('Test Brand', 'https://example.com/test-brand.png');

-- Comments on table structure
COMMENT ON TABLE watermarks IS 'Stores watermark information for different stores/brands';
COMMENT ON COLUMN watermarks.watermark_id IS 'Unique identifier for each watermark';
COMMENT ON COLUMN watermarks.store_name IS 'Name of the store or brand';
COMMENT ON COLUMN watermarks.watermark_url_image IS 'URL or file path to the watermark image';
COMMENT ON COLUMN watermarks.created_at IS 'Timestamp when the watermark was created';
COMMENT ON COLUMN watermarks.updated_at IS 'Timestamp when the watermark was last updated';
