#!/usr/bin/env python3
import psycopg2

def fix_user_auth_emails():
    db_url = "postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a.oregon-postgres.render.com/hotfix"
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Get user emails from users table
        cur.execute("SELECT id, email FROM users ORDER BY id;")
        users = cur.fetchall()
        
        # Update user_auth emails to match users table
        updates = [
            ("john.smith@company.com", "auth1"),
            ("jane.doe@company.com", "auth2"), 
            ("bob.wilson@company.com", "auth3"),
            ("admin@company.com", "auth4")  # Keep admin as is
        ]
        
        for email, auth_id in updates:
            cur.execute("UPDATE user_auth SET email = %s WHERE id = %s;", (email, auth_id))
            print(f"✅ Updated {auth_id} to {email}")
        
        conn.commit()
        print("✅ All user_auth emails updated successfully")
        
        # Verify the changes
        cur.execute("SELECT id, email FROM user_auth;")
        auth_emails = cur.fetchall()
        print("\n📧 Updated user_auth emails:")
        for auth_id, email in auth_emails:
            print(f"  {auth_id}: {email}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_user_auth_emails()