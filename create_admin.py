#!/usr/bin/env python3
"""
Simple script to create admin user directly via database connection
"""

import os
import psycopg2
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database connection
DATABASE_URL = 'postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a/hotfix'

def create_users():
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create users table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'Normal User',
                is_verified BOOLEAN DEFAULT true,
                verification_token VARCHAR(100),
                token_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Users to create
        users = [
            ('Admin User', 'admin@company.com', 'System Admin'),
            ('John Smith', 'john.smith@company.com', 'Normal User'),
            ('Sarah Johnson', 'sarah.johnson@company.com', 'Technical User'),
            ('Lisa Rodriguez', 'lisa.rodriguez@company.com', 'Technical Supervisor')
        ]
        
        # Create each user
        for name, email, role in users:
            password_hash = generate_password_hash('password123')
            
            try:
                cur.execute("""
                    INSERT INTO users (name, email, password_hash, role, is_verified, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                """, (name, email, password_hash, role, True, datetime.utcnow()))
                
                print(f"✅ Created user: {email}")
            except Exception as e:
                print(f"❌ Failed to create {email}: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify users were created
        cur.execute("SELECT name, email, role FROM users ORDER BY id")
        users = cur.fetchall()
        
        print(f"\n📊 Total users in database: {len(users)}")
        for user in users:
            print(f"  - {user[0]} ({user[1]}) - {user[2]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("Creating users in PostgreSQL database...")
    success = create_users()
    
    if success:
        print("\n✅ Users created successfully!")
        print("Test login: admin@company.com / password123")
    else:
        print("\n❌ Failed to create users")