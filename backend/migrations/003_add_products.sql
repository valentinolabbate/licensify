-- Migration: Add Products table and update Licenses table
-- Run this on your PostgreSQL database

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    version VARCHAR(50),
    available_features JSON DEFAULT '[]',
    default_max_devices INTEGER DEFAULT 1,
    default_license_type VARCHAR(50) DEFAULT 'limited',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on slug for faster lookups
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);

-- Add product_id column to licenses table
ALTER TABLE licenses 
ADD COLUMN IF NOT EXISTS product_id INTEGER REFERENCES products(id) ON DELETE SET NULL;

-- Create index on product_id for faster joins
CREATE INDEX IF NOT EXISTS idx_licenses_product_id ON licenses(product_id);

-- Add features column to licenses table
ALTER TABLE licenses 
ADD COLUMN IF NOT EXISTS features JSON DEFAULT '[]';

-- Add price column to licenses table if not exists
ALTER TABLE licenses 
ADD COLUMN IF NOT EXISTS price DECIMAL(10, 2);

-- Add note column to licenses table if not exists
ALTER TABLE licenses 
ADD COLUMN IF NOT EXISTS note TEXT;

-- Update trigger for updated_at on products
CREATE OR REPLACE FUNCTION update_products_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_products_updated_at ON products;
CREATE TRIGGER trigger_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_products_updated_at();

-- Verify changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'products';

SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'licenses' 
AND column_name IN ('product_id', 'features', 'price', 'note');
