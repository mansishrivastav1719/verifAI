"""
Main Flask application for Document Forgery Detector
"""

import os
import time
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from config import Config
from utils.file_handler import FileHandler
from utils.pdf_converter import PDFConverter

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize application directories
Config.init_app()

@app.route('/')
def index():
    """Render main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Document Forgery Detector',
        'version': '1.0.0'
    })

@app.route('/upload', methods=['POST'])
def upload_document():
    """
    Handle document upload and initial processing
    
    Returns:
        JSON response with processing status and metadata
    """
    start_time = time.time()
    
    # Check if file is present
    if 'document' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['document']
    
    # Validate and save file
    file_path = FileHandler.save_uploaded_file(file)
    if not file_path:
        return jsonify({'error': 'Invalid file type or corrupted file'}), 400
    
    try:
        # Determine file type and prepare for processing
        file_info = {
            'original_filename': file.filename,
            'saved_path': file_path,
            'file_type': FileHandler.get_file_type(file_path),
            'is_pdf': PDFConverter.is_pdf(file_path)
        }
        
        # Convert PDF to image if necessary
        processing_path = file_path
        if file_info['is_pdf']:
            # Extract first page only for initial processing
            _, first_page_path = PDFConverter.extract_first_page(
                file_path, 
                os.path.join(Config.TEMP_DIR, f"first_page_{os.path.basename(file_path)}.png")
            )
            if first_page_path:
                processing_path = first_page_path
                file_info['first_page_path'] = first_page_path
        
        # Convert to PNG if not already
        if not processing_path.endswith('.png'):
            png_path = PDFConverter.convert_to_png(
                processing_path,
                os.path.join(Config.TEMP_DIR, f"{os.path.basename(processing_path)}.png")
            )
            processing_path = png_path
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            'status': 'uploaded',
            'message': 'Document uploaded successfully',
            'document_id': os.path.basename(file_path).split('_')[0],
            'file_info': {
                'filename': file_info['original_filename'],
                'type': file_info['file_type'],
                'is_pdf': file_info['is_pdf'],
                'processing_path': processing_path,
                'original_path': file_path
            },
            'processing_time': round(processing_time, 2),
            'next_step': 'process',  # Indicate next step is processing
            'process_endpoint': f'/process/{os.path.basename(file_path).split("_")[0]}'
        }
        
        return jsonify(response)
        
    except Exception as e:
        # Clean up on error
        FileHandler.cleanup_file(file_path)
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/process/<document_id>', methods=['GET'])
def process_document(document_id):
    """
    Process document for forgery detection (placeholder - will be implemented)
    
    Args:
        document_id: Unique identifier for the document
    """
    # TODO: Implement actual processing
    return jsonify({
        'status': 'processing',
        'document_id': document_id,
        'message': 'Processing pipeline will be implemented',
        'signals': ['ELA', 'OCR', 'Metadata'],
        'estimated_time': 'Under 20 seconds'
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Serve uploaded files"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files for display"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # Production server
    from waitress import serve
    print("🚀 Document Forgery Detector starting...")
    print(f"📁 Upload folder: {Config.UPLOAD_FOLDER}")
    print(f"⏱️ Max processing time: {Config.MAX_PROCESSING_TIME} seconds")
    print("🌐 Server running at http://localhost:5000")
    
    serve(app, host='0.0.0.0', port=5000)
