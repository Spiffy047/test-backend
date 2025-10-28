from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
import os
from datetime import datetime, timedelta
import random

recreate_tickets_bp = Blueprint('recreate_tickets', __name__)

@recreate_tickets_bp.route('/api/admin/recreate-tickets', methods=['POST'])
@jwt_required()
def recreate_tickets():
    try:
        current_user = get_jwt_identity()
        if current_user.get('role') != 'System Admin':
            return jsonify({'error': 'Unauthorized'}), 403

        # Database connection
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cur = conn.cursor()

        # Clear existing tickets
        cur.execute("DELETE FROM tickets")
        
        # Reset sequence
        cur.execute("ALTER SEQUENCE tickets_id_seq RESTART WITH 1001")

        # Sample ticket data
        sample_tickets = [
            {
                'title': 'Password Reset Request',
                'description': 'Unable to access email account, need password reset',
                'priority': 'Medium',
                'category': 'Account Access',
                'status': 'Open',
                'user_id': 1,
                'assigned_to': 2
            },
            {
                'title': 'Software Installation Issue',
                'description': 'Microsoft Office installation failing on Windows 10',
                'priority': 'High',
                'category': 'Software',
                'status': 'In Progress',
                'user_id': 1,
                'assigned_to': 2
            },
            {
                'title': 'Network Connectivity Problem',
                'description': 'Cannot connect to company VPN from home',
                'priority': 'High',
                'category': 'Network',
                'status': 'Open',
                'user_id': 1,
                'assigned_to': 3
            },
            {
                'title': 'Printer Not Working',
                'description': 'Office printer showing error message',
                'priority': 'Low',
                'category': 'Hardware',
                'status': 'Resolved',
                'user_id': 1,
                'assigned_to': 2
            },
            {
                'title': 'Email Sync Issues',
                'description': 'Outlook not syncing with mobile device',
                'priority': 'Medium',
                'category': 'Email',
                'status': 'Pending',
                'user_id': 1,
                'assigned_to': 3
            }
        ]

        # Insert tickets with proper numbering
        for i, ticket in enumerate(sample_tickets, 1001):
            ticket_number = f"TKT-{i}"
            created_at = datetime.now() - timedelta(days=random.randint(0, 30))
            
            cur.execute("""
                INSERT INTO tickets (ticket_number, title, description, priority, category, status, user_id, assigned_to, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ticket_number,
                ticket['title'],
                ticket['description'],
                ticket['priority'],
                ticket['category'],
                ticket['status'],
                ticket['user_id'],
                ticket['assigned_to'],
                created_at,
                created_at
            ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'message': 'Tickets data recreated successfully',
            'tickets_created': len(sample_tickets)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500