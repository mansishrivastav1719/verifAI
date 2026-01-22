"""
File handling utilities for document processing
"""

import os
import uuid
from werkzeug.utils import secure_filename
from config import Config
import magic  # python-magic

class FileHandler:
    """Handle file uploads, validation, and conversion"""
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_type(file_path):
        """Get actual file type using magic"""
        try:
            mime = magic.Magic(mime=True)
            return mime.from_file(file_path)
        except:
            return None
    
    @staticmethod
    def generate_unique_filename(original_filename):
        """Generate a unique filename to prevent collisions"""
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_id = str(uuid.uuid4())[:8]
        secure_name = secure_filename(original_filename.rsplit('.', 0)[0] if '.' in original_filename else original_filename)
        
        if ext:
            return f"{secure_name}_{unique_id}.{ext}"
        return f"{secure_name}_{unique_id}"
    
    @staticmethod
    def save_uploaded_file(file):
        """Save uploaded file to uploads folder"""
        if not file or file.filename == '':
            return None
        
        if not FileHandler.allowed_file(file.filename):
            return None
        
        # Generate unique filename
        filename = FileHandler.generate_unique_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(file_path)
        
        # Verify file is valid
        mime_type = FileHandler.get_file_type(file_path)
        if not mime_type or not any(mime_type.startswith(prefix) for prefix in ['image/', 'application/pdf']):
            os.remove(file_path)
            return None
        
        return file_path
    
    @staticmethod
    def cleanup_file(file_path):
        """Clean up temporary files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
