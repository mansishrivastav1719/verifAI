"""
Metadata Analyzer for document forensics
Detects anomalies in EXIF data, file structure, and digital signatures
"""

import os
import datetime
from PIL import Image, ImageFile
from PIL.ExifTags import TAGS, GPSTAGS
import pdfplumber
import magic
import hashlib
from pathlib import Path
from config import Config

class MetadataAnalyzer:
    """Analyze document metadata for tampering evidence"""
    
    @staticmethod
    def analyze(file_path):
        """
        Analyze metadata for potential tampering
        
        Args:
            file_path: Path to the document file
            
        Returns:
            dict: Analysis results including metadata anomalies
        """
        try:
            # Get basic file information
            file_info = MetadataAnalyzer.get_basic_file_info(file_path)
            
            # Initialize results
            results = {
                'file_info': file_info,
                'anomalies': [],
                'metadata_extracted': {},
                'overall_confidence': 0
            }
            
            # Determine file type and analyze accordingly
            mime_type = MetadataAnalyzer.get_mime_type(file_path)
            file_info['mime_type'] = mime_type
            
            if mime_type.startswith('image/'):
                image_results = MetadataAnalyzer.analyze_image_metadata(file_path)
                results.update(image_results)
            elif mime_type == 'application/pdf':
                pdf_results = MetadataAnalyzer.analyze_pdf_metadata(file_path)
                results.update(pdf_results)
            else:
                # Generic file analysis
                results['analysis_summary'] = "Unsupported file type for detailed metadata analysis"
                results['overall_confidence'] = 0
            
            # Perform cross-type analysis
            cross_analysis = MetadataAnalyzer.cross_type_analysis(file_path, mime_type)
            results['anomalies'].extend(cross_analysis.get('anomalies', []))
            
            # Calculate overall confidence
            results['overall_confidence'] = MetadataAnalyzer.calculate_confidence(
                results.get('anomalies', []),
                results.get('metadata_extracted', {})
            )
            
            # Generate summary
            results['analysis_summary'] = MetadataAnalyzer.generate_summary(
                results.get('anomalies', []),
                results['overall_confidence']
            )
            
            # Add file hash for verification
            results['file_hash'] = MetadataAnalyzer.calculate_file_hash(file_path)
            
            return results
            
        except Exception as e:
            print(f"Metadata Analysis Error: {e}")
            return {
                'file_info': {'path': file_path, 'error': str(e)},
                'anomalies': [],
                'metadata_extracted': {},
                'overall_confidence': 0,
                'analysis_summary': f"Metadata analysis failed: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def get_basic_file_info(file_path):
        """Extract basic file information"""
        try:
            stat_info = os.stat(file_path)
            
            return {
                'filename': os.path.basename(file_path),
                'file_size': stat_info.st_size,
                'created': datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified': datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'accessed': datetime.datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                'file_extension': Path(file_path).suffix.lower(),
                'absolute_path': os.path.abspath(file_path)
            }
        except Exception as e:
            return {'error': f"Failed to get file info: {str(e)}"}
    
    @staticmethod
    def get_mime_type(file_path):
        """Get MIME type using python-magic"""
        try:
            mime = magic.Magic(mime=True)
            return mime.from_file(file_path)
        except:
            # Fallback to file extension
            ext = Path(file_path).suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                return 'image/jpeg'
            elif ext == '.png':
                return 'image/png'
            elif ext == '.pdf':
                return 'application/pdf'
            else:
                return 'application/octet-stream'
    
    @staticmethod
    def analyze_image_metadata(file_path):
        """Analyze image metadata (EXIF)"""
        try:
            # Open image with PIL
            image = Image.open(file_path)
            
            # Extract EXIF data
            exif_data = {}
            if hasattr(image, '_getexif') and image._getexif():
                for tag_id, value in image._getexif().items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Handle special cases
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)[:100]  # Truncate if too long
                    
                    exif_data[tag] = value
            
            # Extract additional image info
            image_info = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height,
                'palette': image.palette.mode if image.palette else None,
                'info': dict(image.info) if image.info else {}
            }
            
            # Analyze for anomalies
            anomalies = MetadataAnalyzer.analyze_image_anomalies(exif_data, image_info, file_path)
            
            return {
                'metadata_extracted': {
                    'exif': exif_data,
                    'image_info': image_info
                },
                'anomalies': anomalies,
                'file_type': 'image'
            }
            
        except Exception as e:
            return {
                'metadata_extracted': {'error': str(e)},
                'anomalies': [{'type': 'analysis_error', 'description': f"Image analysis failed: {str(e)}"}],
                'file_type': 'image'
            }
    
    @staticmethod
    def analyze_pdf_metadata(file_path):
        """Analyze PDF metadata"""
        try:
            metadata = {}
            anomalies = []
            
            with pdfplumber.open(file_path) as pdf:
                # Extract basic PDF info
                metadata['page_count'] = len(pdf.pages)
                metadata['pdf_version'] = pdf.metadata.get('Producer', 'Unknown')
                
                # Extract document info
                doc_info = {}
                if hasattr(pdf, 'doc') and pdf.doc.info:
                    for key, value in pdf.doc.info:
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except:
                                value = str(value)
                        doc_info[key] = value
                
                metadata['document_info'] = doc_info
                
                # Check for anomalies
                anomalies.extend(MetadataAnalyzer.analyze_pdf_anomalies(pdf, file_path))
            
            return {
                'metadata_extracted': metadata,
                'anomalies': anomalies,
                'file_type': 'pdf'
            }
            
        except Exception as e:
            return {
                'metadata_extracted': {'error': str(e)},
                'anomalies': [{'type': 'analysis_error', 'description': f"PDF analysis failed: {str(e)}"}],
                'file_type': 'pdf'
            }
    
    @staticmethod
    def analyze_image_anomalies(exif_data, image_info, file_path):
        """Detect anomalies in image metadata"""
        anomalies = []
        
        # 1. Check for missing EXIF data (common in edited images)
        essential_tags = ['DateTime', 'Make', 'Model', 'Software']
        missing_tags = [tag for tag in essential_tags if tag not in exif_data]
        
        if missing_tags and len(missing_tags) >= 2:
            anomalies.append({
                'type': 'missing_exif',
                'confidence': 60,
                'description': f"Missing essential EXIF tags: {', '.join(missing_tags)}",
                'details': {'missing_tags': missing_tags}
            })
        
        # 2. Check DateTime vs file system dates
        if 'DateTime' in exif_data:
            try:
                # Parse EXIF datetime
                exif_date_str = exif_data['DateTime']
                # Handle different datetime formats
                if ' ' in exif_date_str:
                    exif_date = datetime.datetime.strptime(exif_date_str, '%Y:%m:%d %H:%M:%S')
                    
                    # Get file modification time
                    file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Check if EXIF date is after file modification (impossible)
                    if exif_date > file_mtime:
                        anomalies.append({
                            'type': 'date_anomaly',
                            'confidence': 85,
                            'description': f"EXIF DateTime ({exif_date}) is after file modification time ({file_mtime})",
                            'details': {
                                'exif_date': exif_date.isoformat(),
                                'file_mtime': file_mtime.isoformat(),
                                'difference_hours': (exif_date - file_mtime).total_seconds() / 3600
                            }
                        })
            except (ValueError, TypeError) as e:
                # Date parsing error - could indicate tampered EXIF
                anomalies.append({
                    'type': 'date_format_error',
                    'confidence': 50,
                    'description': f"Invalid or tampered EXIF DateTime format: {exif_data['DateTime']}",
                    'details': {'error': str(e)}
                })
        
        # 3. Check for editing software signatures
        if 'Software' in exif_data:
            software = exif_data['Software'].lower()
            editing_software = ['photoshop', 'gimp', 'paint', 'editor', 'adobe']
            
            if any(editor in software for editor in editing_software):
                anomalies.append({
                    'type': 'editing_software',
                    'confidence': 70,
                    'description': f"Document created/edited with: {exif_data['Software']}",
                    'details': {'software': exif_data['Software']}
                })
        
        # 4. Check for GPS data in unexpected documents
        gps_tags = [tag for tag in exif_data.keys() if 'gps' in str(tag).lower()]
        if gps_tags and not any(keyword in file_path.lower() for keyword in ['map', 'location', 'geo']):
            anomalies.append({
                'type': 'unexpected_gps',
                'confidence': 55,
                'description': "GPS data found in non-geographic document",
                'details': {'gps_tags_found': gps_tags}
            })
        
        # 5. Check image dimensions vs file size
        file_size = os.path.getsize(file_path)
        width, height = image_info.get('size', (0, 0))
        
        if width > 0 and height > 0:
            pixel_count = width * height
            bytes_per_pixel = file_size / pixel_count if pixel_count > 0 else 0
            
            # Unusual compression ratio
            if bytes_per_pixel < 0.1:  # Very compressed
                anomalies.append({
                    'type': 'compression_anomaly',
                    'confidence': 65,
                    'description': f"Unusually high compression ({(bytes_per_pixel):.4f} bytes/pixel)",
                    'details': {
                        'file_size_bytes': file_size,
                        'dimensions': f"{width}x{height}",
                        'bytes_per_pixel': bytes_per_pixel
                    }
                })
        
        return anomalies
    
    @staticmethod
    def analyze_pdf_anomalies(pdf, file_path):
        """Detect anomalies in PDF metadata"""
        anomalies = []
        
        try:
            # 1. Check for modified dates
            if hasattr(pdf, 'doc') and pdf.doc.info:
                info = dict(pdf.doc.info)
                
                creation_date = info.get('CreationDate')
                mod_date = info.get('ModDate')
                
                if creation_date and mod_date:
                    # Parse PDF dates (format: D:YYYYMMDDHHmmSS)
                    if creation_date != mod_date:
                        anomalies.append({
                            'type': 'pdf_modified',
                            'confidence': 75,
                            'description': "PDF has been modified since creation",
                            'details': {
                                'creation_date': creation_date,
                                'modification_date': mod_date
                            }
                        })
            
            # 2. Check for form fields (could indicate editable document)
            form_fields = []
            for page in pdf.pages:
                if page.annots:
                    for annot in page.annots:
                        if annot and '/FT' in annot:
                            form_fields.append(annot.get('/FT', 'Unknown'))
            
            if form_fields:
                anomalies.append({
                    'type': 'form_fields',
                    'confidence': 60,
                    'description': f"PDF contains {len(form_fields)} form field(s) - could be editable",
                    'details': {'field_types': list(set(form_fields))}
                })
            
            # 3. Check page consistency
            page_sizes = []
            for i, page in enumerate(pdf.pages):
                page_sizes.append({
                    'page': i + 1,
                    'width': page.width,
                    'height': page.height
                })
            
            # Check if all pages have same size
            if len(page_sizes) > 1:
                first_size = (page_sizes[0]['width'], page_sizes[0]['height'])
                inconsistent_pages = []
                
                for page_info in page_sizes[1:]:
                    if (page_info['width'], page_info['height']) != first_size:
                        inconsistent_pages.append(page_info['page'])
                
                if inconsistent_pages:
                    anomalies.append({
                        'type': 'inconsistent_page_sizes',
                        'confidence': 70,
                        'description': f"Inconsistent page sizes on pages: {inconsistent_pages}",
                        'details': {
                            'expected_size': first_size,
                            'inconsistent_pages': inconsistent_pages,
                            'all_page_sizes': page_sizes
                        }
                    })
        
        except Exception as e:
            anomalies.append({
                'type': 'pdf_analysis_error',
                'confidence': 30,
                'description': f"PDF anomaly detection failed: {str(e)}"
            })
        
        return anomalies
    
    @staticmethod
    def cross_type_analysis(file_path, mime_type):
        """Perform cross-type metadata analysis"""
        anomalies = []
        
        try:
            # Check file extension vs actual MIME type
            ext = Path(file_path).suffix.lower()
            expected_mime_for_ext = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.pdf': 'application/pdf'
            }
            
            expected_mime = expected_mime_for_ext.get(ext)
            if expected_mime and mime_type != expected_mime:
                anomalies.append({
                    'type': 'mime_mismatch',
                    'confidence': 80,
                    'description': f"File extension ({ext}) doesn't match actual type ({mime_type})",
                    'details': {
                        'extension': ext,
                        'expected_mime': expected_mime,
                        'actual_mime': mime_type
                    }
                })
            
            # Check file size vs type expectations
            file_size = os.path.getsize(file_path)
            
            if mime_type.startswith('image/'):
                # Images should have reasonable size for their dimensions
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        expected_min_size = width * height * 0.1  # Rough estimate
                        
                        if file_size < expected_min_size * 0.1:  # Too small
                            anomalies.append({
                                'type': 'suspicious_file_size',
                                'confidence': 65,
                                'description': f"Image file size ({file_size:,} bytes) suspiciously small for {width}x{height} resolution",
                                'details': {
                                    'file_size': file_size,
                                    'dimensions': f"{width}x{height}",
                                    'expected_min_size': int(expected_min_size)
                                }
                            })
                except:
                    pass
            
        except Exception as e:
            anomalies.append({
                'type': 'cross_analysis_error',
                'confidence': 20,
                'description': f"Cross-type analysis failed: {str(e)}"
            })
        
        return {'anomalies': anomalies}
    
    @staticmethod
    def calculate_confidence(anomalies, metadata):
        """
        Calculate overall confidence based on metadata anomalies
        
        Args:
            anomalies: List of anomaly dictionaries
            metadata: Extracted metadata
            
        Returns:
            float: Confidence score (0-100)
        """
        if not anomalies:
            # No anomalies found
            if metadata and len(metadata) > 0:
                # Rich metadata suggests authentic document
                return max(0, 100 - (len(metadata) * 0.5))
            else:
                # No metadata could mean stripped/edited
                return 50
        
        # Calculate based on anomaly severity and count
        total_score = 0
        weight_sum = 0
        
        for anomaly in anomalies:
            confidence = anomaly.get('confidence', 50)
            anomaly_type = anomaly.get('type', '')
            
            # Weight different anomaly types
            weight = 1.0
            if 'date' in anomaly_type:
                weight = 1.5  # Date anomalies are more serious
            elif 'mime' in anomaly_type:
                weight = 1.3  # MIME mismatches are suspicious
            
            total_score += confidence * weight
            weight_sum += weight
        
        if weight_sum > 0:
            avg_score = total_score / weight_sum
        else:
            avg_score = 0
        
        # Adjust based on number of anomalies
        anomaly_count_factor = min(1.0, len(anomalies) / 5)  # Cap at 5 anomalies
        final_score = avg_score * (0.7 + 0.3 * anomaly_count_factor)
        
        return min(100, max(0, final_score))
    
    @staticmethod
    def generate_summary(anomalies, overall_confidence):
        """Generate human-readable summary of metadata findings"""
        
        if not anomalies:
            if overall_confidence < 30:
                return "No metadata anomalies detected. Document metadata appears authentic."
            else:
                return "Limited metadata available. Document may have been stripped of metadata."
        
        # Count anomaly types
        anomaly_types = defaultdict(int)
        for anomaly in anomalies:
            anomaly_types[anomaly.get('type', 'unknown')] += 1
        
        # Generate summary based on findings
        total_anomalies = len(anomalies)
        
        if total_anomalies >= 3:
            return f"Multiple metadata anomalies detected ({total_anomalies} issues). Strong evidence of document tampering."
        elif total_anomalies == 2:
            types = list(anomaly_types.keys())
            return f"Two metadata anomalies detected ({', '.join(types)}). Document likely manipulated."
        elif total_anomalies == 1:
            anomaly_type = list(anomaly_types.keys())[0]
            if 'date' in anomaly_type:
                return "Date anomaly detected. Document creation/modification times inconsistent."
            elif 'mime' in anomaly_type:
                return "File type mismatch detected. Actual file type doesn't match extension."
            elif 'software' in anomaly_type:
                return "Editing software signature detected. Document was created/edited with image software."
            else:
                return "Metadata anomaly detected. Document may have been altered."
        else:
            return f"{total_anomalies} metadata issues found."
    
    @staticmethod
    def calculate_file_hash(file_path, algorithm='sha256'):
        """Calculate file hash for verification"""
        try:
            hash_func = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            
            return {
                'algorithm': algorithm,
                'hash': hash_func.hexdigest()
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def test_with_sample():
        """Test metadata analyzer with a sample file"""
        import tempfile
        
        # Create a simple test image
        from PIL import Image
        test_image = Image.new('RGB', (100, 100), color='white')
        
        # Save with some metadata
        test_path = tempfile.mktemp(suffix='_test_metadata.jpg')
        test_image.save(test_path, 'JPEG', 
                       quality=95,
                       exif=Image.Exif())
        
        # Analyze
        results = MetadataAnalyzer.analyze(test_path)
        
        # Cleanup
        import os
        os.remove(test_path)
        
        return results
