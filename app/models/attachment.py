# File attachment model for IT ServiceDesk ticket system
# Handles file uploads associated with support tickets

from app import db
from datetime import datetime

class FileAttachment(db.Model):
    """File attachment model for ticket-related file uploads
    
    Stores metadata and references for files uploaded to tickets.
    Actual file content is stored separately (filesystem, cloud storage, etc.)
    
    Supported file types:
    - Documents: PDF, DOC, DOCX, TXT
    - Images: JPG, JPEG, PNG, GIF
    - Spreadsheets: XLS, XLSX
    - Archives: ZIP
    - Logs: LOG
    
    File size limit: 10MB per file
    """
    __tablename__ = 'file_attachments'
    
    # Primary key and relationships
    id = db.Column(db.String(50), primary_key=True)  # UUID for unique file identification
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)  # Parent ticket
    
    # File metadata
    filename = db.Column(db.String(255), nullable=False)  # Original filename from user
    file_size = db.Column(db.BigInteger, nullable=False)  # File size in bytes
    mime_type = db.Column(db.String(100), nullable=False)  # MIME type for proper handling
    
    # Upload tracking
    uploaded_by = db.Column(db.String(50), nullable=False)  # User ID who uploaded the file
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # Upload timestamp
    
    # Database relationships
    ticket = db.relationship('Ticket', backref='file_attachments')  # Link to parent ticket
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<FileAttachment {self.filename}>'
    
    @property
    def file_size_mb(self):
        """Convert file size from bytes to megabytes for display
        
        Returns:
            float: File size in MB rounded to 2 decimal places
        """
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_image(self):
        """Check if the file is an image based on MIME type
        
        Returns:
            bool: True if file is an image, False otherwise
        """
        return self.mime_type.startswith('image/') if self.mime_type else False
    
    @property
    def file_extension(self):
        """Extract file extension from filename
        
        Returns:
            str: File extension (e.g., 'pdf', 'jpg') or empty string if none
        """
        if '.' in self.filename:
            return self.filename.rsplit('.', 1)[1].lower()
        return ''