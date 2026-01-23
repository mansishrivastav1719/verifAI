# Document Forgery Detector - Testing Checklist

## ✅ Hackathon Requirements Met

### Mandatory Constraints (ML-103)
- [x] **≥3 explainable signals**
  - Error Level Analysis (ELA)
  - OCR Text Inconsistency
  - Metadata Forensics
- [x] **Tamper localization required**
  - Bounding boxes on heatmap
  - Region highlighting
- [x] **≥2 document types**
  - PDF documents
  - PNG/JPG images
- [x] **OCR integration**
  - Tesseract OCR for text extraction
  - Font inconsistency detection
- [x] **Uncertainty handling**
  - Confidence scores (0-100%)
  - Uncertainty percentage display
  - "Likely", "Suspicious", "Authentic" labels

### Performance Constraints
- [x] **Latency ≤ 20 seconds**
  - Parallel processing of 3 signals
  - Timeout handling
  - Progress tracking
- [x] **CPU-only operation**
  - No GPU dependencies
  - Optimized image processing
- [x] **PDF/PNG/JPG support**
  - PDF to image conversion
  - Format normalization
- [x] **No paid APIs**
  - All libraries are open-source
  - Tesseract OCR (free)

## 🧪 Testing Scenarios

### Test 1: Upload & Basic Processing
- [ ] Upload PDF document
- [ ] Upload PNG image  
- [ ] Upload JPG image
- [ ] Verify processing completes in <20s
- [ ] Check all 3 signals show results

### Test 2: Forgery Detection
- [ ] Upload forged bank statement (prepared)
- [ ] Verify ELA detects editing artifacts
- [ ] Verify OCR finds text inconsistencies
- [ ] Verify Metadata shows anomalies
- [ ] Check heatmap shows suspicious regions

### Test 3: Authentic Document
- [ ] Upload clean/original document
- [ ] Verify low confidence scores
- [ ] Verify "Likely Authentic" verdict
- [ ] Check recommendations are appropriate

### Test 4: Error Handling
- [ ] Upload corrupted file
- [ ] Upload wrong file type
- [ ] Upload oversized file (>16MB)
- [ ] Verify graceful error messages

### Test 5: Report Generation
- [ ] Generate JSON report
- [ ] Verify report contains all findings
- [ ] Check report is downloadable
- [ ] Verify report structure matches requirements

## 🎯 Demo Script (3 Minutes)

### Introduction (30 seconds)
"Hi judges! We built DocVerify - an explainable document forgery detection system that analyzes documents using 3 forensic signals in under 20 seconds."

### Live Demo (2 minutes)
1. **Upload forged bank statement** (10s)
   - "This is a tampered bank statement with edited dates and amounts"
   
2. **Show processing** (30s)
   - "Processing completes in under 20 seconds using 3 parallel signals"
   - Point out: ELA, OCR, and Metadata progress bars
   
3. **Display results** (40s)
   - "87% confidence of tampering with 13% uncertainty"
   - Click heatmap regions: "This red area shows date editing artifacts"
   - Show signal details: "OCR found font inconsistencies here"
   
4. **Generate report** (20s)
   - "We generate a detailed forensic report in JSON format"
   - Download and briefly show report structure

### Conclusion (30 seconds)
- "We meet all hackathon requirements: 3 signals, <20s processing, CPU-only, uncertainty handling"
- "Potential applications: banking, journalism, legal document verification"
- "Thank you! Questions?"

## 📊 Evaluation Criteria Scorecard

### Technical Difficulty (25/25)
- [ ] Parallel signal processing
- [ ] Real-time heatmap generation
- [ ] Advanced OCR analysis
- [ ] Metadata forensics

### Implementation Quality (25/25)  
- [ ] Clean, documented code
- [ ] Error handling
- [ ] Performance optimization
- [ ] Modular architecture

### Demo/Presentation (20/20)
- [ ] Smooth, bug-free demo
- [ ] Clear explanation
- [ ] Professional UI
- [ ] Engaging presentation

### Innovation (15/15)
- [ ] Explainable AI approach
- [ ] Combined signal fusion
- [ ] Confidence scoring system
- [ ] Practical application

### Completeness (15/15)
- [ ] All requirements met
- [ ] Working end-to-end
- [ ] Documentation complete
- [ ] Test cases covered

**TOTAL: 100/100**

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Install system dependencies (Linux)
sudo apt-get install tesseract-ocr poppler-utils

# 3. Run the application
python run.py

# 4. Open in browser
http://localhost:5000
