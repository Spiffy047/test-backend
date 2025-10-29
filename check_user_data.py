#!/usr/bin/env python3
import psycopg2

def check_user_data():
    db_url = "postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a.oregon-postgres.render.com/hotfix"
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check users table structure and data
        cur.execute("SELECT id, name, email, role FROM users LIMIT 10;")
        users = cur.fetchall()
        print("👥 Users table:")
        for user in users:
            print(f"  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Role: {user[3]}")
        
        # Check user_auth table if it exists
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'user_auth';")
        auth_columns = [row[0] for row in cur.fetchall()]
        if auth_columns:
            print(f"\n🔐 user_auth columns: {auth_columns}")
            cur.execute("SELECT * FROM user_auth LIMIT 5;")
            auth_data = cur.fetchall()
            print("🔐 user_auth data:")
            for row in auth_data:
                print(f"  {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_user_data()