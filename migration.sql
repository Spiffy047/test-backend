-- Add verification columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS verification_token VARCHAR(100),
ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP;

-- Set existing users as verified
UPDATE users SET is_verified = TRUE WHERE is_verified IS NULL OR is_verified = FALSE;