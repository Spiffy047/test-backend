#!/usr/bin/env python3
import psycopg2

def fix_admin_role():
    db_url = "postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a.oregon-postgres.render.com/hotfix"
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Find admin user and update role
        cur.execute("SELECT id, name, email, role FROM users WHERE email = 'admin@company.com';")
        admin = cur.fetchone()
        
        if admin:
            print(f"Current admin: ID {admin[0]}, Name: {admin[1]}, Role: {admin[3]}")
            
            # Update to System Admin role
            cur.execute("UPDATE users SET role = 'System Admin' WHERE email = 'admin@company.com';")
            conn.commit()
            print("✅ Updated admin role to 'System Admin'")
        else:
            # Create admin user if doesn't exist
            cur.execute("INSERT INTO users (name, email, role) VALUES ('Admin User', 'admin@company.com', 'System Admin');")
            conn.commit()
            print("✅ Created admin user with System Admin role")
        
        # Verify the change
        cur.execute("SELECT id, name, email, role FROM users WHERE email = 'admin@company.com';")
        admin = cur.fetchone()
        print(f"Updated admin: ID {admin[0]}, Name: {admin[1]}, Role: {admin[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_admin_role()