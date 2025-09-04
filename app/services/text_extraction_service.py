"""
Text extraction service for various document types
"""

import os
from typing import Optional
import PyPDF2
import docx
from PIL import Image
import pytesseract
import aiofiles

class TextExtractionService:
    """Service for extracting text from various document types"""
    
    def __init__(self):
        # Configure Tesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    async def extract_text(self, file_path: str) -> str:
        """Extract text from a document file"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return await self._extract_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return await self._extract_from_docx(file_path)
            elif file_extension == '.txt':
                return await self._extract_from_txt(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                return await self._extract_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return f"Error extracting text: {str(e)}"
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {e}")
    
    async def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                return await file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as file:
                    return await file.read()
            except Exception as e:
                raise Exception(f"Error reading TXT file: {e}")
        except Exception as e:
            raise Exception(f"Error reading TXT file: {e}")
    
    async def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Open image
            image = Image.open(file_path)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from image: {e}")
    
    def get_supported_formats(self) -> list:
        """Get list of supported file formats"""
        return [
            '.pdf', '.docx', '.doc', '.txt',
            '.jpg', '.jpeg', '.png', '.tiff', '.bmp'
        ]
