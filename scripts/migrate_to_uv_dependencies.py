#!/usr/bin/env python3
"""
Phoenix 2.1 UV Dependency Migration Script
Consolidates all requirements.txt files into pyproject.toml with proper categorization
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dependency categories based on package names
DEV_DEPENDENCIES = {
    'pytest', 'pytest-asyncio', 'pytest-cov', 'pytest-mock',
    'black', 'ruff', 'mypy', 'flake8', 'pylint', 'isort',
    'coverage', 'pre-commit', 'tox',
    'sphinx', 'mkdocs', 'mkdocs-material',
    'httpx', 'requests-mock', 'faker', 'factory-boy',
    'ipython', 'ipdb', 'jupyter', 'notebook',
    'bandit', 'safety',
}

DOCS_DEPENDENCIES = {
    'sphinx', 'mkdocs', 'mkdocs-material', 'sphinx-rtd-theme',
    'myst-parser', 'sphinx-autodoc-typehints'
}

# Packages to exclude (Flask and related)
EXCLUDE_PACKAGES = {
    'flask', 'flask-cors', 'flask-restful', 'flask-sqlalchemy',
    'gunicorn', 'werkzeug', 'itsdangerous', 'click<8.0',
    'jinja2<3.0'  # Old Flask version constraint
}

class DependencyMigrator:
    def __init__(self):
        self.requirements_files = []
        self.all_dependencies = {}
        self.dev_dependencies = {}
        self.docs_dependencies = {}
        self.runtime_dependencies = {}
        
    def find_requirements_files(self) -> List[Path]:
        """Find all requirements files in the project"""
        files = []
        for pattern in ['requirements*.txt', '**/requirements*.txt']:
            files.extend(Path('.').glob(pattern))
        
        # Filter out external and node_modules
        files = [f for f in files if not any(
            part in str(f) for part in ['node_modules', '.venv', 'external/']
        )]
        
        self.requirements_files = sorted(files)
        logger.info(f"Found {len(self.requirements_files)} requirements files")
        for f in self.requirements_files:
            logger.info(f"  - {f}")
        return self.requirements_files
    
    def parse_requirements_file(self, filepath: Path) -> Dict[str, str]:
        """Parse a requirements file and return package:version dict"""
        dependencies = {}
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle different requirement formats
                if '==' in line:
                    pkg, version = line.split('==', 1)
                    dependencies[pkg.strip()] = f">={version.strip()}"
                elif '>=' in line:
                    pkg, version = line.split('>=', 1)
                    dependencies[pkg.strip()] = f">={version.strip()}"
                elif '~=' in line:
                    pkg, version = line.split('~=', 1)
                    dependencies[pkg.strip()] = f"~={version.strip()}"
                else:
                    # No version specified
                    pkg = line.split('[')[0].strip()
                    dependencies[pkg] = ""
        
        return dependencies
    
    def categorize_dependencies(self):
        """Categorize all dependencies into runtime, dev, and docs"""
        for pkg, version in self.all_dependencies.items():
            pkg_lower = pkg.lower()
            
            # Skip excluded packages
            if pkg_lower in EXCLUDE_PACKAGES:
                logger.warning(f"Excluding legacy package: {pkg}")
                continue
            
            # Categorize
            if pkg_lower in DOCS_DEPENDENCIES:
                self.docs_dependencies[pkg] = version
            elif pkg_lower in DEV_DEPENDENCIES:
                self.dev_dependencies[pkg] = version
            else:
                self.runtime_dependencies[pkg] = version
    
    def merge_dependencies(self):
        """Merge all requirements files, handling version conflicts"""
        for req_file in self.requirements_files:
            logger.info(f"Processing {req_file}")
            deps = self.parse_requirements_file(req_file)
            
            for pkg, version in deps.items():
                if pkg in self.all_dependencies:
                    # Handle version conflict - take the more recent/specific
                    existing = self.all_dependencies[pkg]
                    if version and (not existing or version > existing):
                        logger.info(f"  Updating {pkg}: {existing} -> {version}")
                        self.all_dependencies[pkg] = version
                else:
                    self.all_dependencies[pkg] = version
        
        logger.info(f"Total unique dependencies: {len(self.all_dependencies)}")
    
    def generate_pyproject_content(self) -> str:
        """Generate the new pyproject.toml content"""
        lines = []
        lines.append('[project]')
        lines.append('name = "sophia-ai"')
        lines.append('version = "2.1.0"')
        lines.append('description = "Sophia AI - Enterprise AI Orchestration Platform with Unified FastAPI"')
        lines.append('readme = "README.md"')
        lines.append('requires-python = ">=3.12"')
        lines.append('license = {text = "Proprietary"}')
        lines.append('authors = [')
        lines.append('    {name = "Sophia AI Team", email = "team@sophia-ai.com"}')
        lines.append(']')
        lines.append('keywords = ["ai", "orchestration", "fastapi", "enterprise", "mcp"]')
        lines.append('')
        lines.append('dependencies = [')
        
        # Add runtime dependencies
        for pkg, version in sorted(self.runtime_dependencies.items()):
            if version:
                lines.append(f'    "{pkg}{version}",')
            else:
                lines.append(f'    "{pkg}",')
        
        lines.append(']')
        lines.append('')
        lines.append('[project.optional-dependencies]')
        lines.append('dev = [')
        
        # Add dev dependencies
        for pkg, version in sorted(self.dev_dependencies.items()):
            if version:
                lines.append(f'    "{pkg}{version}",')
            else:
                lines.append(f'    "{pkg}",')
        
        lines.append(']')
        lines.append('docs = [')
        
        # Add docs dependencies
        for pkg, version in sorted(self.docs_dependencies.items()):
            if version:
                lines.append(f'    "{pkg}{version}",')
            else:
                lines.append(f'    "{pkg}",')
        
        lines.append(']')
        lines.append('all = [')
        lines.append('    "sophia-ai[dev]",')
        lines.append('    "sophia-ai[docs]",')
        lines.append(']')
        lines.append('')
        lines.append('[build-system]')
        lines.append('requires = ["hatchling"]')
        lines.append('build-backend = "hatchling.build"')
        lines.append('')
        lines.append('[tool.uv]')
        lines.append('dev-dependencies = [')
        lines.append('    "pytest>=8.0.0",')
        lines.append('    "pytest-asyncio>=0.23.0",')
        lines.append('    "pytest-cov>=4.1.0",')
        lines.append('    "black>=24.0.0",')
        lines.append('    "ruff>=0.1.0",')
        lines.append('    "mypy>=1.8.0",')
        lines.append('    "coverage>=7.4.0",')
        lines.append('    "pre-commit>=3.6.0",')
        lines.append('    "httpx>=0.26.0",')
        lines.append(']')
        lines.append('')
        lines.append('[tool.hatch.build.targets.wheel]')
        lines.append('packages = ["backend"]')
        lines.append('')
        lines.append('[tool.black]')
        lines.append('line-length = 88')
        lines.append('target-version = ["py312"]')
        lines.append('include = "\\\\.pyi?$"')
        lines.append('extend-exclude = """')
        lines.append('/(')
        lines.append('  # directories')
        lines.append('  \\\\.eggs')
        lines.append('  | \\\\.git')
        lines.append('  | \\\\.hg')
        lines.append('  | \\\\.mypy_cache')
        lines.append('  | \\\\.tox')
        lines.append('  | \\\\.venv')
        lines.append('  | build')
        lines.append('  | dist')
        lines.append('  | external')
        lines.append(')/')
        lines.append('"""')
        lines.append('')
        lines.append('[tool.ruff]')
        lines.append('target-version = "py312"')
        lines.append('line-length = 88')
        lines.append('select = ["E", "F", "W", "I", "N", "B", "C4", "UP", "S", "A", "C90", "T20", "SIM", "ARG"]')
        lines.append('ignore = ["E501", "B008", "B904"]')
        lines.append('exclude = [')
        lines.append('    ".git",')
        lines.append('    ".venv",')
        lines.append('    "__pycache__",')
        lines.append('    "external",')
        lines.append('    "build",')
        lines.append('    "dist",')
        lines.append(']')
        lines.append('')
        lines.append('[tool.mypy]')
        lines.append('python_version = "3.12"')
        lines.append('strict = true')
        lines.append('warn_return_any = true')
        lines.append('warn_unused_configs = true')
        lines.append('ignore_missing_imports = true')
        lines.append('exclude = [')
        lines.append('    "external/",')
        lines.append('    "build/",')
        lines.append('    "dist/",')
        lines.append(']')
        lines.append('')
        lines.append('[tool.pytest.ini_options]')
        lines.append('minversion = "8.0"')
        lines.append('addopts = "-ra -q --strict-markers"')
        lines.append('testpaths = ["tests"]')
        lines.append('pythonpath = ["."]')
        lines.append('asyncio_mode = "auto"')
        lines.append('')
        lines.append('[tool.coverage.run]')
        lines.append('source = ["backend"]')
        lines.append('omit = [')
        lines.append('    "*/tests/*",')
        lines.append('    "*/test_*",')
        lines.append('    "*/__pycache__/*",')
        lines.append('    "*/external/*",')
        lines.append(']')
        lines.append('')
        lines.append('[tool.coverage.report]')
        lines.append('precision = 2')
        lines.append('show_missing = true')
        lines.append('skip_covered = false')
        
        return '\n'.join(lines)
    
    def backup_existing_files(self):
        """Backup existing pyproject.toml and requirements files"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"backup_dependencies_{timestamp}")
        backup_dir.mkdir(exist_ok=True)
        
        # Backup pyproject.toml
        if Path("pyproject.toml").exists():
            shutil.copy2("pyproject.toml", backup_dir / "pyproject.toml")
            logger.info(f"Backed up pyproject.toml to {backup_dir}")
        
        # Backup requirements files
        for req_file in self.requirements_files:
            dest = backup_dir / req_file.name
            shutil.copy2(req_file, dest)
            logger.info(f"Backed up {req_file} to {dest}")
        
        return backup_dir
    
    def update_dockerfiles(self):
        """Update all Dockerfiles to use UV"""
        dockerfiles = list(Path('.').glob('**/Dockerfile*'))
        dockerfiles = [f for f in dockerfiles if not any(
            part in str(f) for part in ['node_modules', '.venv', 'external/']
        )]
        
        for dockerfile in dockerfiles:
            logger.info(f"Updating {dockerfile}")
            with open(dockerfile, 'r') as f:
                content = f.read()
            
            # Replace pip install commands
            content = re.sub(
                r'RUN pip install.*requirements.*\.txt.*',
                'RUN pip install uv && uv pip install --system .',
                content
            )
            content = re.sub(
                r'COPY requirements.*\.txt.*',
                'COPY pyproject.toml .',
                content
            )
            
            with open(dockerfile, 'w') as f:
                f.write(content)
    
    def update_github_workflows(self):
        """Update GitHub Actions workflows"""
        workflows = list(Path('.github/workflows').glob('*.yml')) + \
                   list(Path('.github/workflows').glob('*.yaml'))
        
        for workflow in workflows:
            logger.info(f"Updating {workflow}")
            with open(workflow, 'r') as f:
                content = f.read()
            
            # Replace pip install commands
            content = re.sub(
                r'pip install -r.*requirements.*\.txt',
                'pip install uv && uv pip install .[dev]',
                content
            )
            
            with open(workflow, 'w') as f:
                f.write(content)
    
    def run_migration(self):
        """Execute the full migration process"""
        logger.info("Starting UV dependency migration...")
        
        # Step 1: Find all requirements files
        self.find_requirements_files()
        
        # Step 2: Backup existing files
        backup_dir = self.backup_existing_files()
        logger.info(f"Backups created in {backup_dir}")
        
        # Step 3: Merge all dependencies
        self.merge_dependencies()
        
        # Step 4: Categorize dependencies
        self.categorize_dependencies()
        
        # Step 5: Generate new pyproject.toml
        new_content = self.generate_pyproject_content()
        
        # Step 6: Write new pyproject.toml
        with open("pyproject.toml", "w") as f:
            f.write(new_content)
        logger.info("Generated new pyproject.toml")
        
        # Step 7: Update Dockerfiles
        self.update_dockerfiles()
        
        # Step 8: Update GitHub workflows
        self.update_github_workflows()
        
        # Step 9: Install with UV to generate lock file
        logger.info("Installing dependencies with UV...")
        subprocess.run(["uv", "pip", "install", "-e", ".[dev,docs]"], check=True)
        
        # Step 10: Delete old requirements files
        for req_file in self.requirements_files:
            req_file.unlink()
            logger.info(f"Deleted {req_file}")
        
        logger.info("Migration complete!")
        logger.info(f"Runtime dependencies: {len(self.runtime_dependencies)}")
        logger.info(f"Dev dependencies: {len(self.dev_dependencies)}")
        logger.info(f"Docs dependencies: {len(self.docs_dependencies)}")

if __name__ == "__main__":
    migrator = DependencyMigrator()
    migrator.run_migration() 