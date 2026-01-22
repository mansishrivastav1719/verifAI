"""
OCR Text Inconsistency Analyzer
Detects font, size, and alignment inconsistencies in documents
"""

import pytesseract
import cv2
import numpy as np
from PIL import Image
import re
from collections import defaultdict
from config import Config

class OCRAnalyzer:
    """OCR-based text inconsistency detection"""
    
    @staticmethod
    def analyze(image_path, language='eng'):
        """
        Perform OCR analysis to detect text inconsistencies
        
        Args:
            image_path: Path to the image file
            language: OCR language (default: English)
            
        Returns:
            dict: Analysis results including text regions and inconsistencies
        """
        try:
            # Read and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to grayscale for OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing for better OCR
            processed = OCRAnalyzer.preprocess_image(gray)
            
            # Perform OCR with detailed output
            ocr_data = pytesseract.image_to_data(
                processed, 
                output_type=pytesseract.Output.DICT,
                config=Config.TESSERACT_CONFIG,
                lang=language
            )
            
            # Extract and analyze text regions
            text_regions = OCRAnalyzer.extract_text_regions(ocr_data)
            
            # Analyze for inconsistencies
            inconsistencies = OCRAnalyzer.detect_inconsistencies(text_regions, image.shape)
            
            # Calculate overall confidence
            overall_confidence = OCRAnalyzer.calculate_confidence(inconsistencies, len(text_regions))
            
            # Generate summary
            summary = OCRAnalyzer.generate_summary(inconsistencies, overall_confidence)
            
            # Prepare results
            results = {
                'overall_confidence': round(float(overall_confidence), 2),
                'text_blocks_found': len(text_regions),
                'total_characters': sum(len(region['text']) for region in text_regions),
                'inconsistencies_found': len(inconsistencies),
                'inconsistencies': inconsistencies,
                'text_regions': text_regions[:10],  # Limit to first 10 for response size
                'analysis_summary': summary,
                'ocr_raw_word_count': len(ocr_data.get('text', []))
            }
            
            return results
            
        except Exception as e:
            print(f"OCR Analysis Error: {e}")
            return {
                'overall_confidence': 0,
                'text_blocks_found': 0,
                'total_characters': 0,
                'inconsistencies_found': 0,
                'inconsistencies': [],
                'text_regions': [],
                'analysis_summary': f"OCR analysis failed: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def preprocess_image(image):
        """
        Preprocess image for better OCR results
        
        Args:
            image: Grayscale image (numpy array)
            
        Returns:
            numpy array: Preprocessed image
        """
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            image, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply slight dilation to connect broken text
        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # Denoise
        denoised = cv2.medianBlur(dilated, 3)
        
        return denoised
    
    @staticmethod
    def extract_text_regions(ocr_data):
        """
        Extract text regions from OCR data
        
        Args:
            ocr_data: Tesseract OCR output dictionary
            
        Returns:
            list: List of text region dictionaries
        """
        regions = []
        
        n_boxes = len(ocr_data['level'])
        for i in range(n_boxes):
            # Extract bounding box
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]
            text = ocr_data['text'][i].strip()
            conf = ocr_data['conf'][i]
            
            # Skip empty text and low confidence detections
            if not text or conf < 30 or text.isspace():
                continue
            
            # Skip very small regions (likely noise)
            if w < 10 or h < 10:
                continue
            
            # Calculate region properties
            region = {
                'bbox': [x, y, w, h],
                'text': text,
                'confidence': float(conf),
                'area': w * h,
                'aspect_ratio': w / h if h > 0 else 0,
                'font_size_estimate': h,  # Height as proxy for font size
                'line_num': ocr_data['line_num'][i],
                'block_num': ocr_data['block_num'][i],
                'par_num': ocr_data['par_num'][i]
            }
            
            regions.append(region)
        
        return regions
    
    @staticmethod
    def detect_inconsistencies(text_regions, image_shape):
        """
        Detect text inconsistencies in the document
        
        Args:
            text_regions: List of text region dictionaries
            image_shape: Shape of original image (height, width, channels)
            
        Returns:
            list: List of inconsistency findings
        """
        if len(text_regions) < 2:
            return []
        
        inconsistencies = []
        
        # Group regions by likely lines/paragraphs
        lines = OCRAnalyzer.group_into_lines(text_regions)
        
        # 1. Check font size inconsistency within lines
        for line_num, line_regions in lines.items():
            if len(line_regions) > 1:
                font_sizes = [r['font_size_estimate'] for r in line_regions]
                font_size_std = np.std(font_sizes)
                font_size_mean = np.mean(font_sizes)
                
                if font_size_std > font_size_mean * 0.2:  # More than 20% variation
                    inconsistency = {
                        'type': 'font_size_inconsistency',
                        'regions': [r['bbox'] for r in line_regions],
                        'line': line_num,
                        'confidence': min(90, font_size_std * 2),
                        'description': f"Font size varies significantly within line {line_num}",
                        'details': {
                            'mean_font_size': round(font_size_mean, 2),
                            'std_deviation': round(font_size_std, 2),
                            'variation_percentage': round((font_size_std / font_size_mean) * 100, 2)
                        }
                    }
                    inconsistencies.append(inconsistency)
        
        # 2. Check alignment inconsistencies
        for i in range(len(text_regions) - 1):
            for j in range(i + 1, len(text_regions)):
                region1 = text_regions[i]
                region2 = text_regions[j]
                
                # Check if regions are on same line (similar y-coordinates)
                y1, h1 = region1['bbox'][1], region1['bbox'][3]
                y2, h2 = region2['bbox'][1], region2['bbox'][3]
                
                # Calculate vertical overlap
                vertical_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                min_height = min(h1, h2)
                
                if vertical_overlap > min_height * 0.5:  # Same line
                    # Check horizontal alignment
                    x1, x2 = region1['bbox'][0], region2['bbox'][0]
                    expected_alignment = abs(x1 - x2) < 20  # Within 20 pixels
                    
                    if not expected_alignment and region1['line_num'] == region2['line_num']:
                        inconsistency = {
                            'type': 'alignment_inconsistency',
                            'regions': [region1['bbox'], region2['bbox']],
                            'confidence': 65,
                            'description': f"Text blocks on same line have different alignments",
                            'details': {
                                'block1_text': region1['text'][:20],
                                'block2_text': region2['text'][:20],
                                'x_positions': [x1, x2],
                                'difference': abs(x1 - x2)
                            }
                        }
                        inconsistencies.append(inconsistency)
        
        # 3. Check for abnormal spacing
        for i in range(len(text_regions) - 1):
            region1 = text_regions[i]
            region2 = text_regions[i + 1]
            
            x1, w1 = region1['bbox'][0], region1['bbox'][2]
            x2 = region2['bbox'][0]
            
            # Calculate gap between regions
            gap = x2 - (x1 + w1)
            
            if gap > 100:  # Unusually large gap
                inconsistency = {
                    'type': 'abnormal_spacing',
                    'regions': [region1['bbox'], region2['bbox']],
                    'confidence': min(80, gap / 10),
                    'description': f"Abnormally large gap between text blocks",
                    'details': {
                        'gap_pixels': gap,
                        'block1_text': region1['text'][:20],
                        'block2_text': region2['text'][:20]
                    }
                }
                inconsistencies.append(inconsistency)
        
        # 4. Check for text that looks edited (mixed fonts within same word/line)
        for region in text_regions:
            text = region['text']
            # Look for pattern changes that might indicate editing
            if len(text) > 3:
                # Check for mixed case in a way that suggests editing
                has_lower = any(c.islower() for c in text)
                has_upper = any(c.isupper() for c in text)
                has_digit = any(c.isdigit() for c in text)
                
                if (has_lower and has_upper and len(text) < 10 and 
                    not text[0].isupper() and not text.isupper()):
                    # Mixed case in short text not starting with capital
                    inconsistency = {
                        'type': 'mixed_formatting',
                        'regions': [region['bbox']],
                        'confidence': 70,
                        'description': f"Mixed character formatting in text: '{text[:30]}'",
                        'details': {
                            'text': text,
                            'length': len(text)
                        }
                    }
                    inconsistencies.append(inconsistency)
        
        return inconsistencies
    
    @staticmethod
    def group_into_lines(text_regions, tolerance=10):
        """
        Group text regions into lines based on vertical position
        
        Args:
            text_regions: List of text region dictionaries
            tolerance: Vertical tolerance for same line (pixels)
            
        Returns:
            dict: Lines grouped by line number
        """
        lines = defaultdict(list)
        
        # Sort by y-position
        sorted_regions = sorted(text_regions, key=lambda r: r['bbox'][1])
        
        current_line = 0
        current_y = None
        
        for region in sorted_regions:
            y = region['bbox'][1]
            
            if current_y is None:
                current_y = y
                lines[current_line].append(region)
            elif abs(y - current_y) <= tolerance:
                lines[current_line].append(region)
            else:
                current_line += 1
                current_y = y
                lines[current_line].append(region)
        
        return dict(lines)
    
    @staticmethod
    def calculate_confidence(inconsistencies, total_regions):
        """
        Calculate overall confidence score for OCR analysis
        
        Args:
            inconsistencies: List of inconsistency findings
            total_regions: Total number of text regions found
            
        Returns:
            float: Confidence score (0-100)
        """
        if total_regions == 0:
            return 0
        
        # Base score based on number of inconsistencies
        inconsistency_score = min(100, len(inconsistencies) * 20)
        
        # Adjust based on severity
        severity_sum = 0
        for inc in inconsistencies:
            severity_sum += inc.get('confidence', 50)
        
        if inconsistencies:
            avg_severity = severity_sum / len(inconsistencies)
            final_score = (inconsistency_score * 0.4) + (avg_severity * 0.6)
        else:
            # No inconsistencies found - document likely authentic
            final_score = max(0, 100 - (total_regions * 2))
        
        return min(100, max(0, final_score))
    
    @staticmethod
    def generate_summary(inconsistencies, overall_confidence):
        """Generate human-readable summary of OCR findings"""
        
        if not inconsistencies:
            if overall_confidence < 30:
                return "No text inconsistencies detected. Document formatting appears consistent."
            else:
                return "Minor text anomalies detected. Document likely authentic."
        
        # Count inconsistency types
        type_counts = defaultdict(int)
        for inc in inconsistencies:
            type_counts[inc['type']] += 1
        
        # Generate summary based on findings
        total_inc = len(inconsistencies)
        
        if total_inc >= 3:
            return f"Multiple text inconsistencies detected ({total_inc} issues). Document shows signs of text editing or manipulation."
        elif total_inc == 2:
            return f"Two text inconsistencies detected. Document may have been altered."
        elif total_inc == 1:
            inc_type = inconsistencies[0]['type']
            if 'font' in inc_type:
                return "Font inconsistency detected. Text appears to have been edited."
            elif 'alignment' in inc_type:
                return "Alignment inconsistency detected. Document formatting appears inconsistent."
            else:
                return "Text inconsistency detected. Further verification recommended."
        else:
            return f"{total_inc} text anomalies detected."
    
    @staticmethod
    def visualize_text_regions(image_path, text_regions, output_path=None):
        """
        Visualize detected text regions on image
        
        Args:
            image_path: Path to original image
            text_regions: List of text region dictionaries
            output_path: Path to save visualization
            
        Returns:
            str: Path to saved visualization
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Draw bounding boxes for text regions
            for region in text_regions:
                x, y, w, h = region['bbox']
                
                # Different colors for different confidence levels
                conf = region.get('confidence', 0)
                if conf >= 70:
                    color = (0, 0, 255)  # Red for high confidence
                elif conf >= 40:
                    color = (0, 165, 255)  # Orange for medium
                else:
                    color = (0, 255, 255)  # Yellow for low
                
                cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
                
                # Add text label (truncated)
                text = region.get('text', '')[:15]
                if text:
                    cv2.putText(image, text, (x, y-5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Save or return image
            if output_path:
                cv2.imwrite(output_path, image)
                return output_path
            else:
                # Save to temp location
                import tempfile
                temp_path = tempfile.mktemp(suffix='_ocr_viz.png')
                cv2.imwrite(temp_path, image)
                return temp_path
                
        except Exception as e:
            print(f"Visualization error: {e}")
            return None
    
    @staticmethod
    def test_with_sample():
        """Test OCR analyzer with a sample image"""
        # Create a simple test image with text
        test_image = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        # Add consistent text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(test_image, "Consistent Text", (50, 100), font, 1, (0, 0, 0), 2)
        cv2.putText(test_image, "More Consistent", (50, 150), font, 1, (0, 0, 0), 2)
        
        # Add inconsistent text (different size)
        cv2.putText(test_image, "INCONSISTENT", (50, 220), font, 1.5, (0, 0, 0), 2)
        
        # Save test image
        import tempfile
        test_path = tempfile.mktemp(suffix='_test_ocr.jpg')
        cv2.imwrite(test_path, test_image)
        
        # Analyze
        results = OCRAnalyzer.analyze(test_path)
        
        # Cleanup
        import os
        os.remove(test_path)
        
        return results
