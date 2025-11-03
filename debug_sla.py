#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Ticket, User
from sqlalchemy import func, case

def debug_sla():
    app = create_app()
    with app.app_context():
        try:
            print("=== SLA DEBUG REPORT ===")
            
            # Check total tickets
            total_tickets = Ticket.query.count()
            print(f"Total tickets in database: {total_tickets}")
            
            if total_tickets == 0:
                print("❌ No tickets found - this is why SLA data is empty")
                return
            
            # Check SLA field values
            sla_true = Ticket.query.filter_by(sla_violated=True).count()
            sla_false = Ticket.query.filter_by(sla_violated=False).count()
            sla_null = Ticket.query.filter(Ticket.sla_violated.is_(None)).count()
            
            print(f"SLA violated (True): {sla_true}")
            print(f"SLA met (False): {sla_false}")
            print(f"SLA null: {sla_null}")
            
            # Check ticket statuses
            status_counts = db.session.query(
                Ticket.status, 
                func.count(Ticket.id)
            ).group_by(Ticket.status).all()
            
            print("\nTicket status breakdown:")
            for status, count in status_counts:
                print(f"  {status}: {count}")
            
            # Sample tickets
            print("\nSample tickets:")
            sample_tickets = Ticket.query.limit(5).all()
            for ticket in sample_tickets:
                print(f"  {ticket.ticket_id}: Status={ticket.status}, SLA={ticket.sla_violated}, Priority={ticket.priority}")
            
            # Test the SLA query directly
            print("\n=== TESTING SLA QUERY ===")
            result = db.session.query(
                func.count(Ticket.id).label('total_tickets'),
                func.count(case([(Ticket.sla_violated == False, 1)])).label('on_time'),
                func.count(case([(Ticket.sla_violated == True, 1)])).label('violations')
            ).first()
            
            print(f"Query result - Total: {result.total_tickets}, On-time: {result.on_time}, Violations: {result.violations}")
            
            # Calculate adherence
            total = result.total_tickets or 0
            on_time = result.on_time or 0
            violations = result.violations or 0
            adherence = (on_time / total * 100) if total > 0 else 0
            
            print(f"Calculated SLA adherence: {adherence:.1f}%")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_sla()