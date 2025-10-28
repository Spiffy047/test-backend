#!/usr/bin/env python3
"""
Direct database migration script for live PostgreSQL database
"""

import psycopg2
import os

# Database connection string from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    print("Set it with: export DATABASE_URL='your_database_url'")
    exit(1)

def fix_ticket_ids():
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Connected to live database...")
        
        # Get all tickets that don't have proper TKT-XXXX format
        cur.execute("SELECT id, ticket_id FROM tickets WHERE ticket_id NOT LIKE 'TKT-%' ORDER BY id")
        tickets_to_fix = cur.fetchall()
        
        print(f"Found {len(tickets_to_fix)} tickets to migrate...")
        
        if not tickets_to_fix:
            print("All tickets already have proper TKT-XXXX format!")
            return
        
        # Find the highest existing TKT number
        cur.execute("SELECT ticket_id FROM tickets WHERE ticket_id LIKE 'TKT-%' ORDER BY ticket_id DESC LIMIT 1")
        result = cur.fetchone()
        
        ticket_counter = 1001
        if result:
            try:
                last_num = int(result[0].split('-')[1])
                ticket_counter = last_num + 1
                print(f"Starting from TKT-{ticket_counter:04d}")
            except (ValueError, IndexError):
                print("Starting from TKT-1001")
        else:
            print("Starting from TKT-1001")
        
        # Update each ticket
        for ticket_id, old_ticket_id in tickets_to_fix:
            new_ticket_id = f"TKT-{ticket_counter:04d}"
            
            # Make sure this ID doesn't already exist
            cur.execute("SELECT id FROM tickets WHERE ticket_id = %s", (new_ticket_id,))
            while cur.fetchone():
                ticket_counter += 1
                new_ticket_id = f"TKT-{ticket_counter:04d}"
                cur.execute("SELECT id FROM tickets WHERE ticket_id = %s", (new_ticket_id,))
            
            # Update the ticket
            cur.execute("UPDATE tickets SET ticket_id = %s WHERE id = %s", (new_ticket_id, ticket_id))
            print(f"Updated: {old_ticket_id} -> {new_ticket_id}")
            ticket_counter += 1
        
        # Commit all changes
        conn.commit()
        print(f"Successfully migrated {len(tickets_to_fix)} tickets!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    fix_ticket_ids()