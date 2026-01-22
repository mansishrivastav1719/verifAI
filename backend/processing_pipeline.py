"""
Main Processing Pipeline for Document Forgery Detection
Integrates all 3 forensic signals and manages parallel processing
"""

import os
import time
import threading
import concurrent.futures
from typing import Dict, List, Tuple
from config import Config
from utils.ela_analyzer import ELAAnalyzer
from utils.ocr_analyzer import OCRAnalyzer
from utils.metadata_analyzer import MetadataAnalyzer
from utils.pdf_converter import PDFConverter
from utils.file_handler import FileHandler

class ProcessingPipeline:
    """Orchestrates the complete document forgery detection pipeline"""
    
    def __init__(self):
        self.results_cache = {}
        self.processing_times = {}
    
    def process_document(self, document_id: str, file_path: str) -> Dict:
        """
        Process a document through all 3 forensic signals
        
        Args:
            document_id: Unique identifier for the document
            file_path: Path to the document file
            
        Returns:
            dict: Complete analysis results
        """
        start_time = time.time()
        
        # Check if already processed
        if document_id in self.results_cache:
            return self.results_cache[document_id]
        
        try:
            # Step 1: Prepare document for processing
            processing_path = self._prepare_document(file_path)
            
            # Step 2: Run all 3 signals in parallel
            signals_results = self._run_parallel_analysis(processing_path)
            
            # Step 3: Fuse results and calculate overall confidence
            final_results = self._fuse_results(
                document_id, 
                signals_results, 
                file_path
            )
            
            # Step 4: Calculate total processing time
            processing_time = time.time() - start_time
            final_results['processing_time'] = round(processing_time, 2)
            
            # Step 5: Generate reports
            reports = self._generate_reports(final_results, file_path)
            final_results['reports'] = reports
            
            # Cache results
            self.results_cache[document_id] = final_results
            self.processing_times[document_id] = processing_time
            
            # Cleanup temporary files
            self._cleanup_temp_files(processing_path, file_path)
            
            return final_results
            
        except Exception as e:
            error_result = self._create_error_result(document_id, str(e))
            return error_result
    
    def _prepare_document(self, file_path: str) -> str:
        """
        Prepare document for analysis (convert PDF to image if needed)
        
        Args:
            file_path: Path to original document
            
        Returns:
            str: Path to prepared image for analysis
        """
        # Check if file is PDF
        if PDFConverter.is_pdf(file_path):
            # Extract first page as image
            _, first_page_path = PDFConverter.extract_first_page(
                file_path,
                os.path.join(Config.TEMP_DIR, f"first_page_{os.path.basename(file_path)}.png")
            )
            
            if first_page_path:
                return first_page_path
        
        # If already an image, convert to PNG if needed
        if not file_path.endswith('.png'):
            png_path = PDFConverter.convert_to_png(
                file_path,
                os.path.join(Config.TEMP_DIR, f"{os.path.basename(file_path)}.png")
            )
            return png_path
        
        return file_path
    
    def _run_parallel_analysis(self, image_path: str) -> Dict:
        """
        Run all 3 forensic signals in parallel
        
        Args:
            image_path: Path to image for analysis
            
        Returns:
            dict: Results from all signals
        """
        signals_results = {
            'ela': None,
            'ocr': None,
            'metadata': None,
            'errors': []
        }
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            ela_future = executor.submit(ELAAnalyzer.analyze, image_path)
            ocr_future = executor.submit(OCRAnalyzer.analyze, image_path)
            metadata_future = executor.submit(MetadataAnalyzer.analyze, image_path)
            
            # Collect results with timeout
            try:
                signals_results['ela'] = ela_future.result(timeout=15)
            except concurrent.futures.TimeoutError:
                signals_results['errors'].append('ELA analysis timeout')
                signals_results['ela'] = {'error': 'Timeout', 'overall_confidence': 0}
            except Exception as e:
                signals_results['errors'].append(f'ELA error: {str(e)}')
                signals_results['ela'] = {'error': str(e), 'overall_confidence': 0}
            
            try:
                signals_results['ocr'] = ocr_future.result(timeout=15)
            except concurrent.futures.TimeoutError:
                signals_results['errors'].append('OCR analysis timeout')
                signals_results['ocr'] = {'error': 'Timeout', 'overall_confidence': 0}
            except Exception as e:
                signals_results['errors'].append(f'OCR error: {str(e)}')
                signals_results['ocr'] = {'error': str(e), 'overall_confidence': 0}
            
            try:
                signals_results['metadata'] = metadata_future.result(timeout=15)
            except concurrent.futures.TimeoutError:
                signals_results['errors'].append('Metadata analysis timeout')
                signals_results['metadata'] = {'error': 'Timeout', 'overall_confidence': 0}
            except Exception as e:
                signals_results['errors'].append(f'Metadata error: {str(e)}')
                signals_results['metadata'] = {'error': str(e), 'overall_confidence': 0}
        
        return signals_results
    
    def _fuse_results(self, document_id: str, signals_results: Dict, original_path: str) -> Dict:
        """
        Fuse results from all 3 signals and calculate overall assessment
        
        Args:
            document_id: Document identifier
            signals_results: Results from all signals
            original_path: Path to original document
            
        Returns:
            dict: Fused results with overall assessment
        """
        # Extract confidence scores
        ela_conf = signals_results['ela'].get('overall_confidence', 0) if signals_results['ela'] else 0
        ocr_conf = signals_results['ocr'].get('overall_confidence', 0) if signals_results['ocr'] else 0
        meta_conf = signals_results['metadata'].get('overall_confidence', 0) if signals_results['metadata'] else 0
        
        # Weighted fusion (ELA is most reliable for images)
        weights = {'ela': 0.4, 'ocr': 0.3, 'metadata': 0.3}
        
        overall_confidence = (
            ela_conf * weights['ela'] + 
            ocr_conf * weights['ocr'] + 
            meta_conf * weights['metadata']
        )
        
        # Calculate uncertainty (inverse of confidence)
        uncertainty = max(0, 100 - overall_confidence)
        
        # Determine verdict
        verdict = self._determine_verdict(overall_confidence, signals_results)
        
        # Prepare combined findings
        combined_findings = self._combine_findings(signals_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(verdict, signals_results)
        
        # Prepare final results
        final_results = {
            'document_id': document_id,
            'original_path': original_path,
            'overall_confidence': round(overall_confidence, 2),
            'uncertainty': round(uncertainty, 2),
            'verdict': verdict,
            'signals': {
                'ela': self._format_signal_results(signals_results['ela'], 'Error Level Analysis'),
                'ocr': self._format_signal_results(signals_results['ocr'], 'Text Inconsistency'),
                'metadata': self._format_signal_results(signals_results['metadata'], 'Metadata Forensics')
            },
            'combined_findings': combined_findings,
            'recommendations': recommendations,
            'signal_confidences': {
                'ela': round(ela_conf, 2),
                'ocr': round(ocr_conf, 2),
                'metadata': round(meta_conf, 2)
            },
            'errors': signals_results.get('errors', [])
        }
        
        return final_results
    
    def _format_signal_results(self, signal_results: Dict, signal_name: str) -> Dict:
        """Format signal results for consistent output"""
        if not signal_results or 'error' in signal_results:
            return {
                'name': signal_name,
                'confidence': 0,
                'summary': 'Analysis failed or not available',
                'findings': [],
                'status': 'error'
            }
        
        return {
            'name': signal_name,
            'confidence': signal_results.get('overall_confidence', 0),
            'summary': signal_results.get('analysis_summary', 'No summary available'),
            'findings': signal_results.get('anomalies', []) or signal_results.get('inconsistencies', []) or [],
            'regions': signal_results.get('regions', []),
            'status': 'completed'
        }
    
    def _determine_verdict(self, confidence: float, signals_results: Dict) -> str:
        """Determine final verdict based on confidence and findings"""
        
        if confidence >= 80:
            return "HIGHLY_SUSPICIOUS"
        elif confidence >= 60:
            return "SUSPICIOUS"
        elif confidence >= 40:
            return "MODERATELY_SUSPICIOUS"
        elif confidence >= 20:
            return "SLIGHTLY_SUSPICIOUS"
        else:
            # Check if any signal has high confidence findings
            high_confidence_findings = False
            
            for signal in ['ela', 'ocr', 'metadata']:
                sig_results = signals_results.get(signal)
                if sig_results and not isinstance(sig_results, dict):
                    continue
                    
                if sig_results and 'confidence' in sig_results:
                    if sig_results.get('overall_confidence', 0) > 70:
                        high_confidence_findings = True
                        break
            
            if high_confidence_findings:
                return "NEEDS_REVIEW"
            else:
                return "LIKELY_AUTHENTIC"
    
    def _combine_findings(self, signals_results: Dict) -> List[Dict]:
        """Combine findings from all signals"""
        combined = []
        
        # Add ELA findings
        ela_results = signals_results.get('ela', {})
        if ela_results and 'regions' in ela_results:
            for region in ela_results.get('regions', []):
                combined.append({
                    'type': 'ELA',
                    'confidence': region.get('confidence', 0),
                    'description': f"Editing artifacts detected (confidence: {region.get('confidence', 0)}%)",
                    'bbox': region.get('bbox', []),
                    'signal': 'ela'
                })
        
        # Add OCR findings
        ocr_results = signals_results.get('ocr', {})
        if ocr_results and 'inconsistencies' in ocr_results:
            for inc in ocr_results.get('inconsistencies', []):
                combined.append({
                    'type': 'OCR',
                    'confidence': inc.get('confidence', 0),
                    'description': inc.get('description', 'Text inconsistency'),
                    'details': inc.get('details', {}),
                    'signal': 'ocr'
                })
        
        # Add Metadata findings
        meta_results = signals_results.get('metadata', {})
        if meta_results and 'anomalies' in meta_results:
            for anomaly in meta_results.get('anomalies', []):
                combined.append({
                    'type': 'Metadata',
                    'confidence': anomaly.get('confidence', 0),
                    'description': anomaly.get('description', 'Metadata anomaly'),
                    'details': anomaly.get('details', {}),
                    'signal': 'metadata'
                })
        
        # Sort by confidence (highest first)
        combined.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return combined[:10]  # Limit to top 10 findings
    
    def _generate_recommendations(self, verdict: str, signals_results: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # General recommendations based on verdict
        if verdict in ["HIGHLY_SUSPICIOUS", "SUSPICIOUS"]:
            recommendations.extend([
                "Verify document with issuing authority",
                "Cross-check dates and amounts with original records",
                "Request certified copy for comparison"
            ])
        
        elif verdict == "MODERATELY_SUSPICIOUS":
            recommendations.extend([
                "Review highlighted regions carefully",
                "Check for supporting documentation",
                "Consider digital signature verification"
            ])
        
        elif verdict == "SLIGHTLY_SUSPICIOUS":
            recommendations.extend([
                "Minor anomalies detected - review if critical document",
                "Check for scanning artifacts",
                "Verify metadata consistency"
            ])
        
        else:  # LIKELY_AUTHENTIC or NEEDS_REVIEW
            recommendations.append("Document appears authentic. No immediate action required.")
        
        # Signal-specific recommendations
        ela_results = signals_results.get('ela', {})
        if ela_results and 'overall_confidence' in ela_results:
            if ela_results['overall_confidence'] > 70:
                recommendations.append("High ELA confidence: Document shows clear editing artifacts")
        
        ocr_results = signals_results.get('ocr', {})
        if ocr_results and 'inconsistencies' in ocr_results:
            if len(ocr_results['inconsistencies']) > 2:
                recommendations.append("Multiple text inconsistencies: Verify font and formatting")
        
        meta_results = signals_results.get('metadata', {})
        if meta_results and 'anomalies' in meta_results:
            date_anomalies = [a for a in meta_results['anomalies'] if 'date' in a.get('type', '')]
            if date_anomalies:
                recommendations.append("Date anomalies: Verify creation and modification dates")
        
        return list(set(recommendations))[:5]  # Remove duplicates, limit to 5
    
    def _generate_reports(self, results: Dict, file_path: str) -> Dict:
        """Generate JSON and PDF reports"""
        reports = {
            'json': self._generate_json_report(results),
            'pdf': None  # PDF generation can be added later
        }
        
        # Save JSON report to file
        json_report_path = os.path.join(
            Config.UPLOAD_FOLDER, 
            f"report_{results['document_id']}.json"
        )
        
        import json
        with open(json_report_path, 'w') as f:
            json.dump(reports['json'], f, indent=2)
        
        reports['json_path'] = json_report_path
        
        return reports
    
    def _generate_json_report(self, results: Dict) -> Dict:
        """Generate comprehensive JSON report"""
        report = {
            'document_forensics_report': {
                'metadata': {
                    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'document_id': results['document_id'],
                    'analysis_version': '1.0'
                },
                'overall_assessment': {
                    'confidence': results['overall_confidence'],
                    'uncertainty': results['uncertainty'],
                    'verdict': results['verdict'],
                    'processing_time': results.get('processing_time', 0)
                },
                'signal_analysis': {},
                'detailed_findings': results['combined_findings'],
                'recommendations': results['recommendations']
            }
        }
        
        # Add signal details
        for signal_name, signal_data in results['signals'].items():
            report['document_forensics_report']['signal_analysis'][signal_name] = {
                'confidence': signal_data['confidence'],
                'summary': signal_data['summary'],
                'findings_count': len(signal_data['findings']),
                'status': signal_data['status']
            }
        
        return report
    
    def _cleanup_temp_files(self, processing_path: str, original_path: str):
        """Clean up temporary files created during processing"""
        try:
            # Don't delete original uploaded file
            if processing_path != original_path:
                if os.path.exists(processing_path):
                    os.remove(processing_path)
            
            # Clean up temp directory
            temp_files = os.listdir(Config.TEMP_DIR)
            for temp_file in temp_files:
                if temp_file.endswith('.png') or temp_file.endswith('.jpg'):
                    temp_path = os.path.join(Config.TEMP_DIR, temp_file)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
        except Exception as e:
            print(f"Cleanup error (non-critical): {e}")
    
    def _create_error_result(self, document_id: str, error_message: str) -> Dict:
        """Create error result when processing fails"""
        return {
            'document_id': document_id,
            'error': True,
            'error_message': error_message,
            'overall_confidence': 0,
            'uncertainty': 100,
            'verdict': 'PROCESSING_ERROR',
            'processing_time': 0,
            'signals': {
                'ela': {'status': 'error', 'confidence': 0, 'summary': 'Analysis failed'},
                'ocr': {'status': 'error', 'confidence': 0, 'summary': 'Analysis failed'},
                'metadata': {'status': 'error', 'confidence': 0, 'summary': 'Analysis failed'}
            },
            'combined_findings': [],
            'recommendations': ['Processing failed. Please try again or upload a different document.'],
            'reports': {}
        }
    
    def get_processing_stats(self) -> Dict:
        """Get pipeline processing statistics"""
        return {
            'documents_processed': len(self.results_cache),
            'average_processing_time': (
                sum(self.processing_times.values()) / len(self.processing_times) 
                if self.processing_times else 0
            ),
            'cache_size': len(self.results_cache)
        }
    
    def clear_cache(self):
        """Clear results cache"""
        self.results_cache.clear()
        self.processing_times.clear()
    
    @staticmethod
    def test_pipeline():
        """Test the complete processing pipeline"""
        import tempfile
        from PIL import Image
        
        # Create a test image
        test_image = Image.new('RGB', (400, 300), color='white')
        test_path = tempfile.mktemp(suffix='_test_pipeline.jpg')
        test_image.save(test_path, 'JPEG', quality=95)
        
        # Process through pipeline
        pipeline = ProcessingPipeline()
        document_id = 'test_' + os.path.basename(test_path).split('.')[0]
        
        print(f"Testing pipeline with document: {document_id}")
        
        results = pipeline.process_document(document_id, test_path)
        
        # Cleanup
        os.remove(test_path)
        
        print(f"Pipeline test completed:")
        print(f"Overall confidence: {results['overall_confidence']}%")
        print(f"Verdict: {results['verdict']}")
        print(f"Processing time: {results['processing_time']}s")
        
        return results


# Global pipeline instance
pipeline_instance = ProcessingPipeline()
