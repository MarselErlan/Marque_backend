-- Fix Banner Enum Type in Production Database
-- Run this in Railway PostgreSQL console

-- Step 1: Check current enum values
SELECT enum_range(NULL::bannertype);

-- Step 2: Convert column to VARCHAR temporarily
ALTER TABLE banners ALTER COLUMN banner_type TYPE VARCHAR(50);

-- Step 3: Drop old enum type
DROP TYPE IF EXISTS bannertype CASCADE;

-- Step 4: Create new enum type with correct lowercase values
CREATE TYPE bannertype AS ENUM ('hero', 'promo', 'category');

-- Step 5: Convert column back to use the enum
ALTER TABLE banners ALTER COLUMN banner_type TYPE bannertype USING banner_type::bannertype;

-- Step 6: Verify the fix
SELECT enum_range(NULL::bannertype);

-- Step 7: Check if any banners exist
SELECT COUNT(*) as banner_count FROM banners;

-- Step 8: View existing banners (if any)
SELECT id, title, banner_type, is_active FROM banners;

