#!/usr/bin/env python3
"""
🔧 Binary File Handler - Universal File Processing
Handles various file types with metadata extraction, content analysis, and GPU-powered insights

Supported Types:
- Text files (TXT, MD, CSV, JSON, XML, etc.)
- Office documents (DOCX, XLSX, PPTX, PDF)
- Images (PNG, JPG, GIF, etc.)
- Audio/Video files
- Binary executables and data files
"""

import asyncio
import aiofiles
import logging
import mimetypes
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import time
from datetime import datetime
import os
import struct
import tempfile
import subprocess

# Set up logger first
logger = logging.getLogger(__name__)

# Try to import magic library with fallback
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not available, using basic file type detection")

class FileCategory(Enum):
    """Categories of files we can process"""
    TEXT = "text"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"
    BINARY = "binary"
    UNKNOWN = "unknown"

@dataclass
class FileMetadata:
    """Metadata extracted from a file"""
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_category: FileCategory
    encoding: str = None
    language: str = None
    
    # Content metadata
    line_count: int = 0
    word_count: int = 0
    char_count: int = 0
    
    # Technical metadata
    file_hash: str = None
    created_at: datetime = None
    modified_at: datetime = None
    
    # Extracted content
    text_content: str = None
    structured_data: Dict[str, Any] = None
    
    # Analysis results
    content_summary: str = None
    extracted_entities: List[str] = None
    confidence_score: float = 0.0
    
    # Processing metadata
    processing_time: float = 0.0
    error_message: str = None

    def __post_init__(self):
        if self.extracted_entities is None:
            self.extracted_entities = []
        if self.structured_data is None:
            self.structured_data = {}

@dataclass
class ProcessingResult:
    """Result of file processing"""
    success: bool
    metadata: FileMetadata
    extracted_files: List[str] = None  # For archives
    processing_notes: List[str] = None
    error_message: str = None

    def __post_init__(self):
        if self.extracted_files is None:
            self.extracted_files = []
        if self.processing_notes is None:
            self.processing_notes = []

