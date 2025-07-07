# Backend Clean Architecture Implementation - Part 2

## Phase 3: Migration Execution

### 3.1 File Migration Script

```python
# scripts/migrate_backend_files.py
import os
import shutil
import json
from pathlib import Path
import subprocess

class BackendMigrator:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.migration_log = []

    def load_migration_map(self):
        """Load the file migration mapping"""
        with open('config/file_migrations.json', 'r') as f:
            return json.load(f)

    def migrate_file(self, old_path, new_path):
        """Migrate a single file using git mv to preserve history"""
        if not os.path.exists(old_path):
            self.migration_log.append(f"SKIP: {old_path} does not exist")
            return False

        # Create target directory
        new_dir = os.path.dirname(new_path)
        if not self.dry_run:
            os.makedirs(new_dir, exist_ok=True)

        # Use git mv to preserve history
        if self.dry_run:
            self.migration_log.append(f"WOULD MOVE: {old_path} -> {new_path}")
        else:
            try:
                subprocess.run(['git', 'mv', old_path, new_path], check=True)
                self.migration_log.append(f"MOVED: {old_path} -> {new_path}")
                return True
            except subprocess.CalledProcessError as e:
                self.migration_log.append(f"ERROR: Failed to move {old_path}: {e}")
                return False

    def update_imports_in_file(self, file_path):
        """Update import statements in a file"""
        import_mappings = {
            'from backend.api': 'from api',
            'from backend.core': 'from core',
            'from backend.domain': 'from domain',
            'from backend.agents.core': 'from core.agents',
            'from backend.agents.specialized': 'from core.use_cases',
            'from backend.orchestration': 'from core.workflows',
            'from backend.models': 'from domain.models',
            'from backend.integrations': 'from infrastructure.integrations',
            'from backend.mcp_servers': 'from infrastructure.mcp_servers',
            'from backend.etl': 'from infrastructure.etl',
            'from backend.monitoring': 'from infrastructure.monitoring',
            'from backend.services': 'from core.services',  # may need manual review
            'from backend.utils': 'from shared.utils',
            'from backend.prompts': 'from shared.prompts',
            'import backend.': 'import sophia.',
        }

        if not os.path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content
        for old_import, new_import in import_mappings.items():
            content = content.replace(old_import, new_import)

        if content != original_content:
            if not self.dry_run:
                with open(file_path, 'w') as f:
                    f.write(content)
            self.migration_log.append(f"UPDATED IMPORTS: {file_path}")

    def run_migration(self):
        """Execute the full migration"""
        print("Loading migration map...")
        migrations = self.load_migration_map()

        # Phase 1: Move files
        print(f"Migrating {len(migrations)} files...")
        for migration in migrations:
            self.migrate_file(migration['old'], migration['new'])

        # Phase 2: Update imports
        print("Updating import statements...")
        for root, dirs, files in os.walk('.'):
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.update_imports_in_file(file_path)

        # Save migration log
        with open('reports/migration_log.txt', 'w') as f:
            f.write('\n'.join(self.migration_log))

        print(f"Migration complete. Log saved to reports/migration_log.txt")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', help='Execute migration (default is dry run)')
    args = parser.parse_args()

    migrator = BackendMigrator(dry_run=not args.execute)
    migrator.run_migration()
```

### 3.2 Service Layer Splitting Script

