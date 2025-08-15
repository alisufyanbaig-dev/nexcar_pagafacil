"""
Captcha solver module using OCR for Paga Fácil website.
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import requests
import logging
from typing import Optional, Tuple
import re

logger = logging.getLogger(__name__)

class CaptchaSolver:
    """OCR-based captcha solver for simple text captchas."""
    
    def __init__(self):
        """Initialize the captcha solver with optimal OCR settings."""
        # Tesseract configuration for alphanumeric captchas
        self.tesseract_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
    def download_captcha_image(self, session: requests.Session, captcha_url: str) -> Optional[bytes]:
        """
        Download captcha image from the website.
        
        Args:
            session: Requests session with proxy configuration
            captcha_url: URL of the captcha image
            
        Returns:
            Raw image bytes or None if failed
        """
        try:
            logger.info(f"Downloading captcha from: {captcha_url}")
            response = session.get(captcha_url, timeout=15)
            response.raise_for_status()
            
            if len(response.content) < 100:  # Too small to be a valid image
                logger.warning("Captcha image too small, might be invalid")
                return None
                
            return response.content
            
        except Exception as e:
            logger.error(f"Error downloading captcha: {str(e)}")
            return None
    
    def preprocess_image(self, image_bytes: bytes) -> list:
        """
        Preprocess the captcha image to improve OCR accuracy.
        Returns multiple processed versions for better success rate.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            List of processed images as numpy arrays
        """
        try:
            # Convert bytes to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Resize image if too small (OCR works better on larger images)
            width, height = pil_image.size
            scale_factor = max(200/width, 80/height, 3.0)  # Increased scaling
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.info(f"Resized captcha from {width}x{height} to {new_width}x{new_height}")
            
            processed_images = []
            
            # Version 1: Standard processing
            enhanced_image = pil_image.copy()
            enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = enhancer.enhance(1.8)
            enhancer = ImageEnhance.Sharpness(enhanced_image)
            enhanced_image = enhancer.enhance(2.5)
            
            opencv_image = cv2.cvtColor(np.array(enhanced_image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Try different thresholding methods
            _, binary1 = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(binary1)
            
            # Version 2: Adaptive threshold
            binary2 = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
            processed_images.append(binary2)
            
            # Version 3: Different contrast and brightness
            enhanced_image2 = pil_image.copy()
            enhancer = ImageEnhance.Contrast(enhanced_image2)
            enhanced_image2 = enhancer.enhance(2.5)
            enhancer = ImageEnhance.Brightness(enhanced_image2)
            enhanced_image2 = enhancer.enhance(1.2)
            
            opencv_image2 = cv2.cvtColor(np.array(enhanced_image2), cv2.COLOR_RGB2BGR)
            gray2 = cv2.cvtColor(opencv_image2, cv2.COLOR_BGR2GRAY)
            denoised2 = cv2.medianBlur(gray2, 3)
            _, binary3 = cv2.threshold(denoised2, 127, 255, cv2.THRESH_BINARY)
            processed_images.append(binary3)
            
            # Version 4: Morphological operations
            kernel = np.ones((2,2), np.uint8)
            cleaned = cv2.morphologyEx(binary1, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            processed_images.append(cleaned)
            
            # Version 5: Inverted image (sometimes helps)
            inverted = cv2.bitwise_not(binary1)
            processed_images.append(inverted)
            
            logger.info(f"Generated {len(processed_images)} processed image versions")
            return processed_images
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return []
    
    def extract_text_ocr(self, processed_images: list) -> Optional[str]:
        """
        Extract text from multiple preprocessed images using OCR.
        
        Args:
            processed_images: List of preprocessed images as numpy arrays
            
        Returns:
            Extracted text or None if failed
        """
        try:
            # Try different OCR configurations
            configs = [
                r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                r'--oem 3 --psm 13 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                r'--oem 3 --psm 8',
                r'--oem 3 --psm 7',
            ]
            
            best_result = ""
            best_confidence = 0
            results_count = {}
            
            # Try each processed image with each config
            for img_idx, processed_image in enumerate(processed_images):
                pil_image = Image.fromarray(processed_image)
                
                for config_idx, config in enumerate(configs):
                    try:
                        # Extract text
                        text = pytesseract.image_to_string(pil_image, config=config).strip()
                        
                        # Get confidence
                        data = pytesseract.image_to_data(pil_image, config=config, output_type=pytesseract.Output.DICT)
                        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                        
                        # Clean up text
                        cleaned_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                        
                        if len(cleaned_text) >= 3:
                            # Count occurrences of this result
                            results_count[cleaned_text] = results_count.get(cleaned_text, 0) + 1
                            
                            logger.info(f"OCR result (img {img_idx}, cfg {config_idx}): '{cleaned_text}' (confidence: {avg_confidence:.1f}%)")
                            
                            # Track best result by confidence
                            if avg_confidence > best_confidence:
                                best_result = cleaned_text
                                best_confidence = avg_confidence
                                
                    except Exception as e:
                        continue
            
            # If we have multiple results, prefer the most common one
            if results_count:
                most_common = max(results_count.items(), key=lambda x: x[1])
                most_common_text, count = most_common
                
                # If a result appears multiple times and has reasonable length, prefer it
                if count >= 2 and len(most_common_text) >= 3:
                    logger.info(f"Using most common result: '{most_common_text}' (appeared {count} times)")
                    return most_common_text
                elif best_result and len(best_result) >= 3 and best_confidence > 10:
                    logger.info(f"Using best confidence result: '{best_result}' (confidence: {best_confidence:.1f}%)")
                    return best_result
                elif most_common_text and len(most_common_text) >= 3:
                    logger.info(f"Using most common result: '{most_common_text}' (appeared {count} times)")
                    return most_common_text
                elif best_result and len(best_result) >= 3:
                    logger.info(f"Using best result (low confidence): '{best_result}' (confidence: {best_confidence:.1f}%)")
                    return best_result
            
            logger.warning("No reliable OCR result found")
            return None
                
        except Exception as e:
            logger.error(f"Error in OCR extraction: {str(e)}")
            return None
    
    def solve_captcha(self, session: requests.Session, base_url: str, captcha_image_path: str) -> Optional[str]:
        """
        Complete captcha solving workflow.
        
        Args:
            session: Requests session with proxy configuration
            base_url: Base URL of the website
            captcha_image_path: Relative path to captcha image
            
        Returns:
            Solved captcha text or None if failed
        """
        try:
            # Construct full captcha URL
            if captcha_image_path.startswith('../../'):
                # Handle relative paths like ../../captcha/imagebuilder.php
                captcha_url = captcha_image_path.replace('../../', f"{base_url.rstrip('/')}/../../")
            else:
                captcha_url = f"{base_url.rstrip('/')}/{captcha_image_path.lstrip('/')}"
            
            # Handle specific case for pagafacil structure
            if 'captcha/imagebuilder.php' in captcha_image_path:
                captcha_url = 'https://www.pagafacil.gob.mx/pagafacilv2/captcha/imagebuilder.php'
            
            logger.info(f"Attempting to solve captcha from: {captcha_url}")
            
            # Download captcha image
            image_bytes = self.download_captcha_image(session, captcha_url)
            if not image_bytes:
                return None
            
            # Preprocess image (now returns multiple versions)
            processed_images = self.preprocess_image(image_bytes)
            if not processed_images:
                return None
            
            # Extract text using OCR
            captcha_text = self.extract_text_ocr(processed_images)
            
            if captcha_text:
                logger.info(f"Successfully solved captcha: '{captcha_text}'")
                return captcha_text
            else:
                logger.warning("Failed to solve captcha")
                return None
                
        except Exception as e:
            logger.error(f"Error solving captcha: {str(e)}")
            return None
    
    def save_debug_image(self, image_bytes: bytes, filename: str = "debug_captcha.png"):
        """
        Save captcha image for debugging purposes.
        
        Args:
            image_bytes: Raw image bytes
            filename: Output filename
        """
        try:
            with open(filename, 'wb') as f:
                f.write(image_bytes)
            logger.info(f"Debug image saved as: {filename}")
        except Exception as e:
            logger.error(f"Error saving debug image: {e}")
            
    def get_multiple_attempts(self, session: requests.Session, base_url: str, 
                            captcha_image_path: str, max_attempts: int = 3) -> Optional[str]:
        """
        Try to solve captcha with multiple attempts.
        
        Args:
            session: Requests session
            base_url: Base URL
            captcha_image_path: Path to captcha image
            max_attempts: Maximum number of attempts
            
        Returns:
            Solved captcha text or None
        """
        for attempt in range(max_attempts):
            logger.info(f"Captcha solving attempt {attempt + 1}/{max_attempts}")
            
            result = self.solve_captcha(session, base_url, captcha_image_path)
            if result and len(result) >= 3:  # More permissive length requirement
                return result
            
            # Small delay between attempts
            import time
            time.sleep(1)
        
        logger.warning(f"Failed to solve captcha after {max_attempts} attempts")
        return None