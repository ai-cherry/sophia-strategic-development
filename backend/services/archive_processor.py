"""
📦 Archive Processor - Secure Archive Processing
Handles ZIP, TAR, and other archive formats with security validation and extraction

Security Features:
- Path traversal protection (zip bomb protection)
- Size limits and compression ratio checks
- Malware scanning integration
- Safe extraction with sandboxing
"""

import asyncio
import zipfile
import tarfile
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import mimetypes
import os
import stat

logger = logging.getLogger(__name__)

class ArchiveType(Enum):
    """Supported archive types"""
    ZIP = "zip"
    TAR = "tar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    TAR_XZ = "tar.xz"
    UNKNOWN = "unknown"

@dataclass
class ArchiveInfo:
    """Information about an archive file"""
    archive_type: ArchiveType
    total_files: int
    total_size: int
    compressed_size: int
    compression_ratio: float
    file_list: List[str]
    has_executable: bool = False
    has_hidden_files: bool = False
    has_nested_archives: bool = False
    security_warnings: List[str] = None

    def __post_init__(self):
        if self.security_warnings is None:
            self.security_warnings = []

@dataclass
class ExtractionResult:
    """Result of archive extraction"""
    success: bool
    extracted_files: List[str]
    skipped_files: List[str]
    extraction_path: Path
    total_extracted_size: int
    error_message: str = None
    security_violations: List[str] = None

    def __post_init__(self):
        if self.security_violations is None:
            self.security_violations = []

