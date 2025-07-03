#!/usr/bin/env python3
"""
Archive legacy Docker files to clean up the repository
Part of Phoenix 2.1 Docker consolidation
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Files to keep (canonical)
KEEP_FILES = {
    './Dockerfile',
    './docker/Dockerfile.mcp-server',
    './docker-compose.yml',
    './docker-compose.override.yml',
    './docker-compose.prod.yml',
    './.dockerignore',
}

# Patterns for files to archive
ARCHIVE_PATTERNS = [
    'Dockerfile.*',
    'docker-compose.*.yml',
    'docker-compose.*.yaml',
]

# Directories to check
CHECK_DIRS = [
    '.',
    './backend',
    './mcp-servers',
    './gong-webhook-service',
    './mcp-gateway',
]

def find_docker_files():
    """Find all Docker-related files in the project"""
    docker_files = set()
    
    for check_dir in CHECK_DIRS:
        if not os.path.exists(check_dir):
            continue
            
        for pattern in ARCHIVE_PATTERNS:
            path = Path(check_dir)
            for file in path.rglob(pattern):
                # Skip external and node_modules
                if 'external' in str(file) or 'node_modules' in str(file):
                    continue
                docker_files.add(str(file))
    
    # Add specific Dockerfiles
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['external', 'node_modules', '.git', '__pycache__']):
            continue
            
        for file in files:
            if file.startswith('Dockerfile'):
                filepath = os.path.join(root, file)
                docker_files.add(filepath)
    
    return docker_files

def categorize_files(docker_files):
    """Categorize files into keep, archive, and delete"""
    keep = set()
    archive = set()
    delete = set()
    
    for file in docker_files:
        # Normalize path
        normalized = os.path.normpath(file)
        
        if normalized in KEEP_FILES:
            keep.add(file)
        elif any(pattern in file for pattern in ['.uv.', '.debug', '.working', '.test']):
            # Delete temporary/development files
            delete.add(file)
        else:
            # Archive everything else
            archive.add(file)
    
    return keep, archive, delete

def create_archive_directory():
    """Create archive directory with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = f"archive/docker_legacy_{timestamp}"
    os.makedirs(archive_dir, exist_ok=True)
    return archive_dir

def archive_files(files, archive_dir):
    """Archive files preserving directory structure"""
    for file in files:
        # Create relative path in archive
        rel_path = os.path.relpath(file, '.')
        dest_path = os.path.join(archive_dir, rel_path)
        
        # Create destination directory
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Copy file
        shutil.copy2(file, dest_path)
        logger.info(f"Archived: {file} -> {dest_path}")
        
        # Remove original
        os.remove(file)
        logger.info(f"Removed original: {file}")

def delete_files(files):
    """Delete temporary files"""
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            logger.info(f"Deleted: {file}")

def create_archive_readme(archive_dir, archived_files):
    """Create README in archive directory"""
    readme_path = os.path.join(archive_dir, 'README.md')
    
    content = f"""# Archived Docker Files

Archived on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Purpose
These Docker files were archived as part of the Phoenix 2.1 Docker consolidation effort.
They are kept for reference but should not be used for new deployments.

## Canonical Files
The following files are now the canonical Docker configuration:
- `/Dockerfile` - Main multi-stage Dockerfile
- `/docker/Dockerfile.mcp-server` - MCP server Dockerfile
- `/docker-compose.yml` - Main compose file
- `/docker-compose.override.yml` - Development overrides
- `/docker-compose.prod.yml` - Production overrides

## Archived Files ({len(archived_files)} total)
"""
    
    for file in sorted(archived_files):
        content += f"- {file}\n"
    
    with open(readme_path, 'w') as f:
        f.write(content)

def main():
    """Main execution"""
    logger.info("Starting Docker file cleanup...")
    
    # Find all Docker files
    docker_files = find_docker_files()
    logger.info(f"Found {len(docker_files)} Docker-related files")
    
    # Categorize files
    keep, archive, delete = categorize_files(docker_files)
    
    logger.info(f"Files to keep: {len(keep)}")
    logger.info(f"Files to archive: {len(archive)}")
    logger.info(f"Files to delete: {len(delete)}")
    
    if not archive and not delete:
        logger.info("No files to archive or delete. Cleanup complete!")
        return
    
    # Create archive directory
    archive_dir = create_archive_directory()
    logger.info(f"Created archive directory: {archive_dir}")
    
    # Archive files
    if archive:
        archive_files(archive, archive_dir)
        create_archive_readme(archive_dir, archive)
    
    # Delete temporary files
    if delete:
        delete_files(delete)
    
    # Summary
    logger.info("\nCleanup Summary:")
    logger.info(f"- Kept: {len(keep)} canonical files")
    logger.info(f"- Archived: {len(archive)} legacy files to {archive_dir}")
    logger.info(f"- Deleted: {len(delete)} temporary files")
    logger.info("\nDocker consolidation complete!")

if __name__ == "__main__":
    main() 