class BinaryFileHandler:
    """Universal file handler for processing various file types"""
    
    def __init__(self):
        """Initialize the file handler"""
        self.max_text_size = 50 * 1024 * 1024  # 50MB for text extraction
        self.max_content_length = 1000000  # 1M chars for content analysis
        
        # File type mappings
        self.text_extensions = {
            '.txt', '.md', '.rst', '.log', '.csv', '.tsv', '.json', '.xml', '.yaml', '.yml',
            '.ini', '.cfg', '.conf', '.properties', '.sql', '.html', '.htm', '.css'
        }
        
        self.code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go',
            '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.sh', '.ps1', '.bat'
        }
        
        self.document_extensions = {
            '.docx', '.doc', '.odt', '.rtf'
        }
        
        self.spreadsheet_extensions = {
            '.xlsx', '.xls', '.ods', '.csv'
        }
        
        self.presentation_extensions = {
            '.pptx', '.ppt', '.odp'
        }
        
        logger.info("🔧 Binary File Handler initialized")

    async def process_file(self, file_path: Path, extract_content: bool = True, 
                          analyze_content: bool = False) -> ProcessingResult:
        """Process a file and extract metadata and content"""
        start_time = time.time()
        
        try:
            # Basic file information
            file_stat = file_path.stat()
            file_size = file_stat.st_size
            
            # Detect file type
            mime_type, encoding = self._detect_file_type(file_path)
            file_category = self._categorize_file(file_path, mime_type)
            
            # Calculate file hash
            file_hash = await self._calculate_file_hash(file_path)
            
            # Create base metadata
            metadata = FileMetadata(
                filename=file_path.name,
                file_path=str(file_path),
                file_size=file_size,
                mime_type=mime_type,
                file_category=file_category,
                encoding=encoding,
                file_hash=file_hash,
                created_at=datetime.fromtimestamp(file_stat.st_ctime),
                modified_at=datetime.fromtimestamp(file_stat.st_mtime)
            )
            
            processing_notes = []
            
            # Extract content based on file type
            if extract_content and file_size <= self.max_text_size:
                await self._extract_content(file_path, metadata, processing_notes)
            elif file_size > self.max_text_size:
                processing_notes.append(f"File too large for content extraction: {file_size} bytes")
            
            # Analyze content with AI if requested
            if analyze_content and metadata.text_content:
                await self._analyze_content(metadata, processing_notes)
            
            # Calculate processing time
            metadata.processing_time = time.time() - start_time
            
            logger.info(f"✅ Processed file: {file_path.name} ({file_category.value}, {file_size} bytes)")
            
            return ProcessingResult(
                success=True,
                metadata=metadata,
                processing_notes=processing_notes
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to process file {file_path}: {e}")
            
            # Return partial metadata with error
            metadata = FileMetadata(
                filename=file_path.name,
                file_path=str(file_path),
                file_size=file_path.stat().st_size if file_path.exists() else 0,
                mime_type="unknown",
                file_category=FileCategory.UNKNOWN,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
            
            return ProcessingResult(
                success=False,
                metadata=metadata,
                error_message=str(e)
            )

    def _detect_file_type(self, file_path: Path) -> tuple[str, str]:
        """Detect file MIME type and encoding"""
        try:
            # Try python-magic first if available
            if MAGIC_AVAILABLE:
                mime_type = magic.from_file(str(file_path), mime=True)
                encoding = magic.from_file(str(file_path))
                return mime_type, encoding
            
            # Fallback to mimetypes module
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return mime_type or "application/octet-stream", "unknown"
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to detect file type for {file_path}: {e}")
            return "application/octet-stream", "unknown"

    def _categorize_file(self, file_path: Path, mime_type: str) -> FileCategory:
        """Categorize file based on extension and MIME type"""
        extension = file_path.suffix.lower()
        
        # Check by extension first
        if extension in self.text_extensions:
            return FileCategory.TEXT
        elif extension in self.code_extensions:
            return FileCategory.CODE
        elif extension in self.document_extensions:
            return FileCategory.DOCUMENT
        elif extension in self.spreadsheet_extensions:
            return FileCategory.SPREADSHEET
        elif extension in self.presentation_extensions:
            return FileCategory.PRESENTATION
        elif extension == '.pdf':
            return FileCategory.PDF
        elif extension in {'.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar'}:
            return FileCategory.ARCHIVE
        
        # Check by MIME type
        if mime_type.startswith('text/'):
            return FileCategory.TEXT
        elif mime_type.startswith('image/'):
            return FileCategory.IMAGE
        elif mime_type.startswith('audio/'):
            return FileCategory.AUDIO
        elif mime_type.startswith('video/'):
            return FileCategory.VIDEO
        elif 'json' in mime_type or 'xml' in mime_type:
            return FileCategory.DATA
        
        return FileCategory.BINARY

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hasher = hashlib.sha256()
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to calculate hash for {file_path}: {e}")
            return "unknown"

    async def _extract_content(self, file_path: Path, metadata: FileMetadata, 
                              processing_notes: List[str]):
        """Extract text content from file based on its type"""
        try:
            if metadata.file_category in [FileCategory.TEXT, FileCategory.CODE]:
                await self._extract_text_content(file_path, metadata, processing_notes)
            elif metadata.file_category == FileCategory.DATA:
                await self._extract_data_content(file_path, metadata, processing_notes)
            elif metadata.file_category == FileCategory.DOCUMENT:
                await self._extract_document_content(file_path, metadata, processing_notes)
            elif metadata.file_category == FileCategory.PDF:
                await self._extract_pdf_content(file_path, metadata, processing_notes)
            else:
                processing_notes.append(f"Content extraction not implemented for {metadata.file_category.value}")
                
        except Exception as e:
            logger.error(f"❌ Content extraction failed: {e}")
            metadata.error_message = f"Content extraction failed: {e}"

    async def _extract_text_content(self, file_path: Path, metadata: FileMetadata, 
                                   processing_notes: List[str]):
        """Extract content from text files"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                        content = await f.read()
                    metadata.encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                processing_notes.append("Failed to decode text content with common encodings")
                return
            
            # Truncate if too long
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length] + "... [truncated]"
                processing_notes.append(f"Content truncated to {self.max_content_length} characters")
            
            metadata.text_content = content
            metadata.char_count = len(content)
            metadata.line_count = content.count('\n') + 1
            metadata.word_count = len(content.split())
            
            processing_notes.append(f"Extracted {metadata.char_count} characters, {metadata.word_count} words")
            
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {e}")
            processing_notes.append(f"Text extraction failed: {e}")

    async def _extract_data_content(self, file_path: Path, metadata: FileMetadata, 
                                   processing_notes: List[str]):
        """Extract content from structured data files (JSON, XML, CSV)"""
        try:
            extension = file_path.suffix.lower()
            
            if extension == '.json':
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    metadata.structured_data = data
                    metadata.text_content = json.dumps(data, indent=2)[:self.max_content_length]
                    processing_notes.append("Extracted JSON structure")
            
            elif extension == '.csv':
                # Read CSV as text for now - could enhance with pandas
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    lines = content.split('\n')
                    metadata.line_count = len(lines)
                    metadata.text_content = content[:self.max_content_length]
                    
                    # Extract header if present
                    if lines:
                        metadata.structured_data = {"header": lines[0].split(',')}
                    
                    processing_notes.append(f"Extracted CSV with {len(lines)} rows")
            
            else:
                # Treat as text
                await self._extract_text_content(file_path, metadata, processing_notes)
                
        except Exception as e:
            logger.error(f"❌ Data extraction failed: {e}")
            processing_notes.append(f"Data extraction failed: {e}")

    async def _extract_document_content(self, file_path: Path, metadata: FileMetadata, 
                                       processing_notes: List[str]):
        """Extract content from office documents (DOCX, etc.)"""
        try:
            # For now, just note that document processing would require additional libraries
            # like python-docx, openpyxl, etc.
            processing_notes.append("Document content extraction requires additional libraries")
            
            # Could implement with:
            # - python-docx for DOCX files
            # - openpyxl for XLSX files
            # - python-pptx for PPTX files
            
        except Exception as e:
            logger.error(f"❌ Document extraction failed: {e}")
            processing_notes.append(f"Document extraction failed: {e}")

    async def _extract_pdf_content(self, file_path: Path, metadata: FileMetadata, 
                                  processing_notes: List[str]):
        """Extract content from PDF files"""
        try:
            # PDF content extraction would require libraries like PyPDF2 or pdfplumber
            processing_notes.append("PDF content extraction requires additional libraries")
            
            # Could implement with:
            # - PyPDF2 for basic text extraction
            # - pdfplumber for more advanced extraction
            # - OCR for image-based PDFs
            
        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {e}")
            processing_notes.append(f"PDF extraction failed: {e}")

    async def _analyze_content(self, metadata: FileMetadata, processing_notes: List[str]):
        """Analyze content with AI (placeholder for Lambda Labs GPU integration)"""
        try:
            if not metadata.text_content:
                return
            
            # This is where we would integrate with Lambda Labs GPU for:
            # - Content summarization
            # - Entity extraction
            # - Language detection
            # - Sentiment analysis
            # - Topic classification
            
            # For now, provide basic analysis
            content = metadata.text_content
            
            # Simple language detection (very basic)
            if any(char in content for char in 'abcdefghijklmnopqrstuvwxyz'):
                metadata.language = "en"  # Default to English
            
            # Simple entity extraction (keywords)
            words = content.lower().split()
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            entities = [word.strip('.,!?;:') for word in words if len(word) > 3 and word not in common_words]
            metadata.extracted_entities = list(set(entities))[:50]  # Top 50 entities
            
            # Simple summary (first few sentences)
            sentences = content.split('.')[:3]
            metadata.content_summary = '. '.join(sentences).strip()[:500]
            
            metadata.confidence_score = 0.7  # Basic confidence
            
            processing_notes.append("Applied basic content analysis")
            
        except Exception as e:
            logger.error(f"❌ Content analysis failed: {e}")
            processing_notes.append(f"Content analysis failed: {e}")

    async def process_directory(self, directory_path: Path, 
                               recursive: bool = True) -> List[ProcessingResult]:
        """Process all files in a directory"""
        try:
            results = []
            
            if recursive:
                file_paths = directory_path.rglob('*')
            else:
                file_paths = directory_path.glob('*')
            
            for file_path in file_paths:
                if file_path.is_file():
                    result = await self.process_file(file_path)
                    results.append(result)
            
            logger.info(f"📁 Processed {len(results)} files from {directory_path}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to process directory {directory_path}: {e}")
            return []

    def get_processing_stats(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """Get statistics from processing results"""
        if not results:
            return {}
        
        total_files = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total_files - successful
        
        # Category breakdown
        categories = {}
        total_size = 0
        total_processing_time = 0
        
        for result in results:
            if result.success:
                category = result.metadata.file_category.value
                categories[category] = categories.get(category, 0) + 1
                total_size += result.metadata.file_size
                total_processing_time += result.metadata.processing_time
        
        return {
            "total_files": total_files,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_files) * 100 if total_files > 0 else 0,
            "categories": categories,
            "total_size_bytes": total_size,
            "average_processing_time": total_processing_time / successful if successful > 0 else 0,
            "total_processing_time": total_processing_time
        }

# Global service instance
_binary_file_handler = None

async def get_binary_file_handler() -> BinaryFileHandler:
    """Get or create the global binary file handler instance"""
    global _binary_file_handler
    
    if _binary_file_handler is None:
        _binary_file_handler = BinaryFileHandler()
    
    return _binary_file_handler 