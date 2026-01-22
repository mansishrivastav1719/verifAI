#!/usr/bin/env python3
"""
Run script for Document Forgery Detector
"""

import os
import sys
from app import app

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import opencv_python
        import pytesseract
        import pdf2image
        import pdfplumber
        import waitress
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install -r requirements.txt")
        return False

def check_system_dependencies():
    """Check system-level dependencies"""
    import subprocess
    
    # Check Tesseract
    try:
        subprocess.run(['tesseract', '--version'], 
                      capture_output=True, check=True)
        print("✅ Tesseract OCR is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Tesseract OCR not found. OCR analysis will be limited.")
        print("   Install: sudo apt-get install tesseract-ocr (Linux)")
        print("   Install: brew install tesseract (macOS)")
    
    # Check Poppler (for PDF conversion)
    try:
        subprocess.run(['pdftoppm', '-v'], 
                      capture_output=True, check=False)
        print("✅ Poppler (pdftoppm) is installed")
    except FileNotFoundError:
        print("⚠️  Poppler not found. PDF conversion will be limited.")
        print("   Install: sudo apt-get install poppler-utils (Linux)")
        print("   Install: brew install poppler (macOS)")

def create_directories():
    """Create necessary directories"""
    from config import Config
    Config.init_app()
    print("✅ Directories created")

def main():
    """Main entry point"""
    print("=" * 60)
    print("DOCUMENT FORGERY DETECTOR - Starting Up")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    check_system_dependencies()
    create_directories()
    
    print("\n" + "=" * 60)
    print("SYSTEM READY")
    print("=" * 60)
    print(f"📁 Upload folder: uploads/")
    print(f"⏱️  Max processing time: 20 seconds")
    print(f"🔍 Forensic signals: 3 (ELA, OCR, Metadata)")
    print(f"🌐 Web interface: http://localhost:5000")
    print(f"📊 API status: http://localhost:5000/health")
    print("=" * 60)
    
    # Run the application
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
