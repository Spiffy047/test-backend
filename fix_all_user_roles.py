#!/usr/bin/env python3
import psycopg2

def fix_all_user_roles():
    db_url = "postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a.oregon-postgres.render.com/hotfix"
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Define correct user roles
        user_roles = [
            ('john.smith@company.com', 'Normal User'),
            ('jane.doe@company.com', 'Normal User'),
            ('bob.wilson@company.com', 'Normal User'),
            ('alice.johnson@company.com', 'Normal User'),
            ('charlie.brown@company.com', 'Normal User'),
            ('diana.prince@company.com', 'Normal User'),
            ('edward.norton@company.com', 'Normal User'),
            ('fiona.green@company.com', 'Normal User'),
            ('sarah.johnson@company.com', 'Technical User'),
            ('mike.chen@company.com', 'Technical User'),
            ('alex.rivera@company.com', 'Technical User'),
            ('lisa.rodriguez@company.com', 'Technical Supervisor'),
            ('david.kim@company.com', 'Technical Supervisor'),
            ('admin@company.com', 'System Admin'),
            ('superadmin@company.com', 'System Admin')
        ]
        
        # Update each user's role
        for email, role in user_roles:
            cur.execute("UPDATE users SET role = %s WHERE email = %s;", (role, email))
            print(f"✅ Updated {email} to {role}")
        
        conn.commit()
        print("\n✅ All user roles updated successfully")
        
        # Verify the changes
        cur.execute("SELECT email, role FROM users ORDER BY id;")
        users = cur.fetchall()
        print("\n📋 Updated user roles:")
        for email, role in users:
            print(f"  {email}: {role}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_all_user_roles()