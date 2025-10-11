-- Create banners table for production
-- Run this in Railway PostgreSQL console

CREATE TABLE IF NOT EXISTS banners (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(500),
    description VARCHAR(1000),
    image_url VARCHAR(500) NOT NULL,
    mobile_image_url VARCHAR(500),
    banner_type VARCHAR(50) NOT NULL DEFAULT 'hero',
    cta_text VARCHAR(100),
    cta_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE
);

-- Create index on banner_type for faster queries
CREATE INDEX IF NOT EXISTS idx_banners_type ON banners(banner_type);
CREATE INDEX IF NOT EXISTS idx_banners_active ON banners(is_active);
CREATE INDEX IF NOT EXISTS idx_banners_display_order ON banners(display_order);

-- Create enum type for banner_type (PostgreSQL enum)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'bannertype') THEN
        CREATE TYPE bannertype AS ENUM ('hero', 'promo', 'category');
    END IF;
END $$;

-- Alter column to use enum (if table already exists)
-- ALTER TABLE banners ALTER COLUMN banner_type TYPE bannertype USING banner_type::bannertype;

