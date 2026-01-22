/**
 * Main JavaScript for Document Forgery Detector
 * Handles file upload, processing, and visualization
 */

// Global variables
let currentDocumentId = null;
let currentDocumentPath = null;
let detectionResults = null;
let heatmapRegions = [];

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');
const uploadContent = document.getElementById('uploadContent');
const processingSection = document.getElementById('processingSection');
const processingText = document.getElementById('processingText');
const processingProgress = document.getElementById('processingProgress');
const signalStatus = document.getElementById('signalStatus');
const resultsSection = document.getElementById('resultsSection');
const originalPreview = document.getElementById('originalPreview');
const heatmapCanvas = document.getElementById('heatmapCanvas');
const overallConfidence = document.getElementById('overallConfidence');
const confidenceText = document.getElementById('confidenceText');
const confidenceFill = document.getElementById('confidenceFill');
const uncertaintyScore = document.getElementById('uncertaintyScore');
const signalResults = document.getElementById('signalResults');
const generateReport = document.getElementById('generateReport');
const detailedFindings = document.getElementById('detailedFindings');

// Initialize application
function init() {
    setupEventListeners();
    console.log('DocVerify Frontend initialized');
}

// Set up event listeners
function setupEventListeners() {
    // File input button
    uploadButton.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
    
    // Report generation
    generateReport.addEventListener('click', generateForensicReport);
    
    // Heatmap click events
    heatmapCanvas.addEventListener('click', handleHeatmapClick);
}

// Handle file selection via button
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

// Handle drag over
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    uploadZone.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    uploadZone.classList.remove('dragover');
}

// Handle file drop
function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    uploadZone.classList.remove('dragover');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        processFile(file);
    }
}

// Process uploaded file
function processFile(file) {
    // Validate file
    if (!validateFile(file)) {
        alert('Please upload a valid document (PDF, PNG, JPG, JPEG) under 16MB');
        return;
    }
    
    // Show processing section
    showProcessing();
    
    // Create FormData
    const formData = new FormData();
    formData.append('document', file);
    
    // Upload file to backend
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Upload successful:', data);
        
        // Save document info
        currentDocumentId = data.document_id;
        currentDocumentPath = data.file_info.processing_path;
        
        // Update processing status
        updateProcessingStatus('File uploaded. Starting analysis...', 25);
        
        // Start processing
        return processDocument(data.process_endpoint);
    })
    .then(results => {
        // Update processing status
        updateProcessingStatus('Analysis complete! Generating report...', 100);
        
        // Show results after a short delay
        setTimeout(() => {
            displayResults(results);
        }, 1000);
    })
    .catch(error => {
        console.error('Error:', error);
        updateProcessingStatus('Error processing document. Please try again.', 0);
        setTimeout(() => {
            hideProcessing();
            alert(`Error: ${error.message}`);
        }, 2000);
    });
}

// Validate file
function validateFile(file) {
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|png|jpg|jpeg)$/i)) {
        return false;
    }
    
    if (file.size > maxSize) {
        return false;
    }
    
    return true;
}

// Show processing section
function showProcessing() {
    uploadContent.style.opacity = '0.5';
    processingSection.style.display = 'block';
    updateProcessingStatus('Uploading document...', 10);
    
    // Initialize signal status
    signalStatus.innerHTML = `
        <div class="col">
            <div class="card signal-card signal-ela">
                <div class="card-body">
                    <h6><i class="fas fa-code-branch"></i> ELA Analysis</h6>
                    <small class="text-muted" id="elaStatus">Waiting...</small>
                </div>
            </div>
        </div>
        <div class="col">
            <div class="card signal-card signal-ocr">
                <div class="card-body">
                    <h6><i class="fas fa-font"></i> OCR Analysis</h6>
                    <small class="text-muted" id="ocrStatus">Waiting...</small>
                </div>
            </div>
        </div>
        <div class="col">
            <div class="card signal-card signal-meta">
                <div class="card-body">
                    <h6><i class="fas fa-database"></i> Metadata Analysis</h6>
                    <small class="text-muted" id="metaStatus">Waiting...</small>
                </div>
            </div>
        </div>
    `;
}

// Update processing status
function updateProcessingStatus(message, progress) {
    processingText.textContent = message;
    processingProgress.style.width = `${progress}%`;
    
    // Update signal status based on progress
    if (progress >= 33) {
        document.getElementById('elaStatus').textContent = 'Completed';
        document.getElementById('elaStatus').className = 'text-success';
    }
    if (progress >= 66) {
        document.getElementById('ocrStatus').textContent = 'Completed';
        document.getElementById('ocrStatus').className = 'text-success';
    }
    if (progress >= 99) {
        document.getElementById('metaStatus').textContent = 'Completed';
        document.getElementById('metaStatus').className = 'text-success';
    }
}

