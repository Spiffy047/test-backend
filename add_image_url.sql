-- Add image_url column to messages table for Cloudinary file storage
-- This migration adds support for storing file URLs in timeline messages

-- Check if column exists and add it if not
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'messages' AND column_name = 'image_url'
    ) THEN
        ALTER TABLE messages ADD COLUMN image_url VARCHAR(500);
        RAISE NOTICE 'Added image_url column to messages table';
    ELSE
        RAISE NOTICE 'image_url column already exists in messages table';
    END IF;
END $$;