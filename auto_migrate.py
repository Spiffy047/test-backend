import os
import psycopg2
from urllib.parse import urlparse

def run_migration():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("No DATABASE_URL found")
        return
    
    try:
        # Parse database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]  # Remove leading slash
        )
        
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name IN ('is_verified', 'verification_token', 'token_expires_at');
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add missing columns
        if 'is_verified' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT TRUE;")
            print("Added is_verified column")
        
        if 'verification_token' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN verification_token VARCHAR(100);")
            print("Added verification_token column")
        
        if 'token_expires_at' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN token_expires_at TIMESTAMP;")
            print("Added token_expires_at column")
        
        # Set existing users as verified
        cursor.execute("UPDATE users SET is_verified = TRUE WHERE is_verified IS NULL;")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == '__main__':
    run_migration()