// Hide processing section
function hideProcessing() {
    processingSection.style.display = 'none';
    uploadContent.style.opacity = '1';
}

// Process document through backend
function processDocument(processEndpoint) {
    return new Promise((resolve, reject) => {
        // Simulate processing with multiple steps
        let progress = 25;
        
        // Step 1: ELA Analysis
        setTimeout(() => {
            updateProcessingStatus('Running Error Level Analysis...', 33);
            updateSignalStatus('ela', 'processing');
        }, 1000);
        
        // Step 2: OCR Analysis
        setTimeout(() => {
            updateProcessingStatus('Analyzing text consistency...', 66);
            updateSignalStatus('ocr', 'processing');
        }, 3000);
        
        // Step 3: Metadata Analysis
        setTimeout(() => {
            updateProcessingStatus('Checking metadata anomalies...', 80);
            updateSignalStatus('meta', 'processing');
        }, 5000);
        
        // Step 4: Final processing
        setTimeout(() => {
            updateProcessingStatus('Generating final report...', 90);
            
            // Call actual backend endpoint
            fetch(processEndpoint)
                .then(response => response.json())
                .then(data => {
                    // For demo purposes, generate mock results
                    // Replace with actual API response when backend is ready
                    const mockResults = generateMockResults();
                    resolve(mockResults);
                })
                .catch(error => {
                    console.warn('Backend processing not ready, using mock data');
                    const mockResults = generateMockResults();
                    resolve(mockResults);
                });
        }, 7000);
    });
}

// Update signal status
function updateSignalStatus(signal, status) {
    const statusElement = document.getElementById(`${signal}Status`);
    if (!statusElement) return;
    
    switch(status) {
        case 'processing':
            statusElement.textContent = 'Processing...';
            statusElement.className = 'text-warning';
            break;
        case 'completed':
            statusElement.textContent = 'Completed';
            statusElement.className = 'text-success';
            break;
        case 'error':
            statusElement.textContent = 'Error';
            statusElement.className = 'text-danger';
            break;
    }
}

// Generate mock results for demo
function generateMockResults() {
    return {
        document_id: currentDocumentId,
        confidence: 87,
        uncertainty: 13,
        processing_time: 14.5,
        signals: {
            ela: {
                confidence: 85,
                findings: [
                    {region: [100, 150, 200, 80], confidence: 90, description: 'Date field shows copy-paste artifacts'},
                    {region: [300, 250, 150, 50], confidence: 80, description: 'Amount field has inconsistent compression'}
                ],
                summary: 'Multiple regions show editing artifacts'
            },
            ocr: {
                confidence: 75,
                findings: [
                    {region: [100, 150, 200, 30], confidence: 70, description: 'Font inconsistency in date field'},
                    {region: [300, 250, 150, 30], confidence: 80, description: 'Text alignment mismatch'}
                ],
                summary: 'Text formatting inconsistencies detected'
            },
            metadata: {
                confidence: 95,
                findings: [
                    {description: 'Creation date (2024-01-15) is after modification date (2023-12-20)', confidence: 95},
                    {description: 'Software metadata shows "Photoshop" for a PDF document', confidence: 90}
                ],
                summary: 'Metadata anomalies suggest document editing'
            }
        },
        verdict: 'SUSPICIOUS',
        recommendations: [
            'Verify date fields with issuing authority',
            'Check amount fields against bank records',
            'Request original document for comparison'
        ]
    };
}

// Display results
function displayResults(results) {
    detectionResults = results;
    
    // Hide processing, show results
    hideProcessing();
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({behavior: 'smooth'});
    
    // Update UI with results
    updateConfidenceDisplay(results.confidence, results.uncertainty);
    updateSignalDisplay(results.signals);
    updateHeatmap(results.signals);
    updateDetailedFindings(results);
    
    // Set document preview (for demo, use placeholder)
    originalPreview.src = '/placeholder.png';
    originalPreview.alt = 'Document Preview';
}

// Update confidence display
function updateConfidenceDisplay(confidence, uncertainty) {
    overallConfidence.textContent = `${confidence}%`;
    uncertaintyScore.textContent = `${uncertainty}%`;
    
    // Set confidence text
    if (confidence >= 80) {
        confidenceText.textContent = 'HIGH CONFIDENCE - Document likely tampered';
        confidenceText.className = 'text-danger';
        confidenceFill.className = 'confidence-fill high-confidence';
    } else if (confidence >= 50) {
        confidenceText.textContent = 'MEDIUM CONFIDENCE - Document suspicious';
        confidenceText.className = 'text-warning';
        confidenceFill.className = 'confidence-fill medium-confidence';
    } else {
        confidenceText.textContent = 'LOW CONFIDENCE - Document likely authentic';
        confidenceText.className = 'text-success';
        confidenceFill.className = 'confidence-fill low-confidence';
    }
    
    // Animate confidence bar
    setTimeout(() => {
        confidenceFill.style.width = `${confidence}%`;
    }, 100);
}