```python
# scripts/split_service_layer.py
import ast
import os
from pathlib import Path

class ServiceAnalyzer(ast.NodeVisitor):
    """Analyze service files to determine if they're business logic or infrastructure"""

    def __init__(self):
        self.has_external_imports = False
        self.has_io_operations = False
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
            if any(lib in alias.name for lib in ['requests', 'httpx', 'boto3', 'snowflake', 'redis', 'psycopg2']):
                self.has_external_imports = True

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
            if any(lib in node.module for lib in ['requests', 'httpx', 'boto3', 'snowflake', 'redis', 'psycopg2']):
                self.has_external_imports = True

    def visit_Call(self, node):
        # Check for I/O operations
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['get', 'post', 'put', 'delete', 'execute', 'query', 'connect']:
                self.has_io_operations = True
        self.generic_visit(node)

def analyze_service_file(file_path):
    """Determine if service file should go to core or infrastructure"""
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read())
            analyzer = ServiceAnalyzer()
            analyzer.visit(tree)

            # If it has external dependencies or I/O, it's infrastructure
            if analyzer.has_external_imports or analyzer.has_io_operations:
                return 'infrastructure'
            else:
                return 'core'
        except:
            return 'manual_review'

def split_services():
    """Split service files between core and infrastructure"""
    services_dir = Path('backend/services')

    core_services = []
    infra_services = []
    manual_review = []

    for service_file in services_dir.rglob('*.py'):
        if '__pycache__' in str(service_file):
            continue

        classification = analyze_service_file(service_file)

        if classification == 'core':
            core_services.append(service_file)
        elif classification == 'infrastructure':
            infra_services.append(service_file)
        else:
            manual_review.append(service_file)

    # Generate report
    with open('reports/service_split_report.txt', 'w') as f:
        f.write("Service Layer Split Analysis\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Core Services ({len(core_services)}):\n")
        for svc in core_services:
            f.write(f"  - {svc}\n")

        f.write(f"\nInfrastructure Services ({len(infra_services)}):\n")
        for svc in infra_services:
            f.write(f"  - {svc}\n")

        f.write(f"\nManual Review Required ({len(manual_review)}):\n")
        for svc in manual_review:
            f.write(f"  - {svc}\n")

    print(f"Service split analysis complete. Report saved to reports/service_split_report.txt")

if __name__ == '__main__':
    split_services()
```

### 3.3 Dependency Injection Setup

```python
# api/dependencies.py
"""Dependency injection configuration for FastAPI"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from core.ports import (
    AIGatewayPort,
    DatabasePort,
    CachePort,
    FileStoragePort,
    MessageQueuePort,
    SearchPort
)
from infrastructure.integrations.portkey import PortkeyGateway
from infrastructure.integrations.snowflake import SnowflakeDatabase
from infrastructure.integrations.redis import RedisCache
from infrastructure.integrations.s3 import S3FileStorage
from infrastructure.integrations.sqs import SQSMessageQueue
from infrastructure.integrations.pinecone import PineconeSearch

@lru_cache()
def get_ai_gateway() -> AIGatewayPort:
    """Get AI Gateway instance"""
    return PortkeyGateway()

@lru_cache()
def get_database() -> DatabasePort:
    """Get Database instance"""
    return SnowflakeDatabase()

@lru_cache()
def get_cache() -> CachePort:
    """Get Cache instance"""
    return RedisCache()

@lru_cache()
def get_file_storage() -> FileStoragePort:
    """Get File Storage instance"""
    return S3FileStorage()

@lru_cache()
def get_message_queue() -> MessageQueuePort:
    """Get Message Queue instance"""
    return SQSMessageQueue()

@lru_cache()
def get_search() -> SearchPort:
    """Get Search instance"""
    return PineconeSearch()

# Type aliases for cleaner route signatures
AIGatewayDep = Annotated[AIGatewayPort, Depends(get_ai_gateway)]
DatabaseDep = Annotated[DatabasePort, Depends(get_database)]
CacheDep = Annotated[CachePort, Depends(get_cache)]
FileStorageDep = Annotated[FileStoragePort, Depends(get_file_storage)]
MessageQueueDep = Annotated[MessageQueuePort, Depends(get_message_queue)]
SearchDep = Annotated[SearchPort, Depends(get_search)]
```

### 3.4 Main Application Entry Point

```python
# api/main.py
"""Main FastAPI application entry point"""

import sys
from pathlib import Path

# Add project root to Python path for clean imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from api.routes import (
    chat_routes,
    knowledge_routes,
    deployment_routes,
    health_routes,
    mcp_routes
)
from api.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    AuthenticationMiddleware
)
from shared.config import settings
from shared.logging import setup_logging

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting Sophia AI API...")

    # Initialize connections, load models, etc.
    from infrastructure.database import init_db
    from infrastructure.cache import init_cache

    await init_db()
    await init_cache()

    yield

    # Shutdown
    print("Shutting down Sophia AI API...")

    # Close connections, cleanup resources
    from infrastructure.database import close_db
    from infrastructure.cache import close_cache

    await close_db()
    await close_cache()

# Create FastAPI app
app = FastAPI(
    title="Sophia AI API",
    description="Executive AI Orchestrator for Pay Ready",
    version="3.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_routes.router, tags=["health"])
app.include_router(chat_routes.router, prefix="/api/v3", tags=["chat"])
app.include_router(knowledge_routes.router, prefix="/api/v3", tags=["knowledge"])
app.include_router(deployment_routes.router, prefix="/api/v3", tags=["deployment"])
app.include_router(mcp_routes.router, prefix="/api/v3", tags=["mcp"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

## Phase 4: Import Updates and Circular Dependency Resolution

### 4.1 Automated Import Update Script

```python
# scripts/update_all_imports.py
import os
import re
from pathlib import Path
import ast
from typing import Dict, Set, Tuple

