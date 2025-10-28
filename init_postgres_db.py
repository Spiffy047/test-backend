#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script
Run this to create tables and populate with sample data
"""

import os
import psycopg2
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_database():
    # Database connection from environment variables
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Connected to PostgreSQL database")
        
        # Drop existing tables
        print("Dropping existing tables...")
        cur.execute("DROP TABLE IF EXISTS activities CASCADE;")
        cur.execute("DROP TABLE IF EXISTS files CASCADE;")
        cur.execute("DROP TABLE IF EXISTS messages CASCADE;")
        cur.execute("DROP TABLE IF EXISTS tickets CASCADE;")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")
        
        # Create users table
        print("Creating users table...")
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'Normal User',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create tickets table
        print("Creating tickets table...")
        cur.execute("""
            CREATE TABLE tickets (
                id SERIAL PRIMARY KEY,
                ticket_id VARCHAR(20) UNIQUE NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'New',
                priority VARCHAR(20) NOT NULL,
                category VARCHAR(50) NOT NULL,
                created_by INTEGER NOT NULL REFERENCES users(id),
                assigned_to INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                resolved_at TIMESTAMP,
                sla_violated BOOLEAN DEFAULT FALSE
            );
        """)
        
        # Create messages table
        print("Creating messages table...")
        cur.execute("""
            CREATE TABLE messages (
                id SERIAL PRIMARY KEY,
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                sender_id INTEGER NOT NULL REFERENCES users(id),
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create files table
        print("Creating files table...")
        cur.execute("""
            CREATE TABLE files (
                id SERIAL PRIMARY KEY,
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER NOT NULL,
                uploaded_by INTEGER NOT NULL REFERENCES users(id),
                uploaded_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create activities table
        print("Creating activities table...")
        cur.execute("""
            CREATE TABLE activities (
                id SERIAL PRIMARY KEY,
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id),
                action VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Insert sample users
        print("Inserting sample users...")
        password_hash = generate_password_hash('password123')
        
        users_data = [
            ('John Smith', 'john.smith@company.com', password_hash, 'Normal User'),
            ('Sarah Johnson', 'sarah.johnson@company.com', password_hash, 'Technical User'),
            ('Mike Chen', 'mike.chen@company.com', password_hash, 'Technical Supervisor'),
            ('Admin User', 'admin@company.com', password_hash, 'System Admin'),
            ('Emily Rodriguez', 'emily.rodriguez@company.com', password_hash, 'Technical User'),
            ('David Kim', 'david.kim@company.com', password_hash, 'Technical User')
        ]
        
        cur.executemany("""
            INSERT INTO users (name, email, password_hash, role) 
            VALUES (%s, %s, %s, %s)
        """, users_data)
        
        # Insert sample tickets
        print("Inserting sample tickets...")
        tickets_data = [
            ('TKT-1001', 'Unable to access company email', 'I am having trouble accessing my email. The error message says authentication failed.', 'Open', 'High', 'Software', 1, 2, False),
            ('TKT-1002', 'Laptop running very slow', 'My laptop has been running extremely slow for the past few days. It takes forever to open applications.', 'New', 'Medium', 'Hardware', 1, None, False),
            ('TKT-1003', 'VPN connection issues', 'Cannot connect to company VPN from home. Getting timeout errors.', 'Pending', 'High', 'Network', 1, 5, True),
            ('TKT-1004', 'Printer not working', 'Office printer is not responding. Shows offline status.', 'Closed', 'Low', 'Hardware', 1, 2, False),
            ('TKT-1005', 'Password reset request', 'Need to reset my Active Directory password.', 'Open', 'Medium', 'Access', 1, 6, False)
        ]
        
        cur.executemany("""
            INSERT INTO tickets (ticket_id, title, description, status, priority, category, created_by, assigned_to, sla_violated) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tickets_data)
        
        # Insert sample messages
        print("Inserting sample messages...")
        messages_data = [
            (1, 1, 'I am having trouble accessing my email. The error message says authentication failed.'),
            (1, 2, 'Hi John, I can help you with this. Can you please try resetting your password first?'),
            (1, 1, 'I tried resetting the password but still getting the same error.'),
            (2, 1, 'My laptop has been running extremely slow for the past few days.'),
            (3, 1, 'Cannot connect to company VPN from home. Getting timeout errors.'),
            (3, 5, 'I will check the VPN server logs and get back to you.')
        ]
        
        cur.executemany("""
            INSERT INTO messages (ticket_id, sender_id, message) 
            VALUES (%s, %s, %s)
        """, messages_data)
        
        # Insert sample activities
        print("Inserting sample activities...")
        activities_data = [
            (1, 2, 'assignment', 'Ticket assigned to Sarah Johnson'),
            (1, 2, 'status_change', 'Status changed from New to Open'),
            (3, 5, 'assignment', 'Ticket assigned to Emily Rodriguez'),
            (3, 5, 'status_change', 'Status changed from Open to Pending'),
            (4, 2, 'status_change', 'Status changed from Open to Closed')
        ]
        
        cur.executemany("""
            INSERT INTO activities (ticket_id, user_id, action, description) 
            VALUES (%s, %s, %s, %s)
        """, activities_data)
        
        # Create indexes
        print("Creating indexes...")
        cur.execute("CREATE INDEX idx_tickets_created_by ON tickets(created_by);")
        cur.execute("CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);")
        cur.execute("CREATE INDEX idx_tickets_status ON tickets(status);")
        cur.execute("CREATE INDEX idx_messages_ticket_id ON messages(ticket_id);")
        cur.execute("CREATE INDEX idx_activities_ticket_id ON activities(ticket_id);")
        
        # Commit all changes
        conn.commit()
        
        # Verify data
        cur.execute("SELECT COUNT(*) FROM users;")
        user_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM tickets;")
        ticket_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM messages;")
        message_count = cur.fetchone()[0]
        
        print(f"\nDatabase initialization completed successfully!")
        print(f"Users created: {user_count}")
        print(f"Tickets created: {ticket_count}")
        print(f"Messages created: {message_count}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    init_database()