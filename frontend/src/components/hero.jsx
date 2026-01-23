import "./Hero.css";
import { useRef, useState } from "react";

const Hero = () => {
    const fileInputRef = useRef(null);
    const [fileName, setFileName] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [results, setResults] = useState(null);
    const [processingProgress, setProcessingProgress] = useState(0);

    const ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg"];
    const MAX_SIZE = 16 * 1024 * 1024;

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const validateFile = (file) => {
        if (!ALLOWED_TYPES.includes(file.type)) {
            alert("Invalid file type. Please upload PDF, PNG, or JPG.");
            return false;
        }
        if (file.size > MAX_SIZE) {
            alert("File size exceeds 16MB limit.");
            return false;
        }
        return true;
    };

    const uploadToBackend = async (file) => {
        setUploading(true);
        setProcessingProgress(25);
        
        try {
            // 1. Upload file to Flask backend (using proxy)
            const formData = new FormData();
            formData.append('document', file);
            
            setProcessingProgress(50);
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const uploadData = await uploadResponse.json();
            
            if (!uploadResponse.ok) {
                throw new Error(uploadData.error || 'Upload failed');
            }
            
            // 2. Process document
            setProcessingProgress(75);
            const processResponse = await fetch(
                `/api/process/${uploadData.document_id}`
            );
            
            const processData = await processResponse.json();
            
            setProcessingProgress(100);
            
            // 3. Display results
            setResults(processData);
            
            // Show success message
            alert(`✅ Analysis complete!\nConfidence: ${processData.overall_confidence}%\nVerdict: ${processData.verdict}`);
            
            return processData;
            
        } catch (error) {
            console.error('API Error:', error);
            
            // Mock data for demo if backend fails
            const mockResults = {
                document_id: 'demo_' + Date.now(),
                overall_confidence: 78,
                uncertainty: 22,
                processing_time: 12.5,
                verdict: 'SUSPICIOUS',
                signals: {
                    ela: { 
                        name: 'Error Level Analysis',
                        confidence: 85, 
                        summary: 'Editing artifacts detected in 2 regions' 
                    },
                    ocr: { 
                        name: 'Text Inconsistency',
                        confidence: 70, 
                        summary: 'Font and alignment inconsistencies found' 
                    },
                    metadata: { 
                        name: 'Metadata Forensics',
                        confidence: 80, 
                        summary: 'Metadata anomalies detected' 
                    }
                }
            };
            
            setResults(mockResults);
            alert(`⚠️ Using demo data\nConfidence: ${mockResults.overall_confidence}%\nVerdict: ${mockResults.verdict}`);
            
            return mockResults;
            
        } finally {
            setUploading(false);
            setTimeout(() => setProcessingProgress(0), 1000);
        }
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            const file = files[0];
            if (validateFile(file)) {
                setFileName(file.name);
                console.log("File uploaded:", file);
                await uploadToBackend(file);
            }
        }
    };

    const handleFileSelect = async (e) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            const file = files[0];
            if (validateFile(file)) {
                setFileName(file.name);
                console.log("File uploaded:", file);
                await uploadToBackend(file);
            }
        }
    };

    const handleButtonClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <section className="w-full hero bg-blue-400">
            <div className="hero-left">
                <h1>Detect Document<br />Forgery with AI</h1>
                <p className="text-white">
                    Upload any document (PDF/Image) and get instant
                    forensic analysis with explainable signals.
                </p>

                <div className="badges">
                    <span>⚡ Under 20s</span>
                    <span>💻 CPU-only</span>
                    <span>🔍 3+ signals</span>
                    <span>📍 Localization</span>
                </div>
                
                {/* Show results if available */}
                {results && (
                    <div className="results mt-6 p-4 bg-white rounded-lg shadow-md">
                        <h3 className="text-xl font-bold mb-3">🔍 Analysis Results</h3>
                        
                        <div className="confidence-score mb-4">
                            <div className="flex justify-between items-center mb-2">
                                <span className="font-medium">Overall Confidence:</span>
                                <span className={`text-lg font-bold ${
                                    results.overall_confidence >= 80 ? 'text-red-600' : 
                                    results.overall_confidence >= 60 ? 'text-yellow-600' : 'text-green-600'
                                }`}>
                                    {results.overall_confidence}%
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                                <div 
                                    className={`h-2.5 rounded-full ${
                                        results.overall_confidence >= 80 ? 'bg-red-600' : 
                                        results.overall_confidence >= 60 ? 'bg-yellow-600' : 'bg-green-600'
                                    }`}
                                    style={{ width: `${results.overall_confidence}%` }}
                                ></div>
                            </div>
                        </div>
                        
                        <div className="verdict mb-4">
                            <div className="flex justify-between items-center">
                                <span className="font-medium">Verdict:</span>
                                <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                                    results.verdict === 'SUSPICIOUS' ? 'bg-red-100 text-red-800' : 
                                    results.verdict === 'LIKELY_AUTHENTIC' ? 'bg-green-100 text-green-800' : 
                                    'bg-yellow-100 text-yellow-800'
                                }`}>
                                    {results.verdict}
                                </span>
                            </div>
                        </div>
                        
                        <div className="signals grid grid-cols-1 gap-3">
                            {Object.entries(results.signals || {}).map(([key, signal]) => (
                                <div key={key} className="signal-item p-3 bg-gray-50 rounded">
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="font-medium">{signal.name || key.toUpperCase()}</span>
                                        <span className={`px-2 py-1 rounded text-xs ${
                                            signal.confidence >= 80 ? 'bg-red-100 text-red-800' : 
                                            signal.confidence >= 60 ? 'bg-yellow-100 text-yellow-800' : 
                                            'bg-green-100 text-green-800'
                                        }`}>
                                            {signal.confidence}%
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600">{signal.summary}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="hero-right">
                <div
                    className={`upload-box ${dragActive ? "drag-active" : ""}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <div className="icon">☁️</div>
                    <p>Drag & Drop or Click to Upload</p>
                    <small>PDF, PNG, JPG (Max 16MB)</small>
                    
                    {uploading && (
                        <div className="mt-6">
                            <div className="text-sm mb-2">Processing forensic analysis...</div>
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                                <div 
                                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                                    style={{ width: `${processingProgress}%` }}
                                ></div>
                            </div>
                            <div className="flex justify-between text-xs mt-1 text-gray-500">
                                <span>Uploading</span>
                                <span>Analyzing</span>
                                <span>Complete</span>
                            </div>
                        </div>
                    )}
                    
                    {fileName && !uploading && (
                        <p className="file-name mt-4">📄 {fileName}</p>
                    )}
                    
                    <button 
                        onClick={handleButtonClick}
                        disabled={uploading}
                        className={`mt-4 ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                        {uploading ? 'Processing...' : 'Choose Document'}
                    </button>
                    
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={handleFileSelect}
                        style={{ display: "none" }}
                        disabled={uploading}
                    />
                </div>
            </div>
        </section>
    );
};

export default Hero;