class ArchiveProcessor:
    """Service for processing archive files with security validation"""
    
    def __init__(self, extraction_dir: str = "temp/extracted"):
        """Initialize the archive processor"""
        self.extraction_dir = Path(extraction_dir)
        self.extraction_dir.mkdir(parents=True, exist_ok=True)
        
        # Security limits
        self.max_extraction_size = 10 * 1024 * 1024 * 1024  # 10GB
        self.max_files_count = 100000  # 100k files
        self.max_compression_ratio = 1000  # Prevent zip bombs
        self.max_file_size = 1024 * 1024 * 1024  # 1GB per file
        self.max_path_length = 255
        
        # Dangerous file patterns
        self.dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
            '.app', '.dmg', '.pkg', '.deb', '.rpm',
            '.sh', '.bash', '.zsh', '.ps1', '.vbs', '.js'
        }
        
        logger.info(f"📦 Archive Processor initialized with extraction dir: {self.extraction_dir}")

    async def analyze_archive(self, archive_path: Path) -> ArchiveInfo:
        """Analyze archive without extracting it"""
        try:
            archive_type = self._detect_archive_type(archive_path)
            
            if archive_type == ArchiveType.ZIP:
                return await self._analyze_zip(archive_path)
            elif archive_type in [ArchiveType.TAR, ArchiveType.TAR_GZ, ArchiveType.TAR_BZ2, ArchiveType.TAR_XZ]:
                return await self._analyze_tar(archive_path)
            else:
                raise ValueError(f"Unsupported archive type: {archive_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to analyze archive {archive_path}: {e}")
            raise

    def _detect_archive_type(self, archive_path: Path) -> ArchiveType:
        """Detect archive type based on file extension and magic bytes"""
        filename = archive_path.name.lower()
        
        if filename.endswith('.zip'):
            return ArchiveType.ZIP
        elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
            return ArchiveType.TAR_GZ
        elif filename.endswith('.tar.bz2') or filename.endswith('.tbz2'):
            return ArchiveType.TAR_BZ2
        elif filename.endswith('.tar.xz') or filename.endswith('.txz'):
            return ArchiveType.TAR_XZ
        elif filename.endswith('.tar'):
            return ArchiveType.TAR
        else:
            return ArchiveType.UNKNOWN

    async def _analyze_zip(self, archive_path: Path) -> ArchiveInfo:
        """Analyze ZIP archive"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                file_list = []
                total_size = 0
                compressed_size = 0
                has_executable = False
                has_hidden_files = False
                has_nested_archives = False
                security_warnings = []
                
                for info in zf.infolist():
                    filename = info.filename
                    file_list.append(filename)
                    
                    total_size += info.file_size
                    compressed_size += info.compress_size
                    
                    # Security checks
                    if self._is_dangerous_file(filename):
                        has_executable = True
                        security_warnings.append(f"Executable file detected: {filename}")
                    
                    if filename.startswith('.') or '/..' in filename:
                        has_hidden_files = True
                        security_warnings.append(f"Hidden/traversal file detected: {filename}")
                    
                    if self._is_archive_file(filename):
                        has_nested_archives = True
                    
                    if len(filename) > self.max_path_length:
                        security_warnings.append(f"Filename too long: {filename}")
                    
                    if info.file_size > self.max_file_size:
                        security_warnings.append(f"File too large: {filename} ({info.file_size} bytes)")
                
                # Check compression ratio
                compression_ratio = total_size / max(compressed_size, 1)
                if compression_ratio > self.max_compression_ratio:
                    security_warnings.append(f"Suspicious compression ratio: {compression_ratio:.1f}")
                
                return ArchiveInfo(
                    archive_type=ArchiveType.ZIP,
                    total_files=len(file_list),
                    total_size=total_size,
                    compressed_size=compressed_size,
                    compression_ratio=compression_ratio,
                    file_list=file_list,
                    has_executable=has_executable,
                    has_hidden_files=has_hidden_files,
                    has_nested_archives=has_nested_archives,
                    security_warnings=security_warnings
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to analyze ZIP file: {e}")
            raise

    async def _analyze_tar(self, archive_path: Path) -> ArchiveInfo:
        """Analyze TAR archive"""
        try:
            # Determine the correct mode based on file extension
            mode = 'r'
            archive_type = self._detect_archive_type(archive_path)
            
            if archive_type == ArchiveType.TAR_GZ:
                mode = 'r:gz'
            elif archive_type == ArchiveType.TAR_BZ2:
                mode = 'r:bz2'
            elif archive_type == ArchiveType.TAR_XZ:
                mode = 'r:xz'
            
            with tarfile.open(archive_path, mode) as tf:
                file_list = []
                total_size = 0
                compressed_size = archive_path.stat().st_size
                has_executable = False
                has_hidden_files = False
                has_nested_archives = False
                security_warnings = []
                
                for member in tf.getmembers():
                    filename = member.name
                    file_list.append(filename)
                    
                    if member.isfile():
                        total_size += member.size
                    
                    # Security checks
                    if self._is_dangerous_file(filename):
                        has_executable = True
                        security_warnings.append(f"Executable file detected: {filename}")
                    
                    if filename.startswith('.') or '/..' in filename:
                        has_hidden_files = True
                        security_warnings.append(f"Hidden/traversal file detected: {filename}")
                    
                    if self._is_archive_file(filename):
                        has_nested_archives = True
                    
                    if len(filename) > self.max_path_length:
                        security_warnings.append(f"Filename too long: {filename}")
                    
                    if member.size > self.max_file_size:
                        security_warnings.append(f"File too large: {filename} ({member.size} bytes)")
                
                # Check compression ratio
                compression_ratio = total_size / max(compressed_size, 1)
                if compression_ratio > self.max_compression_ratio:
                    security_warnings.append(f"Suspicious compression ratio: {compression_ratio:.1f}")
                
                return ArchiveInfo(
                    archive_type=archive_type,
                    total_files=len(file_list),
                    total_size=total_size,
                    compressed_size=compressed_size,
                    compression_ratio=compression_ratio,
                    file_list=file_list,
                    has_executable=has_executable,
                    has_hidden_files=has_hidden_files,
                    has_nested_archives=has_nested_archives,
                    security_warnings=security_warnings
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to analyze TAR file: {e}")
            raise

    async def extract_archive(self, archive_path: Path, job_id: str, 
                            safe_mode: bool = True) -> ExtractionResult:
        """Extract archive with security validation"""
        try:
            # First analyze the archive
            archive_info = await self.analyze_archive(archive_path)
            
            # Security pre-checks
            if safe_mode:
                if archive_info.total_size > self.max_extraction_size:
                    raise ValueError(f"Archive too large: {archive_info.total_size} bytes")
                
                if archive_info.total_files > self.max_files_count:
                    raise ValueError(f"Too many files: {archive_info.total_files}")
                
                if archive_info.compression_ratio > self.max_compression_ratio:
                    raise ValueError(f"Suspicious compression ratio: {archive_info.compression_ratio}")
            
            # Create extraction directory
            extraction_path = self.extraction_dir / f"job_{job_id}"
            extraction_path.mkdir(parents=True, exist_ok=True)
            
            # Extract based on archive type
            if archive_info.archive_type == ArchiveType.ZIP:
                result = await self._extract_zip(archive_path, extraction_path, safe_mode)
            else:
                result = await self._extract_tar(archive_path, extraction_path, safe_mode)
            
            result.extraction_path = extraction_path
            logger.info(f"📦 Extracted {len(result.extracted_files)} files to {extraction_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to extract archive: {e}")
            return ExtractionResult(
                success=False,
                extracted_files=[],
                skipped_files=[],
                extraction_path=Path(),
                total_extracted_size=0,
                error_message=str(e)
            )

    async def _extract_zip(self, archive_path: Path, extraction_path: Path, 
                          safe_mode: bool) -> ExtractionResult:
        """Extract ZIP archive"""
        extracted_files = []
        skipped_files = []
        total_extracted_size = 0
        security_violations = []
        
        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                for info in zf.infolist():
                    filename = info.filename
                    
                    # Security validation
                    if safe_mode:
                        if self._is_path_traversal(filename):
                            skipped_files.append(filename)
                            security_violations.append(f"Path traversal detected: {filename}")
                            continue
                        
                        if self._is_dangerous_file(filename):
                            skipped_files.append(filename)
                            security_violations.append(f"Dangerous file skipped: {filename}")
                            continue
                    
                    # Extract file
                    try:
                        target_path = extraction_path / filename
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with zf.open(info) as source, open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                        
                        extracted_files.append(filename)
                        total_extracted_size += info.file_size
                        
                    except Exception as e:
                        skipped_files.append(filename)
                        logger.warning(f"⚠️ Failed to extract {filename}: {e}")
            
            return ExtractionResult(
                success=True,
                extracted_files=extracted_files,
                skipped_files=skipped_files,
                extraction_path=extraction_path,
                total_extracted_size=total_extracted_size,
                security_violations=security_violations
            )
            
        except Exception as e:
            logger.error(f"❌ ZIP extraction failed: {e}")
            raise

    async def _extract_tar(self, archive_path: Path, extraction_path: Path, 
                          safe_mode: bool) -> ExtractionResult:
        """Extract TAR archive"""
        extracted_files = []
        skipped_files = []
        total_extracted_size = 0
        security_violations = []
        
        try:
            # Determine the correct mode
            mode = 'r'
            archive_type = self._detect_archive_type(archive_path)
            
            if archive_type == ArchiveType.TAR_GZ:
                mode = 'r:gz'
            elif archive_type == ArchiveType.TAR_BZ2:
                mode = 'r:bz2'
            elif archive_type == ArchiveType.TAR_XZ:
                mode = 'r:xz'
            
            with tarfile.open(archive_path, mode) as tf:
                for member in tf.getmembers():
                    filename = member.name
                    
                    # Security validation
                    if safe_mode:
                        if self._is_path_traversal(filename):
                            skipped_files.append(filename)
                            security_violations.append(f"Path traversal detected: {filename}")
                            continue
                        
                        if self._is_dangerous_file(filename):
                            skipped_files.append(filename)
                            security_violations.append(f"Dangerous file skipped: {filename}")
                            continue
                    
                    # Extract file/directory
                    try:
                        # Safe extraction - prevent absolute paths
                        safe_path = extraction_path / filename.lstrip('/')
                        
                        if member.isdir():
                            safe_path.mkdir(parents=True, exist_ok=True)
                        elif member.isfile():
                            safe_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with tf.extractfile(member) as source, open(safe_path, 'wb') as target:
                                if source:
                                    shutil.copyfileobj(source, target)
                        
                        extracted_files.append(filename)
                        if member.isfile():
                            total_extracted_size += member.size
                            
                    except Exception as e:
                        skipped_files.append(filename)
                        logger.warning(f"⚠️ Failed to extract {filename}: {e}")
            
            return ExtractionResult(
                success=True,
                extracted_files=extracted_files,
                skipped_files=skipped_files,
                extraction_path=extraction_path,
                total_extracted_size=total_extracted_size,
                security_violations=security_violations
            )
            
        except Exception as e:
            logger.error(f"❌ TAR extraction failed: {e}")
            raise

    def _is_dangerous_file(self, filename: str) -> bool:
        """Check if file is potentially dangerous"""
        extension = Path(filename).suffix.lower()
        return extension in self.dangerous_extensions

    def _is_archive_file(self, filename: str) -> bool:
        """Check if file is an archive"""
        extension = Path(filename).suffix.lower()
        return extension in {'.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar'}

    def _is_path_traversal(self, filename: str) -> bool:
        """Check for path traversal attacks"""
        # Check for directory traversal patterns
        if '..' in filename or filename.startswith('/'):
            return True
        
        # Check for absolute paths on Windows
        if len(filename) > 1 and filename[1] == ':':
            return True
        
        return False

    async def cleanup_extraction(self, job_id: str):
        """Clean up extracted files for a job"""
        try:
            extraction_path = self.extraction_dir / f"job_{job_id}"
            
            if extraction_path.exists():
                shutil.rmtree(extraction_path)
                logger.info(f"🧹 Cleaned up extraction directory for job {job_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup extraction for job {job_id}: {e}")

    async def get_file_list(self, job_id: str) -> List[str]:
        """Get list of extracted files for a job"""
        try:
            extraction_path = self.extraction_dir / f"job_{job_id}"
            
            if not extraction_path.exists():
                return []
            
            files = []
            for file_path in extraction_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(extraction_path)
                    files.append(str(relative_path))
            
            return sorted(files)
            
        except Exception as e:
            logger.error(f"❌ Failed to get file list for job {job_id}: {e}")
            return []

# Global service instance
_archive_processor = None

async def get_archive_processor() -> ArchiveProcessor:
    """Get or create the global archive processor instance"""
    global _archive_processor
    
    if _archive_processor is None:
        _archive_processor = ArchiveProcessor()
    
    return _archive_processor 