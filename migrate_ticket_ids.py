#!/usr/bin/env python3
"""
Migration script to update existing ticket IDs to proper TKT-XXXX format
Run this once to fix existing tickets in the live database
"""

from app import create_app, db
from app.models import Ticket
from sqlalchemy import text

def migrate_ticket_ids():
    app = create_app('production')
    
    with app.app_context():
        try:
            # Get all tickets that don't have proper TKT-XXXX format
            tickets = Ticket.query.filter(~Ticket.ticket_id.like('TKT-%')).all()
            
            print(f"Found {len(tickets)} tickets to migrate...")
            
            # Start numbering from 1001
            ticket_counter = 1001
            
            # Check if we already have TKT-XXXX tickets and start from the highest number
            existing_tkt_tickets = db.session.execute(
                text("SELECT ticket_id FROM tickets WHERE ticket_id LIKE 'TKT-%' ORDER BY ticket_id DESC LIMIT 1")
            ).fetchone()
            
            if existing_tkt_tickets:
                try:
                    last_num = int(existing_tkt_tickets[0].split('-')[1])
                    ticket_counter = last_num + 1
                    print(f"Starting from TKT-{ticket_counter:04d}")
                except (ValueError, IndexError):
                    print("Starting from TKT-1001")
            
            # Update each ticket
            for ticket in tickets:
                old_id = ticket.ticket_id
                new_id = f"TKT-{ticket_counter:04d}"
                
                # Make sure this ID doesn't already exist
                while Ticket.query.filter_by(ticket_id=new_id).first():
                    ticket_counter += 1
                    new_id = f"TKT-{ticket_counter:04d}"
                
                ticket.ticket_id = new_id
                print(f"Updated: {old_id} -> {new_id}")
                ticket_counter += 1
            
            # Commit all changes
            db.session.commit()
            print(f"Successfully migrated {len(tickets)} tickets!")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_ticket_ids()