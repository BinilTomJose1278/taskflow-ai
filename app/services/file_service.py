"""
File service for handling file operations
"""

import os
import aiofiles
from pathlib import Path
from typing import Optional
import uuid
from datetime import datetime

from app.core.config import settings

class FileService:
    """Service for file operations"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file, file_content: bytes) -> str:
        """Save uploaded file to disk"""
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create date-based subdirectory
        date_dir = datetime.now().strftime("%Y/%m/%d")
        file_dir = self.upload_dir / date_dir
        file_dir.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = file_dir / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return str(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from disk"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "exists": True
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None
    
    def ensure_directory_exists(self, directory_path: str) -> bool:
        """Ensure directory exists"""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {directory_path}: {e}")
            return False
