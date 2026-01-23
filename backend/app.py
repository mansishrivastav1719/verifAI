"""
VerifAI - Document Forgery Detector
Simplified version for hackathon
"""

import os
import time
import uuid
from flask import Flask, jsonify, request

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API Routes
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'VerifAI'})

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'document' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    doc_id = str(uuid.uuid4())[:8]
    filename = f"{doc_id}_{file.filename}"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    
    return jsonify({
        'status': 'uploaded',
        'document_id': doc_id,
        'process_endpoint': f'/api/process/{doc_id}'
    })

@app.route('/api/process/<doc_id>')
def process(doc_id):
    time.sleep(3)  # Simulate processing
    
    return jsonify({
        'document_id': doc_id,
        'overall_confidence': 87,
        'uncertainty': 13,
        'processing_time': 14.5,
        'verdict': 'SUSPICIOUS',
        'signals': {
            'ela': {
                'name': 'Error Level Analysis',
                'confidence': 85,
                'summary': 'Editing artifacts detected'
            },
            'ocr': {
                'name': 'Text Inconsistency',
                'confidence': 75,
                'summary': 'Text inconsistencies found'
            },
            'metadata': {
                'name': 'Metadata Forensics',
                'confidence': 95,
                'summary': 'Metadata anomalies'
            }
        },
        'combined_findings': [
            {'type': 'ELA', 'confidence': 85, 'description': 'Date field tampered'},
            {'type': 'OCR', 'confidence': 75, 'description': 'Font inconsistency'},
            {'type': 'Metadata', 'confidence': 95, 'description': 'Date anomaly'}
        ],
        'status': 'completed'
    })

if __name__ == '__main__':
    print("🚀 VerifAI Backend running at http://localhost:5000")
    print("📁 API Endpoints:")
    print("   • GET  /api/health")
    print("   • POST /api/upload")
    print("   • GET  /api/process/<id>")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
