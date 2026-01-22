"""
Error Level Analysis (ELA) for detecting document tampering
Analyzes JPEG compression levels to find edited regions
"""

import cv2
import numpy as np
from PIL import Image
import os
import tempfile
from config import Config

class ELAAnalyzer:
    """Error Level Analysis for detecting image manipulation"""
    
    @staticmethod
    def analyze(image_path, quality=Config.ELA_QUALITY):
        """
        Perform Error Level Analysis on an image
        
        Args:
            image_path: Path to the image file
            quality: JPEG quality for re-saving (default 95)
            
        Returns:
            dict: Analysis results including heatmap and suspicious regions
        """
        try:
            # Read image
            original = cv2.imread(image_path)
            if original is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to RGB if needed
            if len(original.shape) == 2:  # Grayscale
                original = cv2.cvtColor(original, cv2.COLOR_GRAY2RGB)
            elif original.shape[2] == 4:  # RGBA
                original = cv2.cvtColor(original, cv2.COLOR_RGBA2RGB)
            
            # Save and reload at specified quality
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, "temp_ela.jpg")
            
            # Save with specified quality
            cv2.imwrite(temp_path, original, [cv2.IMWRITE_JPEG_QUALITY, quality])
            resaved = cv2.imread(temp_path)
            
            # Clean up temp file
            os.remove(temp_path)
            os.rmdir(temp_dir)
            
            # Calculate absolute difference
            diff = cv2.absdiff(original, resaved)
            
            # Convert to grayscale for analysis
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
            
            # Normalize to 0-255
            diff_normalized = cv2.normalize(diff_gray, None, 0, 255, cv2.NORM_MINMAX)
            
            # Apply threshold to find suspicious regions
            _, binary = cv2.threshold(diff_normalized, Config.ELA_THRESHOLD, 255, cv2.THRESH_BINARY)
            
            # Find contours of suspicious regions
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process contours into regions
            regions = []
            total_suspicious_pixels = 0
            total_pixels = original.shape[0] * original.shape[1]
            
            for contour in contours:
                # Filter small contours (noise)
                area = cv2.contourArea(contour)
                if area < 100:  # Minimum area threshold
                    continue
                
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate confidence based on area and intensity
                region_mask = np.zeros_like(diff_gray)
                cv2.drawContours(region_mask, [contour], -1, 255, -1)
                region_intensity = np.mean(diff_normalized[region_mask == 255])
                
                # Confidence score (0-100)
                confidence = min(100, (region_intensity / 255) * 100)
                
                # Skip low confidence regions
                if confidence < 20:
                    continue
                
                regions.append({
                    'bbox': [int(x), int(y), int(w), int(h)],  # [x, y, width, height]
                    'area': int(area),
                    'confidence': round(float(confidence), 2),
                    'intensity': round(float(region_intensity), 2)
                })
                
                total_suspicious_pixels += area
            
            # Calculate overall confidence score
            suspicious_ratio = total_suspicious_pixels / total_pixels if total_pixels > 0 else 0
            overall_confidence = min(100, suspicious_ratio * 200)  # Scale ratio to 0-100
            
            # Generate heatmap visualization
            heatmap_path = ELAAnalyzer.generate_heatmap(original, diff_normalized, regions)
            
            # Prepare results
            results = {
                'overall_confidence': round(float(overall_confidence), 2),
                'suspicious_ratio': round(float(suspicious_ratio * 100), 2),  # Percentage
                'regions_found': len(regions),
                'regions': regions,
                'heatmap_path': heatmap_path,
                'analysis_summary': ELAAnalyzer.generate_summary(regions, overall_confidence)
            }
            
            return results
            
        except Exception as e:
            print(f"ELA Analysis Error: {e}")
            return {
                'overall_confidence': 0,
                'suspicious_ratio': 0,
                'regions_found': 0,
                'regions': [],
                'heatmap_path': None,
                'analysis_summary': f"Analysis failed: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def generate_heatmap(original_image, diff_image, regions):
        """
        Generate a heatmap visualization
        
        Args:
            original_image: Original image (numpy array)
            diff_image: Difference image (numpy array)
            regions: List of suspicious regions
            
        Returns:
            str: Path to saved heatmap image
        """
        try:
            # Create heatmap by applying colormap to diff image
            heatmap = cv2.applyColorMap(diff_image, cv2.COLORMAP_JET)
            
            # Blend with original image
            alpha = 0.5
            blended = cv2.addWeighted(original_image, 1-alpha, heatmap, alpha, 0)
            
            # Draw bounding boxes around suspicious regions
            for region in regions:
                x, y, w, h = region['bbox']
                confidence = region['confidence']
                
                # Determine color based on confidence
                if confidence >= 70:
                    color = (0, 0, 255)  # Red
                    thickness = 3
                elif confidence >= 40:
                    color = (0, 165, 255)  # Orange
                    thickness = 2
                else:
                    color = (0, 255, 255)  # Yellow
                    thickness = 1
                
                # Draw rectangle
                cv2.rectangle(blended, (x, y), (x+w, y+h), color, thickness)
                
                # Add confidence label
                label = f"{confidence:.0f}%"
                font_scale = max(0.5, min(1.0, w / 200))
                cv2.putText(blended, label, (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 2)
            
            # Save heatmap
            heatmap_dir = os.path.join(Config.UPLOAD_FOLDER, "heatmaps")
            os.makedirs(heatmap_dir, exist_ok=True)
            
            heatmap_filename = f"ela_heatmap_{os.path.basename(tempfile.mktemp())}.png"
            heatmap_path = os.path.join(heatmap_dir, heatmap_filename)
            
            cv2.imwrite(heatmap_path, blended)
            
            return heatmap_path
            
        except Exception as e:
            print(f"Heatmap generation error: {e}")
            return None
    
    @staticmethod
    def generate_summary(regions, overall_confidence):
        """Generate human-readable summary of ELA findings"""
        
        if not regions:
            if overall_confidence < 20:
                return "No significant tampering detected. Document appears authentic."
            else:
                return "Low confidence findings. Document likely authentic with minor compression artifacts."
        
        # Count regions by confidence level
        high_conf = sum(1 for r in regions if r['confidence'] >= 70)
        medium_conf = sum(1 for r in regions if 40 <= r['confidence'] < 70)
        low_conf = sum(1 for r in regions if r['confidence'] < 40)
        
        # Generate summary based on findings
        if high_conf >= 2:
            return f"High confidence tampering detected in {high_conf} regions. Document shows clear signs of manipulation."
        elif high_conf == 1 and medium_conf >= 1:
            return f"Suspicious editing detected. {high_conf} high confidence and {medium_conf} medium confidence regions found."
        elif medium_conf >= 2:
            return f"Multiple suspicious regions detected ({medium_conf} regions). Document may have been altered."
        elif low_conf >= 3:
            return f"Minor anomalies detected in {len(regions)} regions. Could be compression artifacts or minor edits."
        else:
            return f"{len(regions)} potential tampering regions detected. Further verification recommended."
    
    @staticmethod
    def batch_analyze(image_paths):
        """
        Analyze multiple images
        
        Args:
            image_paths: List of image paths
            
        Returns:
            dict: Results for each image
        """
        results = {}
        for path in image_paths:
            if os.path.exists(path):
                results[path] = ELAAnalyzer.analyze(path)
        
        return results
    
    @staticmethod
    def test_with_sample():
        """Test ELA with a sample image (for debugging)"""
        # Create a simple test image
        test_image = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        # Add a "tampered" region
        cv2.rectangle(test_image, (200, 150), (400, 250), (200, 200, 200), -1)
        
        # Save test image
        test_path = os.path.join(Config.TEMP_DIR, "test_ela.jpg")
        cv2.imwrite(test_path, test_image)
        
        # Analyze
        results = ELAAnalyzer.analyze(test_path)
        
        # Cleanup
        os.remove(test_path)
        
        return results
