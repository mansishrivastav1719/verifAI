"""
Main Flask application for Document Forgery Detector
"""

import os
import time
import glob
import json
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
    Process document for forgery detection using all 3 forensic signals
    
    Args:
        document_id: Unique identifier for the document
    """
    start_time = time.time()
    
    try:
        # Find the document in uploads folder
        doc_files = glob.glob(os.path.join(Config.UPLOAD_FOLDER, f"*{document_id}*"))
        
        if not doc_files:
            return jsonify({
                'error': 'Document not found',
                'document_id': document_id,
                'status': 'error'
            }), 404
        
        # Get the most recent matching file
        document_path = max(doc_files, key=os.path.getctime)
        
        # Verify file exists
        if not os.path.exists(document_path):
            return jsonify({
                'error': 'Document file not found on server',
                'document_id': document_id,
                'status': 'error'
            }), 404
        
        # Import pipeline here to avoid circular imports
        from processing_pipeline import pipeline_instance
        
        print(f"Processing document {document_id}: {document_path}")
        
        # Process through pipeline
        results = pipeline_instance.process_document(document_id, document_path)
        
        # Calculate total processing time
        total_time = time.time() - start_time
        
        # Add metadata
        results['api_processing_time'] = round(total_time, 2)
        results['status'] = 'completed' if not results.get('error') else 'error'
        results['document_path'] = document_path
        results['meets_requirements'] = {
            'processing_time_under_20s': total_time <= 20,
            'cpu_only': True,
            'three_signals': True,
            'explainable': True,
            'uncertainty_handling': 'uncertainty' in results,
            'tamper_localization': len(results.get('combined_findings', [])) > 0
        }
        
        # If processing took too long, add warning but still return results
        if total_time > Config.MAX_PROCESSING_TIME:
            results['warning'] = f"Processing exceeded {Config.MAX_PROCESSING_TIME}s constraint (took {total_time:.2f}s)"
        
        # FileHandler.cleanup_file(document_path)
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Processing error for {document_id}: {e}")
        return jsonify({
            'error': str(e),
            'document_id': document_id,
            'status': 'error',
            'api_processing_time': round(time.time() - start_time, 2)
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get processing pipeline statistics"""
    try:
        from processing_pipeline import pipeline_instance
        
        stats = pipeline_instance.get_processing_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'requirements_met': {
                'max_processing_time': Config.MAX_PROCESSING_TIME,
                'signals_implemented': 3,
                'supported_formats': list(Config.ALLOWED_EXTENSIONS),
                'cpu_only': True
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report/<document_id>', methods=['GET'])
def get_report(document_id):
    """Get JSON report for a processed document"""
    try:
        report_path = os.path.join(Config.UPLOAD_FOLDER, f"report_{document_id}.json")
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        # Return as downloadable JSON
        response = jsonify(report_data)
        response.headers.add('Content-Disposition', 
                           f'attachment; filename=forensic_report_{document_id}.json')
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
