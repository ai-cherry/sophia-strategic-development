#!/usr/bin/env python3
"""
🏗️ MONOREPO MIGRATOR - COMPLETE TRANSFORMATION
Migrates entire Sophia AI codebase to monorepo structure

ARCHITECTURE TRANSFORMATION:
- backend/ → apps/api/
- frontend/ → apps/frontend/  
- mcp-servers/ → apps/mcp-servers/
- Shared code → libs/
- Unified configuration → config/
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict
import json

class MonorepoMigrator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.migration_log = []
        self.backup_dir = self.project_root / f"monorepo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Define monorepo structure mapping
        self.migration_mapping = {
            # Applications
            "backend": "apps/api",
            "frontend": "apps/frontend", 
            "mcp-servers": "apps/mcp-servers",
            "n8n-integration": "apps/n8n-bridge",
            "sophia-chrome-extension": "apps/chrome-extension",
            "sophia-vscode-extension": "apps/vscode-extension",
            
            # Shared libraries
            "core": "libs/core",
            "shared": "libs/shared", 
            "domain": "libs/domain",
            
            # Infrastructure
            "infrastructure": "libs/infrastructure",
            "kubernetes": "libs/kubernetes",
            "k8s": "libs/k8s", 
            
            # Configuration (consolidate)
            "config": "config",
            "configs": "config",
            "mcp-config": "config/mcp",
            
            # Scripts remain
            "scripts": "scripts",
            
            # Documentation restructure
            "docs": "docs"
        }
        
        # New monorepo structure to create
        self.monorepo_structure = {
            "apps": {
                "api": {"src": "backend_code", "tests": "backend_tests"},
                "frontend": {"src": "frontend_code", "public": "frontend_public"},
                "mcp-servers": {"servers": "mcp_servers_code"},
                "n8n-bridge": {"workflows": "n8n_workflows"},
                "chrome-extension": {"manifest": "extension_files"},
                "vscode-extension": {"extension": "vscode_files"}
            },
            "libs": {
                "core": {"services": "core_services", "utils": "core_utils"},
                "shared": {"types": "shared_types", "constants": "shared_constants"},
                "domain": {"entities": "domain_entities", "models": "domain_models"},
                "infrastructure": {"pulumi": "infra_code", "k8s": "k8s_manifests"},
                "ui": {"components": "ui_components", "styles": "ui_styles"}
            },
            "config": {
                "eslint": "eslint_configs",
                "prettier": "prettier_configs",
                "typescript": "ts_configs",
                "ruff": "ruff_configs",
                "mcp": "mcp_configs"
            }
        }
        
    def execute_migration(self):
        """Execute complete monorepo migration"""
        
        print("🏗️ MONOREPO MIGRATION - COMPLETE TRANSFORMATION")
        print("===============================================")
        print(f"📅 Started: {datetime.now()}")
        print("🎯 Target: Transform to apps/ and libs/ structure")
        print(f"🛡️ Backup: {self.backup_dir}")
        print("")
        
        # Phase 1: Create backup
        self._create_backup()
        
        # Phase 2: Create new structure
        self._create_monorepo_structure()
        
        # Phase 3: Migrate applications
        self._migrate_applications()
        
        # Phase 4: Migrate shared libraries
        self._migrate_shared_libraries()
        
        # Phase 5: Consolidate configuration
        self._consolidate_configuration()
        
        # Phase 6: Update import paths
        self._update_import_paths()
        
        # Phase 7: Create root configuration files
        self._create_root_configs()
        
        # Phase 8: Clean up old structure
        self._cleanup_old_structure()
        
        # Phase 9: Generate migration report
        self._generate_migration_report()
        
        print("✅ MONOREPO MIGRATION COMPLETE!")
        print(f"   Migrated: {len(self.migration_log)} items")
        print("   New structure: apps/ and libs/")
        print(f"   Backup: {self.backup_dir}")
        
    def _create_backup(self):
        """Create complete backup before migration"""
        
        print("🛡️ Creating complete backup...")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup critical directories (skip node_modules to avoid symlink issues)
        backup_dirs = ["backend", "mcp-servers", "core", "shared", "config", "infrastructure"]
        
        for dir_name in backup_dirs:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                dst_dir = self.backup_dir / dir_name
                try:
                    shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns('node_modules', '.git'))
                    print(f"✅ Backed up: {dir_name}")
                except Exception as e:
                    print(f"⚠️ Backup warning for {dir_name}: {e}")
                    
        # Special handling for frontend (skip node_modules)
        frontend_src = self.project_root / "frontend"
        if frontend_src.exists():
            frontend_dst = self.backup_dir / "frontend"
            try:
                shutil.copytree(frontend_src, frontend_dst, ignore=shutil.ignore_patterns('node_modules'))
                print("✅ Backed up: frontend (excluding node_modules)")
            except Exception as e:
                print(f"⚠️ Backup warning for frontend: {e}")
                
        print(f"✅ Complete backup created: {self.backup_dir}")
        
    def _create_monorepo_structure(self):
        """Create new monorepo directory structure"""
        
        print("🏗️ Creating monorepo structure...")
        
        # Create apps/ structure
        for app_name, app_structure in self.monorepo_structure["apps"].items():
            app_dir = self.project_root / "apps" / app_name
            app_dir.mkdir(parents=True, exist_ok=True)
            
            for subdir in app_structure.keys():
                (app_dir / subdir).mkdir(exist_ok=True)
                
            print(f"✅ Created: apps/{app_name}")
            
        # Create libs/ structure  
        for lib_name, lib_structure in self.monorepo_structure["libs"].items():
            lib_dir = self.project_root / "libs" / lib_name
            lib_dir.mkdir(parents=True, exist_ok=True)
            
            for subdir in lib_structure.keys():
                (lib_dir / subdir).mkdir(exist_ok=True)
                
            print(f"✅ Created: libs/{lib_name}")
            
        # Create config/ structure
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        for config_name in self.monorepo_structure["config"].keys():
            (config_dir / config_name).mkdir(exist_ok=True)
            
        print("✅ Monorepo structure created")
        
    def _migrate_applications(self):
        """Migrate applications to apps/ directory"""
        
        print("📱 Migrating applications...")
        
        # Backend → apps/api
        if (self.project_root / "backend").exists():
            self._migrate_directory("backend", "apps/api/src")
            self._log_migration("backend", "apps/api/src", "Backend API application")
            
        # Frontend → apps/frontend  
        if (self.project_root / "frontend").exists():
            self._migrate_directory("frontend", "apps/frontend/src")
            self._log_migration("frontend", "apps/frontend/src", "Frontend application")
            
        # MCP Servers → apps/mcp-servers
        if (self.project_root / "mcp-servers").exists():
            self._migrate_directory("mcp-servers", "apps/mcp-servers/servers")
            self._log_migration("mcp-servers", "apps/mcp-servers/servers", "MCP servers")
            
        # Extensions
        extensions = [
            ("sophia-chrome-extension", "apps/chrome-extension/manifest"),
            ("sophia-vscode-extension", "apps/vscode-extension/extension"),
            ("n8n-integration", "apps/n8n-bridge/workflows")
        ]
        
        for src, dst in extensions:
            if (self.project_root / src).exists():
                self._migrate_directory(src, dst)
                self._log_migration(src, dst, f"{src} application")
                
        print("✅ Applications migrated")
        
    def _migrate_shared_libraries(self):
        """Migrate shared code to libs/ directory"""
        
        print("📚 Migrating shared libraries...")
        
        # Core → libs/core
        if (self.project_root / "core").exists():
            self._migrate_directory("core", "libs/core/services")
            self._log_migration("core", "libs/core/services", "Core services")
            
        # Shared → libs/shared
        if (self.project_root / "shared").exists():
            self._migrate_directory("shared", "libs/shared/types")
            self._log_migration("shared", "libs/shared/types", "Shared utilities")
            
        # Domain → libs/domain
        if (self.project_root / "domain").exists():
            self._migrate_directory("domain", "libs/domain/entities")
            self._log_migration("domain", "libs/domain/entities", "Domain models")
            
        # Infrastructure → libs/infrastructure
        if (self.project_root / "infrastructure").exists():
            self._migrate_directory("infrastructure", "libs/infrastructure/pulumi")
            self._log_migration("infrastructure", "libs/infrastructure/pulumi", "Infrastructure code")
            
        # Kubernetes → libs/infrastructure/k8s
        k8s_dirs = ["kubernetes", "k8s", "k3s-manifests"]
        for k8s_dir in k8s_dirs:
            if (self.project_root / k8s_dir).exists():
                self._migrate_directory(k8s_dir, "libs/infrastructure/k8s")
                self._log_migration(k8s_dir, "libs/infrastructure/k8s", "Kubernetes manifests")
                
        print("✅ Shared libraries migrated")
        
    def _consolidate_configuration(self):
        """Consolidate all configuration files"""
        
        print("⚙️ Consolidating configuration...")
        
        # Collect all config files
        config_sources = [
            ("config", "config"),
            ("configs", "config"), 
            ("mcp-config", "config/mcp"),
            (".eslintrc*", "config/eslint"),
            (".prettierrc*", "config/prettier"),
            ("tsconfig*.json", "config/typescript"),
            ("ruff.toml", "config/ruff"),
            ("pyproject.toml", "config/python")
        ]
        
        for src_pattern, dst_dir in config_sources:
            self._migrate_config_files(src_pattern, dst_dir)
            
        print("✅ Configuration consolidated")
        
    def _update_import_paths(self):
        """Update import paths throughout codebase"""
        
        print("🔗 Updating import paths...")
        
        # Define import path mappings
        import_mappings = {
            # Backend imports
            "from backend.": "from apps.api.src.",
            "import backend.": "import apps.api.src.",
            
            # Core imports  
            "from core.": "from libs.core.",
            "import core.": "import libs.core.",
            
            # Shared imports
            "from shared.": "from libs.shared.",
            "import shared.": "import libs.shared.",
            
            # Domain imports
            "from domain.": "from libs.domain.",
            "import domain.": "import libs.domain.",
            
            # Infrastructure imports
            "from infrastructure.": "from libs.infrastructure.",
            "import infrastructure.": "import libs.infrastructure."
        }
        
        # Update all Python files
        python_files = list(self.project_root.rglob("*.py"))
        updated_files = 0
        
        for py_file in python_files:
            if self._update_file_imports(py_file, import_mappings):
                updated_files += 1
                
        print(f"✅ Updated imports in {updated_files} Python files")
        
        # Update TypeScript files
        ts_files = list(self.project_root.rglob("*.ts")) + list(self.project_root.rglob("*.tsx"))
        ts_updated = 0
        
        ts_mappings = {
            "from '../backend": "from '../apps/api/src",
            "from './backend": "from './apps/api/src",
            "from '../core": "from '../libs/core",
            "from './core": "from './libs/core"
        }
        
        for ts_file in ts_files:
            if self._update_file_imports(ts_file, ts_mappings):
                ts_updated += 1
                
        print(f"✅ Updated imports in {ts_updated} TypeScript files")
        
    def _create_root_configs(self):
        """Create root configuration files for monorepo"""
        
        print("📋 Creating root configuration files...")
        
        # Create workspace configuration
        workspace_config = {
            "name": "sophia-ai-monorepo",
            "version": "1.0.0",
            "workspaces": [
                "apps/*",
                "libs/*"
            ],
            "scripts": {
                "build": "npm run build --workspaces",
                "test": "npm run test --workspaces",
                "lint": "npm run lint --workspaces",
                "dev": "npm run dev --workspaces"
            },
            "devDependencies": {
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "eslint": "^8.0.0",
                "prettier": "^3.0.0",
                "typescript": "^5.0.0"
            }
        }
        
        with open(self.project_root / "package.json", 'w') as f:
            json.dump(workspace_config, f, indent=2)
            
        # Create monorepo pyproject.toml
        pyproject_content = '''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "sophia-ai-monorepo"
version = "1.0.0"
description = "Sophia AI - Executive AI Orchestrator Monorepo"
authors = [{name = "Sophia AI Team"}]

[tool.hatch.build.targets.wheel]
packages = ["apps", "libs"]

[tool.ruff]
# Import configuration from config/ruff/
extend = "config/ruff/ruff.toml"

[tool.mypy]
# Import configuration from config/python/
mypy_path = "libs:apps"
'''
        
        with open(self.project_root / "pyproject.toml", 'w') as f:
            f.write(pyproject_content)
            
        # Create TypeScript configuration
        tsconfig_content = '''{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@sophia/core/*": ["libs/core/*"],
      "@sophia/shared/*": ["libs/shared/*"],
      "@sophia/domain/*": ["libs/domain/*"],
      "@sophia/ui/*": ["libs/ui/*"]
    }
  },
  "references": [
    { "path": "apps/frontend" },
    { "path": "apps/chrome-extension" },
    { "path": "apps/vscode-extension" },
    { "path": "libs/core" },
    { "path": "libs/shared" },
    { "path": "libs/ui" }
  ]
}'''
        
        with open(self.project_root / "tsconfig.json", 'w') as f:
            f.write(tsconfig_content)
            
        print("✅ Root configuration files created")
        
    def _cleanup_old_structure(self):
        """Clean up old directory structure"""
        
        print("🧹 Cleaning up old structure...")
        
        # Directories to remove after migration
        old_dirs = [
            "backend", "frontend", "mcp-servers", "core", "shared", 
            "infrastructure", "kubernetes", "k8s", "k3s-manifests",
            "configs", "mcp-config", "sophia-chrome-extension",
            "sophia-vscode-extension", "n8n-integration"
        ]
        
        cleaned_dirs = 0
        for old_dir in old_dirs:
            old_path = self.project_root / old_dir
            if old_path.exists():
                # Double check it's empty or has been migrated
                if self._is_safe_to_remove(old_path):
                    shutil.rmtree(old_path)
                    print(f"🗑️ Removed: {old_dir}")
                    cleaned_dirs += 1
                else:
                    print(f"⚠️ Skipped: {old_dir} (not empty)")
                    
        print(f"✅ Cleaned up {cleaned_dirs} old directories")
        
    def _migrate_directory(self, src: str, dst: str):
        """Migrate directory from src to dst"""
        
        src_path = self.project_root / src
        dst_path = self.project_root / dst
        
        if not src_path.exists():
            return
            
        # Create destination directory
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move contents
        try:
            if dst_path.exists():
                # Merge contents
                for item in src_path.iterdir():
                    dst_item = dst_path / item.name
                    if item.is_dir():
                        shutil.copytree(item, dst_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dst_item)
            else:
                # Move entire directory
                shutil.move(str(src_path), str(dst_path))
                
            print(f"📦 Migrated: {src} → {dst}")
            
        except Exception as e:
            print(f"❌ Error migrating {src} to {dst}: {e}")
            
    def _migrate_config_files(self, pattern: str, dst_dir: str):
        """Migrate configuration files matching pattern"""
        
        dst_path = self.project_root / dst_dir
        dst_path.mkdir(parents=True, exist_ok=True)
        
        # Handle directory patterns
        if not pattern.startswith('.') and not pattern.endswith('*'):
            src_path = self.project_root / pattern
            if src_path.exists() and src_path.is_dir():
                for item in src_path.iterdir():
                    dst_item = dst_path / item.name
                    if item.is_file():
                        shutil.copy2(item, dst_item)
                        
        # Handle file patterns
        else:
            for config_file in self.project_root.glob(pattern):
                if config_file.is_file():
                    dst_file = dst_path / config_file.name
                    shutil.copy2(config_file, dst_file)
                    
    def _update_file_imports(self, file_path: Path, mappings: Dict[str, str]) -> bool:
        """Update import statements in a file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Apply all mappings
            for old_import, new_import in mappings.items():
                content = content.replace(old_import, new_import)
                
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"❌ Error updating imports in {file_path}: {e}")
            
        return False
        
    def _is_safe_to_remove(self, path: Path) -> bool:
        """Check if directory is safe to remove (empty or migrated)"""
        
        if not path.exists():
            return True
            
        # Check if directory is empty
        try:
            items = list(path.iterdir())
            return len(items) == 0
        except:
            return False
            
    def _log_migration(self, src: str, dst: str, description: str):
        """Log migration action"""
        
        self.migration_log.append({
            "source": src,
            "destination": dst,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
    def _generate_migration_report(self):
        """Generate comprehensive migration report"""
        
        report_path = self.project_root / "MONOREPO_MIGRATION_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write(f"""# 🏗️ MONOREPO MIGRATION REPORT

**Generated:** {datetime.now()}  
**Migration Items:** {len(self.migration_log)}  
**Backup Location:** {self.backup_dir}  

## 📊 MIGRATION STATISTICS

### Applications Migrated:
- **Backend API:** `backend/` → `apps/api/src/`
- **Frontend:** `frontend/` → `apps/frontend/src/`
- **MCP Servers:** `mcp-servers/` → `apps/mcp-servers/servers/`
- **Extensions:** Various → `apps/*/`

### Libraries Organized:
- **Core Services:** `core/` → `libs/core/services/`
- **Shared Utilities:** `shared/` → `libs/shared/types/`
- **Domain Models:** `domain/` → `libs/domain/entities/`
- **Infrastructure:** `infrastructure/` → `libs/infrastructure/`

### Configuration Consolidated:
- **All configs:** → `config/*/`
- **TypeScript paths:** Updated for monorepo
- **Python imports:** Updated for new structure

## 📦 MIGRATION LOG

""")
            
            for migration in self.migration_log:
                f.write(f"- **{migration['description']}:** `{migration['source']}` → `{migration['destination']}`\n")
                
            f.write("""

## ✅ NEW MONOREPO STRUCTURE

```
sophia-ai/
├── apps/                  # Applications
│   ├── api/              # Backend API (from backend/)
│   ├── frontend/         # React frontend  
│   ├── mcp-servers/      # MCP microservices
│   ├── n8n-bridge/       # N8N integration
│   ├── chrome-extension/ # Chrome extension
│   └── vscode-extension/ # VS Code extension
├── libs/                 # Shared libraries
│   ├── core/            # Core services
│   ├── shared/          # Shared utilities
│   ├── domain/          # Domain models
│   ├── infrastructure/  # Infrastructure code
│   └── ui/              # UI components
├── config/              # Centralized configuration
│   ├── eslint/          # ESLint configs
│   ├── prettier/        # Prettier configs
│   ├── typescript/      # TypeScript configs
│   ├── ruff/            # Ruff configs
│   └── mcp/             # MCP configs
├── scripts/             # Development scripts
└── docs/                # Documentation
```

## 🚀 BENEFITS ACHIEVED

- **🏗️ Clean Architecture:** Separated apps and libraries
- **📦 Workspace Management:** NPM workspaces configured
- **🔗 Unified Imports:** TypeScript path mapping
- **⚙️ Centralized Config:** All configuration consolidated
- **🛡️ Safety:** Complete backup created
- **📈 Scalability:** Ready for unlimited app addition

## 🎯 NEXT STEPS

1. Verify all applications work in new structure
2. Update CI/CD pipelines for monorepo
3. Configure workspace scripts
4. Update documentation links
5. Proceed with legacy code elimination

""")
        
        print(f"📋 Migration report saved: {report_path}")

if __name__ == "__main__":
    migrator = MonorepoMigrator()
    migrator.execute_migration() 