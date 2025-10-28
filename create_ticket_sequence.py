#!/usr/bin/env python3
"""
Create ticket sequence in PostgreSQL database if it doesn't exist
"""
import os
import psycopg2
from urllib.parse import urlparse

# Database connection string
DATABASE_URL = "postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a/hotfix"

def create_ticket_sequence():
    """Create ticket sequence if it doesn't exist"""
    
    # Parse database URL
    url = urlparse(DATABASE_URL)
    
    # Connect to database
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        database=url.path[1:],  # Remove leading slash
        user=url.username,
        password=url.password
    )
    
    try:
        cursor = conn.cursor()
        
        # Check if sequence exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.sequences 
                WHERE sequence_name = 'ticket_id_seq'
            )
        """)
        
        sequence_exists = cursor.fetchone()[0]
        
        if not sequence_exists:
            print("Creating ticket_id_seq sequence...")
            
            # Get current max ticket number
            cursor.execute("""
                SELECT COUNT(*) FROM tickets
            """)
            ticket_count = cursor.fetchone()[0]
            
            # Start sequence from 1001 or next available number
            start_value = max(1001, ticket_count + 1001)
            
            cursor.execute(f"""
                CREATE SEQUENCE ticket_id_seq 
                START WITH {start_value} 
                INCREMENT BY 1
            """)
            
            conn.commit()
            print(f"✅ Created ticket_id_seq starting from {start_value}")
        else:
            print("✅ ticket_id_seq sequence already exists")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔧 Creating ticket sequence...")
    create_ticket_sequence()
    print("✨ Done!")