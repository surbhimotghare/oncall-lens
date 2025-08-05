"""
File Processor Service for Oncall Lens
Handles processing of different file types for incident analysis.
"""

import logging
import mimetypes
import os
from pathlib import Path
from typing import List, Dict, Any
import hashlib

from fastapi import UploadFile, HTTPException
import aiofiles

from models.api_models import ProcessedFile
from config.settings import get_settings

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    Service for processing uploaded incident files.
    Handles various file types: logs, diffs, stack traces, images, etc.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.max_file_size = self.settings.max_file_size  # Already in bytes
        self.supported_extensions = set(self.settings.allowed_file_types)
        
    async def process_files(self, files: List[UploadFile]) -> List[ProcessedFile]:
        """
        Process a list of uploaded files and extract their content.
        
        Args:
            files: List of uploaded files from FastAPI
            
        Returns:
            List of processed files with extracted content
        """
        processed_files = []
        
        for file in files:
            try:
                processed_file = await self._process_single_file(file)
                processed_files.append(processed_file)
                logger.info(f"✅ Processed file: {file.filename} ({processed_file.file_type})")
                
            except Exception as e:
                logger.error(f"❌ Failed to process file {file.filename}: {e}")
                # Continue processing other files, but note the failure
                processed_files.append(ProcessedFile(
                    filename=file.filename or "unknown",
                    file_type="error",
                    content=f"Failed to process: {str(e)}",
                    size_bytes=0,
                    processing_notes=f"Processing failed: {str(e)}"
                ))
                
        return processed_files
    
    async def _process_single_file(self, file: UploadFile) -> ProcessedFile:
        """
        Process a single uploaded file.
        
        Args:
            file: Single uploaded file
            
        Returns:
            ProcessedFile with extracted content
        """
        # Validate file
        await self._validate_file(file)
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Determine file type and process accordingly
        file_type = self._determine_file_type(file.filename, content)
        
        # Extract text content based on file type
        text_content = await self._extract_content(content, file_type, file.filename)
        
        return ProcessedFile(
            filename=file.filename or "unknown",
            file_type=file_type,
            content=text_content,
            size_bytes=file_size,
            processing_notes=f"Successfully processed as {file_type}"
        )
    
    async def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file (size, type, etc.)
        
        Args:
            file: File to validate
            
        Raises:
            HTTPException: If file is invalid
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.supported_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_ext}. Supported types: {self.supported_extensions}"
            )
        
        # Check file size (read first chunk to estimate)
        await file.seek(0)
        chunk = await file.read(1024)
        await file.seek(0)
        
        if not chunk:
            raise HTTPException(status_code=400, detail="File is empty")
    
    def _determine_file_type(self, filename: str, content: bytes) -> str:
        """
        Determine the type of file based on filename and content.
        
        Args:
            filename: Original filename
            content: File content bytes
            
        Returns:
            String representing the file type
        """
        filename_lower = filename.lower()
        file_ext = Path(filename).suffix.lower()
        
        # Check by filename patterns
        if any(pattern in filename_lower for pattern in ['stack', 'trace', 'exception']):
            return "stack_trace"
        elif any(pattern in filename_lower for pattern in ['.log', 'error', 'debug']):
            return "log_file"
        elif any(pattern in filename_lower for pattern in ['.diff', '.patch']):
            return "code_diff"
        elif 'postmortem' in filename_lower or 'incident' in filename_lower:
            return "postmortem"
        elif any(pattern in filename_lower for pattern in ['cpu', 'memory', 'metrics', 'dashboard']):
            return "metrics"
        
        # Check by file extension
        if file_ext in ['.log']:
            return "log_file"
        elif file_ext in ['.diff', '.patch']:
            return "code_diff"
        elif file_ext in ['.md', '.txt'] and len(content) > 1000:
            return "documentation"
        elif file_ext in ['.json']:
            return "configuration"
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            return "screenshot"
        elif file_ext in ['.csv']:
            return "metrics_data"
        else:
            return "text_file"
    
    async def _extract_content(self, content: bytes, file_type: str, filename: str) -> str:
        """
        Extract text content from file based on its type.
        
        Args:
            content: File content bytes
            file_type: Determined file type
            filename: Original filename
            
        Returns:
            Extracted text content
        """
        try:
            if file_type == "screenshot":
                return await self._process_image(content, filename)
            else:
                # Try to decode as text
                text_content = await self._decode_text(content)
                
                # Apply type-specific processing
                if file_type == "log_file":
                    return self._process_log_file(text_content)
                elif file_type == "stack_trace":
                    return self._process_stack_trace(text_content)
                elif file_type == "code_diff":
                    return self._process_code_diff(text_content)
                elif file_type == "configuration":
                    return self._process_json_config(text_content)
                else:
                    return text_content
                    
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract content from {filename}: {e}")
            return f"[Content extraction failed: {str(e)}]"
    
    async def _decode_text(self, content: bytes) -> str:
        """
        Decode bytes to text, trying multiple encodings.
        
        Args:
            content: Bytes to decode
            
        Returns:
            Decoded text string
        """
        encodings = ['utf-8', 'utf-16', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # If all fail, decode with errors ignored
        return content.decode('utf-8', errors='ignore')
    
    def _process_log_file(self, content: str) -> str:
        """
        Process log file content to highlight important information.
        
        Args:
            content: Raw log content
            
        Returns:
            Processed log content with annotations
        """
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            line_lower = line.lower()
            # Mark important lines
            if any(keyword in line_lower for keyword in ['error', 'exception', 'failed', 'timeout']):
                processed_lines.append(f"🔴 ERROR: {line}")
            elif any(keyword in line_lower for keyword in ['warn', 'warning']):
                processed_lines.append(f"🟡 WARN: {line}")
            elif any(keyword in line_lower for keyword in ['info', 'start', 'stop', 'success']):
                processed_lines.append(f"ℹ️ INFO: {line}")
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _process_stack_trace(self, content: str) -> str:
        """
        Process stack trace content to highlight the exception and key frames.
        
        Args:
            content: Raw stack trace content
            
        Returns:
            Processed stack trace with annotations
        """
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            if line.strip().startswith('Exception') or line.strip().startswith('Error'):
                processed_lines.append(f"💥 EXCEPTION: {line}")
            elif 'at ' in line and any(keyword in line for keyword in ['java.', 'com.', 'org.']):
                processed_lines.append(f"📍 FRAME: {line}")
            elif 'Caused by:' in line:
                processed_lines.append(f"🔗 CAUSE: {line}")
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _process_code_diff(self, content: str) -> str:
        """
        Process code diff to highlight changes.
        
        Args:
            content: Raw diff content
            
        Returns:
            Processed diff with annotations
        """
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                processed_lines.append(f"➕ ADDED: {line}")
            elif line.startswith('-') and not line.startswith('---'):
                processed_lines.append(f"➖ REMOVED: {line}")
            elif line.startswith('@@'):
                processed_lines.append(f"📍 LOCATION: {line}")
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _process_json_config(self, content: str) -> str:
        """
        Process JSON configuration files.
        
        Args:
            content: Raw JSON content
            
        Returns:
            Processed JSON with validation
        """
        try:
            import json
            parsed = json.loads(content)
            # Return pretty-printed JSON
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError as e:
            return f"⚠️ INVALID JSON: {content}\n\nError: {str(e)}"
    
    async def _process_image(self, content: bytes, filename: str) -> str:
        """
        Process image files (placeholder for OCR functionality).
        
        Args:
            content: Image bytes
            filename: Original filename
            
        Returns:
            Description of the image (placeholder)
        """
        # Placeholder for image processing
        # In a real implementation, you might use OCR libraries like pytesseract
        # or send to GPT-4 Vision API for analysis
        
        image_hash = hashlib.md5(content).hexdigest()[:8]
        
        return f"""
📸 IMAGE FILE: {filename}
🔍 Size: {len(content)} bytes
🆔 Hash: {image_hash}

📋 CONTENT DESCRIPTION:
This appears to be a screenshot or image file related to the incident.
For full analysis, this image would need to be processed with OCR or 
vision AI capabilities.

🔧 PROCESSING NOTE:
Image content extraction is not yet implemented. Consider:
- Using OCR to extract text from screenshots
- Using GPT-4 Vision API to analyze dashboard screenshots
- Converting charts/graphs to textual descriptions
""" 