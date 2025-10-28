import os
import psycopg2
from datetime import datetime, timedelta
import random

# Try to connect using environment variable or fallback
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    print("Set it with: export DATABASE_URL='your_postgres_connection_string'")
    exit(1)

def recreate_tickets():
    try:
        print(f"Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Connected successfully")
        
        # Check current tickets
        cur.execute("SELECT COUNT(*) FROM tickets")
        count = cur.fetchone()[0]
        print(f"Current tickets in database: {count}")
        
        # Delete all tickets
        print("Deleting all existing tickets...")
        cur.execute("DELETE FROM tickets")
        
        # Reset sequence
        print("Resetting ID sequence...")
        cur.execute("ALTER SEQUENCE tickets_id_seq RESTART WITH 1001")
        
        # Create sample tickets
        sample_tickets = [
            ('Password Reset Request', 'Unable to access email account, need password reset', 'Medium', 'Account Access', 'Open', 1, 2),
            ('Software Installation Issue', 'Microsoft Office installation failing on Windows 10', 'High', 'Software', 'In Progress', 1, 2),
            ('Network Connectivity Problem', 'Cannot connect to company VPN from home', 'High', 'Network', 'Open', 1, 3),
            ('Printer Not Working', 'Office printer showing error message', 'Low', 'Hardware', 'Resolved', 1, 2),
            ('Email Sync Issues', 'Outlook not syncing with mobile device', 'Medium', 'Email', 'Pending', 1, 3),
            ('System Performance Issues', 'Computer running very slowly after update', 'Medium', 'Hardware', 'Open', 1, 2),
            ('Access Card Malfunction', 'Employee access card not opening doors', 'High', 'Security', 'In Progress', 1, 3),
            ('Phone System Outage', 'Office phone system not receiving calls', 'Critical', 'Communication', 'Open', 1, 2)
        ]
        
        print(f"Creating {len(sample_tickets)} new tickets...")
        
        for i, (title, desc, priority, category, status, user_id, assigned_to) in enumerate(sample_tickets, 1001):
            ticket_number = f"TKT-{i}"
            created_at = datetime.now() - timedelta(days=random.randint(0, 30))
            
            cur.execute("""
                INSERT INTO tickets (ticket_number, title, description, priority, category, status, user_id, assigned_to, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (ticket_number, title, desc, priority, category, status, user_id, assigned_to, created_at, created_at))
        
        conn.commit()
        
        # Verify results
        cur.execute("SELECT ticket_number, title, status FROM tickets ORDER BY id")
        results = cur.fetchall()
        
        print(f"\n✅ Successfully created {len(results)} tickets!")
        print("\nTickets created:")
        for ticket_num, title, status in results:
            print(f"  {ticket_num}: {title} [{status}]")
        
        cur.close()
        conn.close()
        
        print(f"\n🎉 Ticket numbering fixed! All tickets now use TKT-XXXX format.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    recreate_tickets()