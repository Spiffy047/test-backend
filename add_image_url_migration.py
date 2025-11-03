#!/usr/bin/env python3
"""
Database migration script to add image_url column to messages table
Run this script to update existing database schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Add image_url column to messages table"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'messages' AND column_name = 'image_url'
            """))
            
            if result.fetchone():
                print("✓ image_url column already exists in messages table")
                return True
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE messages 
                ADD COLUMN image_url VARCHAR(500)
            """))
            
            conn.commit()
            print("✓ Successfully added image_url column to messages table")
            return True
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("Running database migration: Add image_url to messages table")
    success = run_migration()
    sys.exit(0 if success else 1)