// Update signal display
function updateSignalDisplay(signals) {
    signalResults.innerHTML = '';
    heatmapRegions = [];
    
    // ELA Signal
    const elaCard = createSignalCard(
        'ela',
        'Error Level Analysis',
        signals.ela.confidence,
        signals.ela.summary,
        signals.ela.findings.length
    );
    signalResults.appendChild(elaCard);
    
    // OCR Signal
    const ocrCard = createSignalCard(
        'ocr',
        'Text Inconsistency',
        signals.ocr.confidence,
        signals.ocr.summary,
        signals.ocr.findings.length
    );
    signalResults.appendChild(ocrCard);
    
    // Metadata Signal
    const metaCard = createSignalCard(
        'meta',
        'Metadata Forensics',
        signals.metadata.confidence,
        signals.metadata.summary,
        signals.metadata.findings.length
    );
    signalResults.appendChild(metaCard);
}

// Create signal card element
function createSignalCard(type, title, confidence, summary, findingCount) {
    const card = document.createElement('div');
    card.className = `card signal-card signal-${type} mb-3`;
    
    // Determine confidence color
    let confidenceColor = 'success';
    if (confidence >= 70) confidenceColor = 'danger';
    else if (confidence >= 40) confidenceColor = 'warning';
    
    card.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
                <h6 class="mb-0">${title}</h6>
                <span class="badge bg-${confidenceColor}">${confidence}%</span>
            </div>
            <p class="small text-muted mb-2 mt-2">${summary}</p>
            <div class="d-flex justify-content-between">
                <small>${findingCount} findings</small>
                <small><i class="fas fa-info-circle"></i> Click for details</small>
            </div>
        </div>
    `;
    
    // Add click event
    card.addEventListener('click', () => showSignalDetails(type));
    
    return card;
}

// Update heatmap
function updateHeatmap(signals) {
    const ctx = heatmapCanvas.getContext('2d');
    const width = heatmapCanvas.width;
    const height = heatmapCanvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw placeholder document
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, width, height);
    
    ctx.strokeStyle = '#dee2e6';
    ctx.lineWidth = 1;
    ctx.strokeRect(10, 10, width - 20, height - 20);
    
    // Draw text placeholder
    ctx.fillStyle = '#6c757d';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Document will be displayed here', width/2, height/2);
    ctx.font = '12px Arial';
    ctx.fillText('(Heatmap visualization in next iteration)', width/2, height/2 + 20);
    
    // Store detection regions for click handling
    heatmapRegions = [];
    
    // Combine all regions from signals
    if (signals.ela.findings) {
        signals.ela.findings.forEach(finding => {
            if (finding.region) {
                heatmapRegions.push({
                    ...finding,
                    signal: 'ela',
                    color: 'rgba(220, 53, 69, 0.3)' // Red for ELA
                });
            }
        });
    }
    
    if (signals.ocr.findings) {
        signals.ocr.findings.forEach(finding => {
            if (finding.region) {
                heatmapRegions.push({
                    ...finding,
                    signal: 'ocr',
                    color: 'rgba(255, 193, 7, 0.3)' // Yellow for OCR
                });
            }
        });
    }
    
    // Draw detection regions (for demo, draw sample regions)
    drawSampleRegions(ctx);
}

// Draw sample regions for demo
function drawSampleRegions(ctx) {
    // Sample regions for demo
    const sampleRegions = [
        {region: [100, 150, 200, 80], confidence: 90, description: 'Date field anomaly', signal: 'ela'},
        {region: [300, 250, 150, 50], confidence: 80, description: 'Amount field issue', signal: 'ocr'},
        {region: [200, 350, 100, 40], confidence: 70, description: 'Signature area', signal: 'ela'}
    ];
    
    sampleRegions.forEach(region => {
        const [x, y, width, height] = region.region;
        
        // Determine color based on confidence
        let color;
        if (region.confidence >= 80) {
            color = 'rgba(220, 53, 69, 0.5)'; // Red
        } else if (region.confidence >= 60) {
            color = 'rgba(255, 193, 7, 0.5)'; // Yellow
        } else {
            color = 'rgba(40, 167, 69, 0.5)'; // Green
        }
        
        // Draw rectangle
        ctx.fillStyle = color;
        ctx.fillRect(x, y, width, height);
        
        // Draw border
        ctx.strokeStyle = color.replace('0.5', '1');
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, width, height);
        
        // Store for click handling
        heatmapRegions.push(region);
    });
}

// Handle heatmap click
function handleHeatmapClick(event) {
    const rect = heatmapCanvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Scale coordinates to canvas size
    const scaleX = heatmapCanvas.width / rect.width;
    const scaleY = heatmapCanvas.height / rect.height;
    const canvasX = x * scaleX;
    const canvasY = y * scaleY;
    
    // Find clicked region
    const clickedRegion = heatmapRegions.find(region => {
        const [rx, ry, rwidth, rheight] = region.region;
        return canvasX >= rx && canvasX <= rx + rwidth &&
               canvasY >= ry && canvasY <= ry + rheight;
    });
    
    if (clickedRegion) {
        showRegionDetails(clickedRegion);
    }
}

// Show region details
function showRegionDetails(region) {
    const modalContent = `
        <div class="modal fade" id="regionModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Detection Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Signal:</strong> ${region.signal === 'ela' ? 'Error Level Analysis' : 'OCR Analysis'}</p>
                        <p><strong>Confidence:</strong> ${region.confidence}%</p>
                        <p><strong>Description:</strong> ${region.description}</p>
                        <p><strong>Location:</strong> Region detected in document</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal
    const existingModal = document.getElementById('regionModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalContent);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('regionModal'));
    modal.show();
}

// Show signal details
function showSignalDetails(signalType) {
    if (!detectionResults) return;
    
    const signal = detectionResults.signals[signalType];
    const signalName = signalType === 'ela' ? 'Error Level Analysis' : 
                      signalType === 'ocr' ? 'Text Inconsistency' : 
                      'Metadata Forensics';
    
    let findingsHTML = '';
    signal.findings.forEach((finding, index) => {
        findingsHTML += `
            <div class="mb-2 p-2 border rounded">
                <strong>Finding ${index + 1}:</strong> ${finding.description}<br>
                <small>Confidence: ${finding.confidence}%</small>
            </div>
        `;
    });
    
    const modalContent = `
        <div class="modal fade" id="signalModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${signalName} Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <strong>Summary:</strong> ${signal.summary}<br>
                            <strong>Overall Confidence:</strong> ${signal.confidence}%
                        </div>
                        <h6>Detailed Findings:</h6>
                        ${findingsHTML}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal
    const existingModal = document.getElementById('signalModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalContent);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('signalModal'));
    modal.show();
}

// Update detailed findings
function updateDetailedFindings(results) {
    let html = `
        <div class="alert alert-${results.verdict === 'SUSPICIOUS' ? 'warning' : 'success'}">
            <h5><i class="fas fa-${results.verdict === 'SUSPICIOUS' ? 'exclamation-triangle' : 'check-circle'}"></i> 
                Verdict: ${results.verdict}</h5>
            <p>Processing time: ${results.processing_time} seconds</p>
        </div>
        
        <h6>Recommendations:</h6>
        <ul class="list-group mb-3">
    `;
    
    results.recommendations.forEach(rec => {
        html += `<li class="list-group-item"><i class="fas fa-check-circle text-success"></i> ${rec}</li>`;
    });
    
    html += `</ul>`;
    
    detailedFindings.innerHTML = html;
}

// Generate forensic report
function generateForensicReport() {
    if (!detectionResults) {
        alert('No analysis results available');
        return;
    }
    
    // Create report content
    const reportContent = `
        DOCUMENT FORENSIC REPORT
        ========================
        
        Document ID: ${detectionResults.document_id}
        Analysis Time: ${new Date().toLocaleString()}
        
        OVERALL ASSESSMENT
        ------------------
        Confidence: ${detectionResults.confidence}%
        Uncertainty: ${detectionResults.uncertainty}%
        Verdict: ${detectionResults.verdict}
        
        SIGNAL ANALYSIS
        ---------------
        
        1. ERROR LEVEL ANALYSIS (${detectionResults.signals.ela.confidence}%)
           ${detectionResults.signals.ela.summary}
           
        2. TEXT INCONSISTENCY ANALYSIS (${detectionResults.signals.ocr.confidence}%)
           ${detectionResults.signals.ocr.summary}
           
        3. METADATA FORENSICS (${detectionResults.signals.metadata.confidence}%)
           ${detectionResults.signals.metadata.summary}
        
        RECOMMENDATIONS
        ---------------
        ${detectionResults.recommendations.map(r => `• ${r}`).join('\n        ')}
        
        ---
        Generated by DocVerify - Explainable Document Forgery Detection
        HackTheWinter 2024 • ML-103
    `;
    
    // Create and download file
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forensic_report_${detectionResults.document_id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    // Show success message
    alert('Forensic report downloaded successfully!');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