class ImportUpdater:
    def __init__(self):
        self.import_mappings = self.create_import_mappings()
        self.circular_dependencies = set()

    def create_import_mappings(self) -> Dict[str, str]:
        """Create comprehensive import mappings"""
        return {
            # Direct mappings
            'backend.api': 'api',
            'backend.core': 'core',
            'backend.domain': 'domain',

            # Agent mappings
            'backend.agents.core': 'core.agents',
            'backend.agents.specialized': 'core.use_cases',

            # Service mappings (requires analysis)
            'backend.services.ai_service': 'core.services.ai_service',
            'backend.services.gong_api_client': 'infrastructure.integrations.gong',
            'backend.services.snowflake_service': 'infrastructure.integrations.snowflake',

            # Model mappings
            'backend.models': 'domain.models',
            'backend.core.models': 'domain.models',

            # Infrastructure mappings
            'backend.integrations': 'infrastructure.integrations',
            'backend.mcp_servers': 'infrastructure.mcp_servers',
            'backend.etl': 'infrastructure.etl',
            'backend.monitoring': 'infrastructure.monitoring',
            'backend.security': 'infrastructure.security',

            # Utility mappings
            'backend.utils': 'shared.utils',
            'backend.prompts': 'shared.prompts',
            'backend.core.constants': 'shared.constants',
            'backend.core.config': 'shared.config',
        }

    def update_file_imports(self, file_path: Path) -> bool:
        """Update imports in a single file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            original = content

            # Update imports using regex
            for old_import, new_import in self.import_mappings.items():
                # Handle 'from X import Y' style
                content = re.sub(
                    rf'from\s+{re.escape(old_import)}',
                    f'from {new_import}',
                    content
                )

                # Handle 'import X' style
                content = re.sub(
                    rf'import\s+{re.escape(old_import)}',
                    f'import {new_import}',
                    content
                )

            # Update relative imports to absolute
            content = self.convert_relative_imports(file_path, content)

            if content != original:
                with open(file_path, 'w') as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return False

    def convert_relative_imports(self, file_path: Path, content: str) -> str:
        """Convert relative imports to absolute imports"""
        # Determine the module path
        module_parts = file_path.parts

        # Find which layer this file belongs to
        if 'api' in module_parts:
            base_module = 'api'
        elif 'core' in module_parts:
            base_module = 'core'
        elif 'domain' in module_parts:
            base_module = 'domain'
        elif 'infrastructure' in module_parts:
            base_module = 'infrastructure'
        elif 'shared' in module_parts:
            base_module = 'shared'
        else:
            return content

        # Replace relative imports
        content = re.sub(
            r'from\s+\.\s+import',
            f'from {base_module} import',
            content
        )

        return content

    def detect_circular_dependencies(self):
        """Detect circular import dependencies"""
        import networkx as nx

        # Build dependency graph
        G = nx.DiGraph()

        for root, dirs, files in os.walk('.'):
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    module = self.file_to_module(file_path)

                    # Parse imports
                    imports = self.extract_imports(file_path)

                    for imp in imports:
                        G.add_edge(module, imp)

        # Find cycles
        try:
            cycles = list(nx.simple_cycles(G))
            self.circular_dependencies = cycles
            return cycles
        except:
            return []

    def file_to_module(self, file_path: Path) -> str:
        """Convert file path to module name"""
        parts = file_path.parts
        if parts[0] == '.':
            parts = parts[1:]

        module = '.'.join(parts).replace('.py', '')
        return module

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract all imports from a file"""
        imports = set()

        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        except:
            pass

        return imports

    def run(self):
        """Run the import update process"""
        updated_files = 0

        for root, dirs, files in os.walk('.'):
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    if self.update_file_imports(file_path):
                        updated_files += 1
                        print(f"Updated: {file_path}")

        print(f"\nUpdated {updated_files} files")

        # Check for circular dependencies
        cycles = self.detect_circular_dependencies()
        if cycles:
            print(f"\nWarning: Found {len(cycles)} circular dependencies:")
            for cycle in cycles:
                print(f"  - {' -> '.join(cycle)}")
        else:
            print("\nNo circular dependencies detected")

if __name__ == '__main__':
    updater = ImportUpdater()
    updater.run()
```
