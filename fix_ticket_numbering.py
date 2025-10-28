#!/usr/bin/env python3
"""
Fix ticket numbering in PostgreSQL database to use TKT-1001, TKT-1002 format
"""
import os
import psycopg2
from urllib.parse import urlparse

# Database connection string
DATABASE_URL = "postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a/hotfix"

def fix_ticket_numbering():
    """Fix ticket numbering to TKT-XXXX format starting from 1001"""
    
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
        
        # Get all tickets ordered by creation date
        cursor.execute("""
            SELECT id, created_at 
            FROM tickets 
            ORDER BY created_at ASC
        """)
        
        tickets = cursor.fetchall()
        print(f"Found {len(tickets)} tickets to renumber")
        
        # Create a mapping of old IDs to new IDs
        id_mapping = {}
        
        for i, (old_id, created_at) in enumerate(tickets, start=1001):
            new_id = f"TKT-{i:04d}"
            id_mapping[old_id] = new_id
            print(f"Mapping {old_id} -> {new_id}")
        
        # Update tickets table
        print("\nUpdating tickets table...")
        for old_id, new_id in id_mapping.items():
            cursor.execute("""
                UPDATE tickets 
                SET id = %s 
                WHERE id = %s
            """, (new_id, old_id))
        
        # Update related tables with foreign key references
        print("Updating ticket_messages table...")
        for old_id, new_id in id_mapping.items():
            cursor.execute("""
                UPDATE ticket_messages 
                SET ticket_id = %s 
                WHERE ticket_id = %s
            """, (new_id, old_id))
        
        print("Updating ticket_activities table...")
        for old_id, new_id in id_mapping.items():
            cursor.execute("""
                UPDATE ticket_activities 
                SET ticket_id = %s 
                WHERE ticket_id = %s
            """, (new_id, old_id))
        
        # Update alerts table if it exists
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'alerts'
            """)
            if cursor.fetchone()[0] > 0:
                print("Updating alerts table...")
                for old_id, new_id in id_mapping.items():
                    cursor.execute("""
                        UPDATE alerts 
                        SET ticket_id = %s 
                        WHERE ticket_id = %s
                    """, (new_id, old_id))
        except Exception as e:
            print(f"Note: Could not update alerts table: {e}")
        
        # Create or update sequence for future ticket numbering
        print("Setting up ticket sequence...")
        next_number = len(tickets) + 1001
        
        cursor.execute("""
            DROP SEQUENCE IF EXISTS ticket_id_seq CASCADE
        """)
        
        cursor.execute(f"""
            CREATE SEQUENCE ticket_id_seq 
            START WITH {next_number} 
            INCREMENT BY 1
        """)
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ Successfully renumbered {len(tickets)} tickets!")
        print(f"Next ticket will be: TKT-{next_number:04d}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔧 Fixing ticket numbering in PostgreSQL database...")
    fix_ticket_numbering()
    print("✨ Done!")