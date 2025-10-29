# File upload and download routes for IT ServiceDesk
# Handles secure file operations for ticket attachments

# Flask imports
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Database and models
from app import db
from app.models.attachment import FileAttachment
from app.models.ticket import Ticket

# Cloudinary service
from app.services.cloudinary_service import CloudinaryService

# System imports
import os
import uuid
from datetime import datetime

# Blueprint for file-related endpoints
files_bp = Blueprint('files', __name__)

# === FILE UPLOAD CONFIGURATION ===
# Upload directory (relative to project root)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')

# Allowed file extensions for security
# Only these file types can be uploaded to prevent malicious files
ALLOWED_EXTENSIONS = {
    'txt',           # Text files
    'pdf',           # PDF documents
    'png', 'jpg', 'jpeg', 'gif',  # Images
    'doc', 'docx',   # Microsoft Word
    'xls', 'xlsx',   # Microsoft Excel
    'zip',           # Archives
    'log'            # Log files
}

# Maximum file size limit (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if uploaded file has an allowed extension
    
    Args:
        filename (str): Original filename from upload
    
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload for ticket attachments
    
    Expected form data:
        - file: The uploaded file
        - ticket_id: ID of the ticket to attach file to
        - uploaded_by: ID of the user uploading the file
        - message_id: Optional message ID (for future use)
    
    Returns:
        JSON response with file metadata or error message
    
    Security measures:
        - File type validation (only allowed extensions)
        - File size validation (10MB limit)
        - Secure filename handling
        - UUID-based file naming to prevent conflicts
    """
    # Validation 1: Check if file was provided
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    # Extract form data
    file = request.files['file']
    ticket_id = request.form.get('ticket_id')
    message_id = request.form.get('message_id')  # Optional for future use
    uploaded_by = request.form.get('uploaded_by')
    
    # Validation 2: Check required fields
    if not ticket_id or not uploaded_by:
        return jsonify({'error': 'Missing required fields: ticket_id and uploaded_by'}), 400
    
    # Validation 3: Check if file was actually selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validation 4: Check file type against allowed extensions
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Security: Sanitize filename to prevent directory traversal attacks
    original_filename = secure_filename(file.filename)
    
    # Generate unique file ID to prevent naming conflicts
    file_id = str(uuid.uuid4())
    
    # Create unique filename: UUID_originalname.ext
    filename = f"{file_id}_{original_filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save file to disk
    file.save(filepath)
    
    # Get actual file size after saving
    file_size = os.path.getsize(filepath)
    
    # Validation 5: Check file size limit (after saving to get accurate size)
    if file_size > MAX_FILE_SIZE:
        # Remove the file if it exceeds size limit
        os.remove(filepath)
        return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
    
    # Create database record for the attachment
    try:
        attachment = FileAttachment(
            id=file_id,
            ticket_id=int(ticket_id),  # Ensure integer type
            filename=original_filename,
            file_size=file_size,
            mime_type=file.content_type or 'application/octet-stream',
            uploaded_by=uploaded_by
        )
        
        # Save to database
        db.session.add(attachment)
        db.session.commit()
        
        # Return success response with file metadata
        return jsonify({
            'id': attachment.id,
            'filename': attachment.filename,
            'file_size_mb': attachment.file_size_mb,
            'uploaded_at': attachment.uploaded_at.isoformat(),
            'message': 'File uploaded successfully'
        }), 201
        
    except Exception as e:
        # Rollback database changes and remove file on error
        db.session.rollback()
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@files_bp.route('/<file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download a file attachment by ID
    
    Args:
        file_id (str): UUID of the file attachment
    
    Returns:
        File download response or 404 if not found
    
    Security:
        - File access is controlled by database lookup
        - Original filename is preserved for user experience
        - Files are served as attachments (not inline) for security
    """
    # Look up file attachment in database
    attachment = FileAttachment.query.get_or_404(file_id)
    
    # Construct file path using UUID and original filename
    filepath = os.path.join(UPLOAD_FOLDER, f"{file_id}_{attachment.filename}")
    
    # Check if file exists on disk
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found on disk'}), 404
    
    # Send file as attachment download
    return send_file(
        filepath, 
        as_attachment=True,  # Force download instead of inline display
        download_name=attachment.filename  # Use original filename for download
    )

@files_bp.route('/ticket/<ticket_id>', methods=['GET'])
def get_ticket_files(ticket_id):
    """Get all file attachments for a specific ticket
    
    Args:
        ticket_id (str): ID of the ticket
    
    Returns:
        JSON array of file attachment metadata
    
    Response includes:
        - File ID, filename, size
        - Upload timestamp and user
        - Download URL for each file
    """
    try:
        # Query all attachments for the ticket, ordered by upload time (newest first)
        attachments = FileAttachment.query.filter_by(
            ticket_id=int(ticket_id)
        ).order_by(
            FileAttachment.uploaded_at.desc()
        ).all()
        
        # Build response array with file metadata
        files_data = []
        for attachment in attachments:
            files_data.append({
                'id': attachment.id,
                'filename': attachment.filename,
                'file_size_mb': attachment.file_size_mb,
                'mime_type': attachment.mime_type,
                'uploaded_by': attachment.uploaded_by,
                'uploaded_at': attachment.uploaded_at.isoformat(),
                'download_url': f'/api/files/{attachment.id}/download',
                'is_image': attachment.is_image,  # Helper for UI display
                'file_extension': attachment.file_extension
            })
        
        return jsonify(files_data)
        
    except ValueError:
        # Invalid ticket_id format
        return jsonify({'error': 'Invalid ticket ID format'}), 400
    except Exception as e:
        # Database or other errors
        return jsonify({'error': f'Failed to retrieve files: {str(e)}'}), 500

@files_bp.route('/cloudinary/upload', methods=['POST'])
def cloudinary_upload():
    """Upload file to Cloudinary
    
    Expected form data:
        - file: The uploaded file
        - ticket_id: ID of the ticket
        - uploaded_by: ID of the user
    
    Returns:
        JSON response with upload result
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    ticket_id = request.form.get('ticket_id')
    uploaded_by = request.form.get('uploaded_by')
    
    if not ticket_id or not uploaded_by:
        return jsonify({'error': 'Missing ticket_id or uploaded_by'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        cloudinary_service = CloudinaryService()
        result = cloudinary_service.upload_image(file, ticket_id, uploaded_by)
        
        if result and 'error' not in result:
            return jsonify({
                'message': 'File uploaded successfully',
                'url': result['url'],
                'public_id': result['public_id'],
                'width': result['width'],
                'height': result['height'],
                'format': result['format'],
                'bytes': result['bytes']
            }), 201
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Upload failed'
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        return jsonify({'error': f'Upload error: {str(e)}'}), 500
