import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        self.from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'mwanikijoe1@gmail.com')
    
    def send_ticket_notification(self, to_email, ticket_id, ticket_title, message_type='created'):
        subject_map = {
            'created': f'New Ticket Created: {ticket_id}',
            'assigned': f'Ticket Assigned: {ticket_id}',
            'updated': f'Ticket Updated: {ticket_id}',
            'closed': f'Ticket Resolved: {ticket_id}'
        }
        
        content_map = {
            'created': f'A new support ticket has been created.\n\nTicket ID: {ticket_id}\nTitle: {ticket_title}\n\nYou can view and track this ticket in your dashboard.',
            'assigned': f'A ticket has been assigned to you.\n\nTicket ID: {ticket_id}\nTitle: {ticket_title}\n\nPlease review and take action as needed.',
            'updated': f'Your ticket has been updated.\n\nTicket ID: {ticket_id}\nTitle: {ticket_title}\n\nCheck your dashboard for the latest updates.',
            'closed': f'Your ticket has been resolved.\n\nTicket ID: {ticket_id}\nTitle: {ticket_title}\n\nThank you for using our support system.'
        }
        
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject_map.get(message_type, f'Ticket Notification: {ticket_id}'),
            plain_text_content=content_map.get(message_type, f'Ticket {ticket_id} notification.')
        )
        
        try:
            response = self.sg.send(message)
            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False
    
    def send_sla_violation_alert(self, to_email, ticket_id, ticket_title):
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=f'SLA Violation Alert: {ticket_id}',
            plain_text_content=f'URGENT: SLA violation detected.\n\nTicket ID: {ticket_id}\nTitle: {ticket_title}\n\nImmediate attention required.'
        )
        
        try:
            response = self.sg.send(message)
            return True
        except Exception as e:
            print(f"SLA alert email error: {e}")
            return False