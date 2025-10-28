import psycopg2
import os
from datetime import datetime, timedelta
import random

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://servicedesk_user:servicedesk_pass@localhost/servicedesk_db')

def recreate_tickets():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Deleting existing tickets...")
        cur.execute("DELETE FROM tickets")
        
        print("Resetting sequence...")
        cur.execute("ALTER SEQUENCE tickets_id_seq RESTART WITH 1001")
        
        # Sample tickets
        tickets = [
            ('Password Reset Request', 'Unable to access email account, need password reset', 'Medium', 'Account Access', 'Open', 1, 2),
            ('Software Installation Issue', 'Microsoft Office installation failing on Windows 10', 'High', 'Software', 'In Progress', 1, 2),
            ('Network Connectivity Problem', 'Cannot connect to company VPN from home', 'High', 'Network', 'Open', 1, 3),
            ('Printer Not Working', 'Office printer showing error message', 'Low', 'Hardware', 'Resolved', 1, 2),
            ('Email Sync Issues', 'Outlook not syncing with mobile device', 'Medium', 'Email', 'Pending', 1, 3),
            ('System Slow Performance', 'Computer running very slowly after update', 'Medium', 'Hardware', 'Open', 1, 2),
            ('Access Card Not Working', 'Employee access card not opening doors', 'High', 'Security', 'In Progress', 1, 3),
            ('Phone System Down', 'Office phone system not receiving calls', 'Critical', 'Communication', 'Open', 1, 2)
        ]
        
        print(f"Creating {len(tickets)} sample tickets...")
        for i, (title, desc, priority, category, status, user_id, assigned_to) in enumerate(tickets, 1001):
            ticket_number = f"TKT-{i}"
            created_at = datetime.now() - timedelta(days=random.randint(0, 30))
            
            cur.execute("""
                INSERT INTO tickets (ticket_number, title, description, priority, category, status, user_id, assigned_to, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (ticket_number, title, desc, priority, category, status, user_id, assigned_to, created_at, created_at))
        
        conn.commit()
        print(f"✅ Successfully created {len(tickets)} tickets with proper TKT-XXXX format!")
        
        # Verify results
        cur.execute("SELECT ticket_number, title FROM tickets ORDER BY id")
        results = cur.fetchall()
        print("\nCreated tickets:")
        for ticket_num, title in results:
            print(f"  {ticket_num}: {title}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    recreate_tickets()