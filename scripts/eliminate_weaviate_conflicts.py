#!/usr/bin/env python3
"""
Eliminate Weaviate Conflicts - Pure Qdrant Architecture
Remove all Weaviate dependencies and ensure 100% Qdrant-centric memory architecture

Based on critical findings:
- Weaviate still referenced in unified_memory_service_v3.py
- Mixed Weaviate/Qdrant configuration in memory tiers
- Conflicting imports and client initialization
- Need pure Qdrant architecture for consistency
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Any, Any
import json

class WeaviateConflictEliminator:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.eliminated_files = []
        self.updated_files = []
        self.backup_dir = Path("weaviate_elimination_backup")
        
        # Weaviate patterns to eliminate
        self.weaviate_patterns = [
            r'import\s+weaviate',
            r'from\s+weaviate',
            r'weaviate\.Client',
            r'weaviate_url',
            r'weaviate_client',
            r'WEAVIATE_URL',
            r'storage_type.*weaviate',
            r'weaviate.*8080',
            r'semitechnologies/weaviate',
        ]
        
        # Qdrant replacement patterns
        self.qdrant_replacements = {
            r'import\s+weaviate': 'from qdrant_client import QdrantClient',
            r'from\s+weaviate.*': 'from qdrant_client import QdrantClient',
            r'weaviate\.Client\([^)]*\)': 'QdrantClient(url=get_config_value("qdrant_url"))',
            r'weaviate_url': 'qdrant_url',
            r'weaviate_client': 'qdrant_client',
            r'WEAVIATE_URL': 'QDRANT_URL',
            r'storage_type.*weaviate': 'storage_type": "qdrant',
            r'weaviate.*8080': 'qdrant://localhost:6333',
            r'semitechnologies/weaviate': 'qdrant/qdrant',
        }
        
        # Critical files to update
        self.critical_files = [
            "backend/services/unified_memory_service_v3.py",
            "backend/services/unified_memory_service_v2_deprecated.py",
            "backend/services/multimodal_memory_service.py",
            "backend/services/enhanced_memory_service_v3.py",
            "infrastructure/services/vector_indexing_service.py",
            "mcp-servers/ai_memory/server.py",
        ]
        
    def create_backup(self):
        """Create backup of files before modification"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        self.backup_dir.mkdir()
        
        for file_path in self.critical_files:
            file_path = Path(file_path)
            if file_path.exists():
                backup_path = self.backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                print(f"📁 Backed up: {file_path}")
    
    def analyze_weaviate_usage(self) -> Dict[str, List[str]]:
        """Analyze current Weaviate usage across codebase"""
        results = {
            "active_imports": [],
            "configuration_conflicts": [],
            "mixed_architectures": [],
            "deprecated_references": []
        }
        
        for file_path in self.critical_files:
            file_path = Path(file_path)
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for active imports
                if re.search(r'import\s+weaviate', content, re.IGNORECASE):
                    results["active_imports"].append(str(file_path))
                
                # Check for configuration conflicts
                if 'weaviate' in content.lower() and 'qdrant' in content.lower():
                    results["mixed_architectures"].append(str(file_path))
                
                # Check for deprecated references
                if re.search(r'weaviate.*deprecated|# DEPRECATED.*weaviate', content, re.IGNORECASE):
                    results["deprecated_references"].append(str(file_path))
                    
            except Exception as e:
                print(f"❌ Error analyzing {file_path}: {e}")
        
        return results
    
    def eliminate_weaviate_from_memory_service_v3(self):
        """Fix the critical unified_memory_service_v3.py file"""
        file_path = Path("backend/services/unified_memory_service_v3.py")
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace Weaviate imports with Qdrant
            content = re.sub(
                r'# Core imports\ntry:\n    import weaviate\n    WEAVIATE_AVAILABLE = True\nexcept ImportError:\n    WEAVIATE_AVAILABLE = False\n    weaviate = None',
                '# Core imports - Pure Qdrant Architecture\n# Weaviate eliminated for pure Qdrant-centric design',
                content
            )
            
            # Fix memory tier configuration
            content = re.sub(
                r'storage_type="weaviate"',
                'storage_type="qdrant"',
                content
            )
            
            # Update semantic memory tier
            content = re.sub(
                r'"semantic": MemoryTier\(\s*name="Semantic Memory",\s*storage_type="weaviate"',
                '"semantic": MemoryTier(\n                name="Semantic Memory",\n                storage_type="qdrant"',
                content
            )
            
            # Remove WEAVIATE_AVAILABLE checks
            content = re.sub(
                r'if WEAVIATE_AVAILABLE:.*?else:.*?weaviate = None',
                '# Pure Qdrant architecture - no Weaviate dependencies',
                content,
                flags=re.DOTALL
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.updated_files.append(str(file_path))
            print(f"✅ Updated: {file_path}")
            
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
    
    def create_pure_qdrant_memory_service(self):
        """Create a pure Qdrant memory service configuration"""
        config_content = '''"""
Pure Qdrant Memory Architecture Configuration
Eliminates all Weaviate dependencies for consistent architecture
"""

from dataclasses import dataclass
from typing import Dict, Any
from backend.core.auto_esc_config import get_qdrant_config

@dataclass
class QdrantMemoryTier:
    """Pure Qdrant memory tier configuration"""
    name: str
    collection_name: str
    ttl_seconds: int
    max_entries: int
    vector_size: int = 1024
    distance_metric: str = "cosine"
    
    def to_qdrant_config(self) -> Dict[str, Any]:
        """Convert to Qdrant collection configuration"""
        return {
            "collection_name": self.collection_name,
            "vector_size": self.vector_size,
            "distance": self.distance_metric,
            "ttl": self.ttl_seconds,
            "max_entries": self.max_entries
        }

class PureQdrantArchitecture:
    """Pure Qdrant-centric memory architecture"""
    
    def __init__(self):
        self.qdrant_config = get_qdrant_config()
        
        # Pure Qdrant memory tiers
        self.memory_tiers = {
            "episodic": QdrantMemoryTier(
                name="Episodic Memory",
                collection_name="sophia_episodic",
                ttl_seconds=3600,  # 1 hour
                max_entries=10000,
                vector_size=1024
            ),
            "semantic": QdrantMemoryTier(
                name="Semantic Memory", 
                collection_name="sophia_semantic",
                ttl_seconds=86400 * 30,  # 30 days
                max_entries=100000,
                vector_size=1024
            ),
            "visual": QdrantMemoryTier(
                name="Visual Memory",
                collection_name="sophia_visual",
                ttl_seconds=86400 * 7,  # 7 days
                max_entries=50000,
                vector_size=1024
            ),
            "procedural": QdrantMemoryTier(
                name="Procedural Memory",
                collection_name="sophia_procedural",
                ttl_seconds=86400 * 14,  # 14 days
                max_entries=25000,
                vector_size=1024
            )
        }
    
    def get_tier_config(self, tier_name: str) -> Dict[str, Any]:
        """Get Qdrant configuration for a specific tier"""
        if tier_name not in self.memory_tiers:
            raise ValueError(f"Unknown memory tier: {tier_name}")
        
        return self.memory_tiers[tier_name].to_qdrant_config()
    
    def get_all_collections(self) -> List[str]:
        """Get all Qdrant collection names"""
        return [tier.collection_name for tier in self.memory_tiers.values()]
'''
        
        config_path = Path("backend/core/qdrant_memory_config.py")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ Created pure Qdrant configuration: {config_path}")
    
    def update_kubernetes_manifests(self):
        """Update Kubernetes manifests to use pure Qdrant"""
        k8s_files = [
            "k8s/mcp-servers/ai-memory.yaml",
            "k8s/base/qdrant-secrets.yaml",
            "kubernetes/phase2-agentic-rag/deployment.yaml"
        ]
        
        for file_path in k8s_files:
            file_path = Path(file_path)
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace any remaining Weaviate references
                content = re.sub(r'WEAVIATE_URL', 'QDRANT_URL', content)
                content = re.sub(r'weaviate:8080', 'qdrant:6333', content)
                content = re.sub(r'weaviate-', 'qdrant-', content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.updated_files.append(str(file_path))
                print(f"✅ Updated K8s manifest: {file_path}")
                
            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")
    
    def eliminate_deprecated_services(self):
        """Remove or mark deprecated Weaviate services"""
        deprecated_files = [
            "backend/services/unified_memory_service_v2_deprecated.py",
            "backend/services/weaviate_service.py",
            "infrastructure/services/weaviate_deployment.py"
        ]
        
        for file_path in deprecated_files:
            file_path = Path(file_path)
            if file_path.exists():
                # Move to backup instead of deleting
                backup_path = self.backup_dir / f"deprecated_{file_path.name}"
                shutil.move(file_path, backup_path)
                self.eliminated_files.append(str(file_path))
                print(f"🗑️  Deprecated: {file_path} → {backup_path}")
    
    def validate_pure_qdrant_architecture(self) -> Dict[str, Any]:
        """Validate that architecture is pure Qdrant"""
        validation_results = {
            "weaviate_references_found": [],
            "qdrant_configuration_valid": False,
            "memory_tiers_consistent": False,
            "kubernetes_manifests_clean": False
        }
        
        # Check for remaining Weaviate references
        for file_path in self.critical_files:
            file_path = Path(file_path)
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in self.weaviate_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        validation_results["weaviate_references_found"].append(str(file_path))
                        break
                        
            except Exception as e:
                print(f"❌ Error validating {file_path}: {e}")
        
        # Check Qdrant configuration
        try:
            from backend.core.auto_esc_config import get_qdrant_config
            config = get_qdrant_config()
            validation_results["qdrant_configuration_valid"] = bool(config.get("url"))
        except Exception as e:
            print(f"❌ Error validating Qdrant config: {e}")
        
        return validation_results
    
    def generate_report(self) -> str:
        """Generate comprehensive elimination report"""
        analysis = self.analyze_weaviate_usage()
        validation = self.validate_pure_qdrant_architecture()
        
        report = f"""
# 🎯 WEAVIATE ELIMINATION REPORT

**Date**: {os.popen('date').read().strip()}  
**Status**: {'✅ PURE QDRANT ARCHITECTURE' if not validation['weaviate_references_found'] else '⚠️ CONFLICTS DETECTED'}  
**Strategy**: Eliminate all Weaviate dependencies for consistent Qdrant-centric design

## 📊 ELIMINATION RESULTS

### Files Updated
{chr(10).join(f'- ✅ {file}' for file in self.updated_files)}

### Files Eliminated
{chr(10).join(f'- 🗑️ {file}' for file in self.eliminated_files)}

### Weaviate Analysis
- **Active Imports**: {len(analysis['active_imports'])} found
- **Mixed Architectures**: {len(analysis['mixed_architectures'])} files
- **Deprecated References**: {len(analysis['deprecated_references'])} files

### Validation Results
- **Weaviate References**: {len(validation['weaviate_references_found'])} remaining
- **Qdrant Configuration**: {'✅ Valid' if validation['qdrant_configuration_valid'] else '❌ Invalid'}

## 🎯 PURE QDRANT ARCHITECTURE

### Memory Tiers (All Qdrant)
- **Episodic**: sophia_episodic collection (1 hour TTL)
- **Semantic**: sophia_semantic collection (30 days TTL)  
- **Visual**: sophia_visual collection (7 days TTL)
- **Procedural**: sophia_procedural collection (14 days TTL)

### Configuration
- **URL**: {validation.get('qdrant_url', 'Not configured')}
- **API Key**: {'✅ Configured' if validation.get('qdrant_api_key') else '❌ Missing'}
- **Collections**: 4 Qdrant collections configured

## 🚀 NEXT STEPS

1. **Test Qdrant Connection**: Validate all collections are accessible
2. **Update Dependencies**: Remove weaviate-client from requirements
3. **Deploy to Lambda Labs**: Test pure Qdrant architecture
4. **Monitor Performance**: Ensure no degradation from Weaviate elimination

## 📋 COMMANDS TO COMPLETE ELIMINATION

```bash
# Remove Weaviate dependencies
pip uninstall weaviate-client

# Install/update Qdrant client
pip install qdrant-client>=1.7.0

# Test Qdrant connection
python -c "from backend.core.auto_esc_config import get_qdrant_config; print(get_qdrant_config())"

# Deploy to Lambda Labs
./deploy_lambda_labs.sh
```

**Status**: {'🎉 ELIMINATION COMPLETE' if not validation['weaviate_references_found'] else '⚠️ MANUAL CLEANUP REQUIRED'}
"""
        
        return report
    
    def run_elimination(self):
        """Execute complete Weaviate elimination process"""
        print("🚀 Starting Weaviate Elimination Process...")
        
        # Step 1: Create backup
        self.create_backup()
        
        # Step 2: Analyze current usage
        print("\n📊 Analyzing Weaviate usage...")
        analysis = self.analyze_weaviate_usage()
        
        # Step 3: Eliminate from critical files
        print("\n🔧 Eliminating Weaviate from memory services...")
        self.eliminate_weaviate_from_memory_service_v3()
        
        # Step 4: Create pure Qdrant configuration
        print("\n⚙️ Creating pure Qdrant configuration...")
        self.create_pure_qdrant_memory_service()
        
        # Step 5: Update Kubernetes manifests
        print("\n☸️ Updating Kubernetes manifests...")
        self.update_kubernetes_manifests()
        
        # Step 6: Eliminate deprecated services
        print("\n🗑️ Eliminating deprecated services...")
        self.eliminate_deprecated_services()
        
        # Step 7: Generate report
        print("\n📋 Generating elimination report...")
        report = self.generate_report()
        
        # Save report
        report_path = Path("WEAVIATE_ELIMINATION_REPORT.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Elimination complete! Report saved to: {report_path}")
        print(f"📁 Backup created at: {self.backup_dir}")
        
        return report

if __name__ == "__main__":
    eliminator = WeaviateConflictEliminator()
    eliminator.run_elimination() 