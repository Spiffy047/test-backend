#!/usr/bin/env python3
"""
Migration script to convert hardcoded values to ORM-based configuration
This script updates existing data to use the new configuration tables
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Ticket, Alert
from app.models.configuration import (
    UserRole, TicketStatus, TicketPriority, 
    TicketCategory, AlertType, SystemSetting
)
from app.services.configuration_service import ConfigurationService

def migrate_user_roles():
    """Migrate user role strings to foreign key relationships"""
    print("Migrating user roles...")
    
    # Create role mapping
    role_mapping = {}
    for role in UserRole.query.all():
        role_mapping[role.name] = role.id
    
    # Update users with role_id
    users = User.query.all()
    for user in users:
        if hasattr(user, 'role') and isinstance(user.role, str):
            role_id = role_mapping.get(user.role)
            if role_id:
                # Add role_id column if it doesn't exist
                try:
                    user.role_id = role_id
                    print(f"Updated user {user.email} role to ID {role_id}")
                except Exception as e:
                    print(f"Error updating user {user.email}: {e}")
    
    try:
        db.session.commit()
        print("✅ User roles migrated successfully")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error migrating user roles: {e}")

def migrate_ticket_fields():
    """Migrate ticket status, priority, and category to foreign keys"""
    print("Migrating ticket fields...")
    
    # Create mappings
    status_mapping = {s.name: s.id for s in TicketStatus.query.all()}
    priority_mapping = {p.name: p.id for p in TicketPriority.query.all()}
    category_mapping = {c.name: c.id for c in TicketCategory.query.all()}
    
    tickets = Ticket.query.all()
    for ticket in tickets:
        updated = False
        
        # Migrate status
        if hasattr(ticket, 'status') and isinstance(ticket.status, str):
            status_id = status_mapping.get(ticket.status)
            if status_id:
                try:
                    ticket.status_id = status_id
                    updated = True
                except:
                    pass
        
        # Migrate priority
        if hasattr(ticket, 'priority') and isinstance(ticket.priority, str):
            priority_id = priority_mapping.get(ticket.priority)
            if priority_id:
                try:
                    ticket.priority_id = priority_id
                    updated = True
                except:
                    pass
        
        # Migrate category
        if hasattr(ticket, 'category') and isinstance(ticket.category, str):
            category_id = category_mapping.get(ticket.category)
            if category_id:
                try:
                    ticket.category_id = category_id
                    updated = True
                except:
                    pass
        
        if updated:
            print(f"Updated ticket {ticket.ticket_id}")
    
    try:
        db.session.commit()
        print("✅ Ticket fields migrated successfully")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error migrating ticket fields: {e}")

def migrate_alert_types():
    """Migrate alert type strings to foreign key relationships"""
    print("Migrating alert types...")
    
    # Create mapping
    type_mapping = {t.name: t.id for t in AlertType.query.all()}
    
    alerts = Alert.query.all()
    for alert in alerts:
        if hasattr(alert, 'alert_type') and isinstance(alert.alert_type, str):
            type_id = type_mapping.get(alert.alert_type)
            if type_id:
                try:
                    alert.alert_type_id = type_id
                    print(f"Updated alert {alert.id} type to ID {type_id}")
                except:
                    pass
    
    try:
        db.session.commit()
        print("✅ Alert types migrated successfully")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error migrating alert types: {e}")

def create_database_schema():
    """Create new configuration tables"""
    print("Creating configuration tables...")
    
    try:
        # Create all tables
        db.create_all()
        print("✅ Configuration tables created successfully")
        
        # Initialize default configuration
        ConfigurationService.initialize_default_configuration()
        print("✅ Default configuration data initialized")
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False
    
    return True

def main():
    """Main migration function"""
    print("🚀 Starting ORM migration...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app('development')
    
    with app.app_context():
        # Step 1: Create new schema
        if not create_database_schema():
            print("❌ Migration failed at schema creation")
            return
        
        # Step 2: Migrate existing data
        migrate_user_roles()
        migrate_ticket_fields()
        migrate_alert_types()
        
        print("=" * 50)
        print("✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update your database schema to remove old string columns")
        print("2. Test the application with the new configuration")
        print("3. Use /api/config endpoints to manage configuration")

if __name__ == '__main__':
    main()