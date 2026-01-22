"""
Configuration settings for Document Forgery Detector
"""

import os

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Processing Configuration
    MAX_PROCESSING_TIME = 20  # seconds (constraint from requirements)
    TEMP_DIR = 'temp'
    
    # Signal Processing Configuration
    ELA_QUALITY = 95  # JPEG quality for ELA analysis
    ELA_THRESHOLD = 10  # Threshold for ELA difference detection
    
    # OCR Configuration
    TESSERACT_CONFIG = '--psm 6 --oem 3'
    
    # Create necessary directories
    @staticmethod
    def init_app():
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
