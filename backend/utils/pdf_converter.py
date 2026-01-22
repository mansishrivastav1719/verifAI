"""
PDF to image conversion utilities
"""

import os
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import tempfile
from config import Config

class PDFConverter:
    """Convert PDF documents to images for processing"""
    
    @staticmethod
    def pdf_to_images(file_path, output_dir=None):
        """
        Convert PDF to list of images (PIL Image objects)
        
        Args:
            file_path: Path to PDF file
            output_dir: Directory to save images (optional)
            
        Returns:
            list: List of PIL Image objects
            list: List of saved image paths (if output_dir provided)
        """
        try:
            # Convert PDF to images
            images = convert_from_path(
                file_path,
                dpi=200,  # Good balance of quality vs size
                grayscale=False,  # Keep color for better analysis
                fmt='png',
                thread_count=2  # Use multiple threads for faster conversion
            )
            
            saved_paths = []
            
            # Save images if output directory provided
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                
                for i, img in enumerate(images):
                    # Only process first 5 pages (for performance)
                    if i >= 5:
                        break
                    
                    img_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.png")
                    img.save(img_path, 'PNG', optimize=True)
                    saved_paths.append(img_path)
            
            return images, saved_paths
            
        except Exception as e:
            print(f"Error converting PDF: {e}")
            return [], []
    
    @staticmethod
    def is_pdf(file_path):
        """Check if file is a PDF"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'
        except:
            return False
    
    @staticmethod
    def convert_to_png(image_path, output_path=None):
        """
        Convert any image to PNG format if needed
        
        Args:
            image_path: Path to image file
            output_path: Output path for PNG (optional)
            
        Returns:
            str: Path to PNG file
        """
        try:
            img = Image.open(image_path)
            
            # If already PNG and no output path specified, return original
            if img.format == 'PNG' and not output_path:
                return image_path
            
            # Generate output path if not provided
            if not output_path:
                base_name = os.path.splitext(image_path)[0]
                output_path = f"{base_name}.png"
            
            # Convert to RGB if necessary (for JPEG with transparency)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else img)
                img = background
            
            # Save as PNG
            img.save(output_path, 'PNG', optimize=True)
            
            return output_path
            
        except Exception as e:
            print(f"Error converting to PNG: {e}")
            return image_path  # Return original if conversion fails
    
    @staticmethod
    def extract_first_page(file_path, output_path=None):
        """
        Extract and return only the first page of PDF as image
        
        Args:
            file_path: Path to PDF file
            output_path: Output path for image (optional)
            
        Returns:
            PIL.Image: First page as PIL Image
            str: Path to saved image
        """
        try:
            images, saved_paths = PDFConverter.pdf_to_images(file_path, tempfile.gettempdir())
            
            if not images:
                return None, None
            
            first_image = images[0]
            
            # Save if output path provided
            if output_path:
                first_image.save(output_path, 'PNG', optimize=True)
                return first_image, output_path
            
            return first_image, saved_paths[0] if saved_paths else None
            
        except Exception as e:
            print(f"Error extracting first page: {e}")
            return None, None
