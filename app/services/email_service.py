import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app

class EmailService:
    """Service for sending emails using SendGrid"""
    
    @staticmethod
    def send_email(to_email, subject, html_content, from_email=None):
        """Send email using SendGrid"""
        try:
            api_key = current_app.config.get('SENDGRID_API_KEY')
            if not api_key:
                print("SendGrid API key not configured")
                return False
            
            from_email = from_email or current_app.config.get('FROM_EMAIL')
            
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            
            print(f"Email sent to {to_email}: {response.status_code}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def send_welcome_email(email, name):
        """Send welcome email to new users"""
        subject = "Welcome to IT ServiceDesk"
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to IT ServiceDesk, {name}!</h2>
            <p>Your account has been successfully created.</p>
            <p>You can now log in and start creating support tickets.</p>
            <p>If you have any questions, please don't hesitate to contact our support team.</p>
            <br>
            <p>Best regards,<br>IT ServiceDesk Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(email, subject, html_content)
    
    @staticmethod
    def send_ticket_notification(email, name, ticket_id, ticket_title, status):
        """Send ticket status notification"""
        subject = f"Ticket {ticket_id} - Status Update"
        html_content = f"""
        <html>
        <body>
            <h2>Ticket Status Update</h2>
            <p>Hello {name},</p>
            <p>Your ticket <strong>{ticket_id}</strong> has been updated.</p>
            <p><strong>Title:</strong> {ticket_title}</p>
            <p><strong>New Status:</strong> {status}</p>
            <p>You can view the full details by logging into the ServiceDesk portal.</p>
            <br>
            <p>Best regards,<br>IT ServiceDesk Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(email, subject, html_content)
    
    @staticmethod
    def send_sla_breach_notification(email, name, ticket_id, ticket_title):
        """Send SLA breach notification"""
        subject = f"URGENT: SLA Breach - Ticket {ticket_id}"
        html_content = f"""
        <html>
        <body>
            <h2 style="color: red;">SLA BREACH ALERT</h2>
            <p>Hello {name},</p>
            <p>Ticket <strong>{ticket_id}</strong> has breached its SLA target.</p>
            <p><strong>Title:</strong> {ticket_title}</p>
            <p style="color: red;"><strong>Action Required:</strong> Please review and take immediate action on this ticket.</p>
            <p>Log into the ServiceDesk portal to view details and update the ticket.</p>
            <br>
            <p>Best regards,<br>IT ServiceDesk Team</p>
        </body>
        </html>
        """
        return EmailService.send_email(email, subject, html_content)