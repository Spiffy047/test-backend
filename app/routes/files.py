from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from app import db
from app.models.attachment import FileAttachment
from app.models.ticket import Ticket
import os
import uuid
from datetime import datetime

files_bp = Blueprint('files', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'log'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    ticket_id = request.form.get('ticket_id')
    message_id = request.form.get('message_id')
    uploaded_by = request.form.get('uploaded_by')
    
    if not ticket_id or not uploaded_by:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    original_filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{original_filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    file.save(filepath)
    file_size = os.path.getsize(filepath)
    
    attachment = FileAttachment(
        id=file_id,
        ticket_id=ticket_id,
        message_id=message_id,
        filename=filename,
        original_filename=original_filename,
        file_size=file_size,
        mime_type=file.content_type or 'application/octet-stream',
        storage_path=filepath,
        uploaded_by=uploaded_by,
        is_scanned=True,
        scan_result='clean'
    )
    
    db.session.add(attachment)
    db.session.commit()
    
    return jsonify({
        'id': attachment.id,
        'filename': attachment.original_filename,
        'file_size': attachment.file_size_mb,
        'uploaded_at': attachment.uploaded_at.isoformat()
    }), 201

@files_bp.route('/<file_id>/download', methods=['GET'])
def download_file(file_id):
    attachment = FileAttachment.query.get_or_404(file_id)
    return send_file(attachment.storage_path, as_attachment=True, download_name=attachment.original_filename)

@files_bp.route('/ticket/<ticket_id>', methods=['GET'])
def get_ticket_files(ticket_id):
    attachments = FileAttachment.query.filter_by(ticket_id=ticket_id).order_by(FileAttachment.uploaded_at.desc()).all()
    return jsonify([{
        'id': a.id,
        'filename': a.original_filename,
        'file_size_mb': a.file_size_mb,
        'uploaded_by': a.uploaded_by,
        'uploaded_at': a.uploaded_at.isoformat(),
        'download_url': f'/api/files/{a.id}/download'
    } for a in attachments])
