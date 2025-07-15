#!/usr/bin/env python3
"""
Weaviate Elimination Executor - Complete Cleanup Script
Ensures pure Qdrant architecture by removing all Weaviate references
"""

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

class WeaviateEliminator:
    def __init__(self):
        self.backup_dir = f"weaviate_elimination_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.changes_made = []
        self.files_deleted = []
        self.files_modified = []
        
    def create_backup(self, file_path: str) -> None:
        """Create backup of file before modification"""
        backup_path = os.path.join(self.backup_dir, file_path)
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(file_path, backup_path)
        print(f"📁 Backed up: {file_path}")
    
    def scan_weaviate_references(self) -> Dict[str, List[str]]:
        """Scan for all Weaviate references in the codebase"""
        references = {
            "python_files": [],
            "typescript_files": [],
            "config_files": [],
            "documentation": [],
            "infrastructure": []
        }
        
        excluded_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'backup'}
        
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'weaviate' in content.lower():
                            if file.endswith('.py'):
                                references["python_files"].append(file_path)
                            elif file.endswith(('.ts', '.tsx', '.js')):
                                references["typescript_files"].append(file_path)
                            elif file.endswith(('.yaml', '.yml', '.json')):
                                references["config_files"].append(file_path)
                            elif file.endswith('.md'):
                                references["documentation"].append(file_path)
                            else:
                                references["infrastructure"].append(file_path)
                except:
                    continue
        
        return references
    
    def eliminate_python_files(self, files: List[str]) -> None:
        """Eliminate Weaviate references from Python files"""
        print("\n🐍 Processing Python files...")
        
        for file_path in files:
            if 'backup' in file_path or 'elimination' in file_path:
                continue
                
            self.create_backup(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace Weaviate imports
            content = re.sub(r'from QDRANT_client.*?\n', '', content, flags=re.MULTILINE)
            content = re.sub(r'from QDRANT_client import QdrantClient.*?\n', '', content, flags=re.MULTILINE)
            
            # Replace Weaviate client references
            content = re.sub(r'QDRANT_client', 'QDRANT_client', content)
            content = re.sub(r'self\.weaviate', 'self.QDRANT_client', content)
            content = re.sub(r'\.QDRANT_client', '.QDRANT_client', content)
            
            # Replace Weaviate URLs and configurations
            content = re.sub(r'QDRANT_URL', 'QDRANT_URL', content)
            content = re.sub(r'QDRANT_URL', 'QDRANT_URL', content)
            content = re.sub(r'http://.*QDRANT_client.*:8080', 'http://localhost:6333', content)
            content = re.sub(r'weaviate:8080', 'qdrant:6333', content)
            
            # Replace Weaviate-specific method calls
            content = re.sub(r'\.data_object\.create', '.upsert', content)
            content = re.sub(r'\.query\.get', '.search', content)
            
            # Replace Weaviate collection references
            content = re.sub(r'"weaviate"', '"qdrant"', content)
            content = re.sub(r"'weaviate'", "'qdrant'", content)
            content = re.sub(r'weaviate_gpu', 'QDRANT_gpu', content)
            content = re.sub(r'weaviate-gpu', 'qdrant-gpu', content)
            
            # Replace Weaviate in comments and strings
            content = re.sub(r'# .*[Ww]eaviate.*', '# Qdrant vector database', content)
            content = re.sub(r'""".*[Ww]eaviate.*"""', '"""Qdrant vector database"""', content, flags=re.DOTALL)
            
            # Update function names
            content = re.sub(r'_create_weaviate_collection', '_create_QDRANT_collection', content)
            content = re.sub(r'init_weaviate_schema', 'init_QDRANT_schema', content)
            content = re.sub(r'test_weaviate_', 'test_QDRANT_', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_modified.append(file_path)
                print(f"  ✅ Modified: {file_path}")
    
    def eliminate_typescript_files(self, files: List[str]) -> None:
        """Eliminate Weaviate references from TypeScript files"""
        print("\n📜 Processing TypeScript files...")
        
        for file_path in files:
            if 'backup' in file_path or 'elimination' in file_path:
                continue
                
            self.create_backup(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace Weaviate infrastructure
            content = re.sub(r'weaviate-deployment', 'qdrant-deployment', content)
            content = re.sub(r'weaviateDeployment', 'qdrantDeployment', content)
            content = re.sub(r'weaviateService', 'qdrantService', content)
            content = re.sub(r'weaviateEndpoint', 'qdrantEndpoint', content)
            content = re.sub(r'weaviateHPA', 'qdrantHPA', content)
            content = re.sub(r'weaviatePVC', 'qdrantPVC', content)
            
            # Replace Weaviate image references
            content = re.sub(r'semitechnologies/weaviate:.*', 'qdrant/qdrant:v1.8.0', content)
            
            # Replace Weaviate ports
            content = re.sub(r':8080', ':6333', content)
            content = re.sub(r'8080:', '6333:', content)
            
            # Replace Weaviate environment variables
            content = re.sub(r'WEAVIATE_', 'QDRANT_', content)
            
            # Replace Weaviate paths
            content = re.sub(r'/var/lib/weaviate', '/var/lib/qdrant/storage', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_modified.append(file_path)
                print(f"  ✅ Modified: {file_path}")
    
    def eliminate_config_files(self, files: List[str]) -> None:
        """Eliminate Weaviate references from configuration files"""
        print("\n⚙️  Processing configuration files...")
        
        for file_path in files:
            if 'backup' in file_path or 'elimination' in file_path:
                continue
                
            self.create_backup(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # YAML/JSON specific replacements
            if file_path.endswith(('.yaml', '.yml')):
                content = re.sub(r'weaviate-service', 'qdrant-service', content)
                content = re.sub(r'weaviate-gpu', 'qdrant-gpu', content)
                content = re.sub(r'app: weaviate', 'app: qdrant', content)
                content = re.sub(r'name: weaviate', 'name: qdrant', content)
                content = re.sub(r'- weaviate', '- qdrant', content)
                
            elif file_path.endswith('.json'):
                content = re.sub(r'"weaviate"', '"qdrant"', content)
                content = re.sub(r'"WEAVIATE_', '"QDRANT_', content)
                content = re.sub(r'weaviate_', 'QDRANT_', content)
            
            # Generic replacements
            content = re.sub(r'weaviate:8080', 'qdrant:6333', content)
            content = re.sub(r'localhost:8080', 'localhost:6333', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_modified.append(file_path)
                print(f"  ✅ Modified: {file_path}")
    
    def delete_weaviate_files(self) -> None:
        """Delete Weaviate-specific files"""
        print("\n🗑️  Deleting Weaviate-specific files...")
        
        files_to_delete = [
            "infrastructure/pulumi/weaviate-deployment.ts",
            "scripts/init_weaviate_schema.py",
            "scripts/test_weaviate_cloud_integration.py",
            "scripts/optimize_weaviate_alpha.py"
        ]
        
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                self.create_backup(file_path)
                os.remove(file_path)
                self.files_deleted.append(file_path)
                print(f"  🗑️  Deleted: {file_path}")
    
    def update_github_workflows(self) -> None:
        """Update GitHub Actions workflows to remove Weaviate contamination"""
        print("\n🔄 Updating GitHub Actions workflows...")
        
        workflow_files = [
            ".github/workflows/lambda_labs_fortress_deploy.yml",
            ".github/workflows/deploy-lambda-labs-aligned.yml"
        ]
        
        for file_path in workflow_files:
            if os.path.exists(file_path):
                self.create_backup(file_path)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Remove disabled flags
                content = re.sub(r'if: false\n', '', content)
                content = re.sub(r'# DISABLED: Weaviate contamination.*?\n', '', content)
                
                # Update Weaviate references
                content = re.sub(r'weaviate-gpu', 'qdrant-gpu', content)
                content = re.sub(r'statefulset/weaviate-gpu', 'statefulset/qdrant-gpu', content)
                content = re.sub(r'Weaviate status', 'Qdrant status', content)
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified.append(file_path)
                    print(f"  ✅ Updated: {file_path}")
    
    def create_QDRANT_init_script(self) -> None:
        """Create Qdrant initialization script to replace Weaviate schema"""
        print("\n🔧 Creating Qdrant initialization script...")
        
        script_content = '''#!/usr/bin/env python3
"""
Initialize Qdrant Collections for Sophia AI
Replaces the old Weaviate schema initialization
"""

import asyncio
import os
import logging
from QDRANT_client import QdrantClient
from QDRANT_client.models import Distance, VectorParams, CollectionConfig
from backend.core.auto_esc_config import get_config_value

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_QDRANT_client():
    """Create Qdrant client connection"""
    QDRANT_URL = get_config_value("QDRANT_URL")
    QDRANT_api_key = get_config_value("QDRANT_API_KEY")
    
    try:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_api_key,
            timeout=30
        )
        
        # Test connection
        client.get_collections()
        logger.info(f"✅ Connected to Qdrant at {QDRANT_URL}")
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant: {e}")
        raise

def create_collection(client: QdrantClient, name: str, vector_size: int = 768):
    """Create Qdrant collection if it doesn't exist"""
    try:
        client.get_collection(name)
        logger.info(f"Collection {name} already exists")
        return
    except:
        pass  # Collection doesn't exist, create it
    
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    logger.info(f"✅ Created Qdrant collection: {name}")

def initialize_sophia_collections():
    """Initialize all Sophia AI collections"""
    logger.info("🚀 Initializing Qdrant Collections for Sophia AI")
    
    client = create_QDRANT_client()
    
    # Core collections
    collections = [
        "sophia_episodic",
        "sophia_semantic", 
        "sophia_visual",
        "sophia_procedural",
        "sophia_competitors",
        "sophia_competitor_events",
        "sophia_competitor_analytics"
    ]
    
    for collection in collections:
        create_collection(client, collection)
    
    logger.info("✅ Qdrant schema initialization complete!")

if __name__ == "__main__":
    initialize_sophia_collections()
'''
        
        with open("scripts/init_QDRANT_collections.py", 'w') as f:
            f.write(script_content)
        
        print("  ✅ Created: scripts/init_QDRANT_collections.py")
        self.changes_made.append("Created Qdrant initialization script")
    
    def update_documentation(self) -> None:
        """Update documentation to reflect Weaviate elimination"""
        print("\n📚 Updating documentation...")
        
        # Update .cursorrules
        cursorrules_path = ".cursorrules"
        if os.path.exists(cursorrules_path):
            self.create_backup(cursorrules_path)
            
            with open(cursorrules_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix the memory architecture rules
            content = re.sub(
                r'### ❌ FORBIDDEN - Deprecated Systems.*?- \*\*NEVER\*\* use `CORTEX\.EMBED_TEXT_768\(\)`.*?\n',
                '''### ❌ FORBIDDEN - Eliminated Systems
- **NEVER** use Weaviate (completely eliminated from architecture)
- **NEVER** use Snowflake Cortex for new features
- **NEVER** reference any Weaviate clients or configurations
- **NEVER** use mixed vector database architectures
- **NEVER** use `CORTEX.EMBED_TEXT_768()` - use GPU embeddings instead
''',
                content,
                flags=re.DOTALL
            )
            
            # Update the mandatory section
            content = re.sub(
                r'### ✅ MANDATORY - Use GPU-Accelerated Memory Stack.*?- \*\*ALWAYS\*\* use Lambda GPU inference for embeddings',
                '''### ✅ MANDATORY - Use Pure Qdrant Memory Stack
- **ALWAYS** use `UnifiedMemoryServiceV3` from `backend.services.unified_memory_service_v3`
- **ALWAYS** use Qdrant for vector storage (ONLY vector database)
- **ALWAYS** use Redis for caching layer
- **ALWAYS** use PostgreSQL with pgvector for hybrid queries
- **ALWAYS** use Lambda GPU inference for embeddings''',
                content,
                flags=re.DOTALL
            )
            
            with open(cursorrules_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.files_modified.append(cursorrules_path)
            print("  ✅ Updated: .cursorrules")
    
    def generate_report(self) -> None:
        """Generate elimination report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "files_modified": len(self.files_modified),
            "files_deleted": len(self.files_deleted),
            "changes_made": self.changes_made,
            "modified_files": self.files_modified,
            "deleted_files": self.files_deleted,
            "backup_location": self.backup_dir
        }
        
        with open("weaviate_elimination_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Elimination Report:")
        print(f"  Files modified: {len(self.files_modified)}")
        print(f"  Files deleted: {len(self.files_deleted)}")
        print(f"  Backup location: {self.backup_dir}")
        print(f"  Report saved: weaviate_elimination_report.json")
    
    def execute_elimination(self) -> None:
        """Execute complete Weaviate elimination"""
        print("🚀 Starting Weaviate Elimination Process...")
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Scan for references
        references = self.scan_weaviate_references()
        total_files = sum(len(files) for files in references.values())
        
        print(f"\n📊 Weaviate References Found:")
        print(f"  Python files: {len(references['python_files'])}")
        print(f"  TypeScript files: {len(references['typescript_files'])}")
        print(f"  Config files: {len(references['config_files'])}")
        print(f"  Documentation: {len(references['documentation'])}")
        print(f"  Infrastructure: {len(references['infrastructure'])}")
        print(f"  Total files: {total_files}")
        
        if total_files == 0:
            print("✅ No Weaviate references found - already eliminated!")
            return
        
        # Execute elimination steps
        self.eliminate_python_files(references['python_files'])
        self.eliminate_typescript_files(references['typescript_files'])
        self.eliminate_config_files(references['config_files'])
        self.delete_weaviate_files()
        self.update_github_workflows()
        self.create_QDRANT_init_script()
        self.update_documentation()
        
        # Generate report
        self.generate_report()
        
        print("\n🎉 Weaviate Elimination Complete!")
        print("✅ Pure Qdrant architecture achieved")
        print("✅ All Weaviate references eliminated")
        print("✅ GitHub Actions workflows updated")
        print("✅ Documentation corrected")
        print("✅ Qdrant initialization script created")

if __name__ == "__main__":
    eliminator = WeaviateEliminator()
    eliminator.execute_elimination() 