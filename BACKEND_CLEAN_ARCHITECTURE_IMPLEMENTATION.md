# Sophia AI Backend Clean Architecture Implementation Guide

## Executive Summary

This guide provides a complete implementation plan for refactoring the Sophia AI backend from its current 26-directory structure into a clean, layered architecture with 5 core directories. The refactoring preserves 100% functionality while establishing clear architectural boundaries and dependency rules.

## Architecture Overview

### New Directory Structure
```
sophia-main/
├── api/                 # FastAPI routes and HTTP layer
├── core/                # Business logic and use cases
├── domain/              # Entities and domain models
├── infrastructure/      # External integrations and I/O
├── shared/              # Common utilities and constants
└── backend/             # (deprecated - to be removed)
```

### Dependency Rules
- **Domain** → imports nothing (pure Python)
- **Core** → imports Domain, Shared
- **API** → imports Core, Shared (never Infrastructure directly)
- **Infrastructure** → imports Core, Domain, Shared
- **Shared** → imports nothing from other layers

## Phase 1: Analysis and Preparation

### 1.1 Create Dependency Analysis Script

```python
# scripts/analyze_backend_dependencies.py
import ast
import os
from pathlib import Path
from collections import defaultdict
import csv
import networkx as nx
import matplotlib.pyplot as plt

class DependencyAnalyzer(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)

def analyze_dependencies(root_dir='backend'):
    """Analyze all Python files and their dependencies"""
    dependencies = defaultdict(set)

    for root, dirs, files in os.walk(root_dir):
        # Skip __pycache__ and .git
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]

        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                module_path = str(file_path).replace('/', '.').replace('.py', '')

                try:
                    with open(file_path, 'r') as f:
                        tree = ast.parse(f.read())
                        analyzer = DependencyAnalyzer(str(file_path))
                        analyzer.visit(tree)

                        for imp in analyzer.imports:
                            if imp.startswith('backend.'):
                                dependencies[module_path].add(imp)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")

    return dependencies

def generate_dependency_report(dependencies):
    """Generate CSV report of dependencies"""
    with open('reports/backend_dependencies.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['From Module', 'To Module', 'Current Layer', 'Target Layer'])

        for from_module, to_modules in dependencies.items():
            current_layer = classify_current_layer(from_module)
            for to_module in to_modules:
                target_layer = classify_target_layer(to_module)
                writer.writerow([from_module, to_module, current_layer, target_layer])

def classify_current_layer(module_path):
    """Classify module into current architecture layer"""
    if 'backend.api' in module_path:
        return 'api'
    elif 'backend.agents' in module_path:
        return 'agents'
    elif 'backend.services' in module_path:
        return 'services'
    elif 'backend.models' in module_path:
        return 'models'
    elif 'backend.integrations' in module_path:
        return 'integrations'
    elif 'backend.core' in module_path:
        return 'core'
    elif 'backend.domain' in module_path:
        return 'domain'
    elif 'backend.mcp_servers' in module_path:
        return 'mcp_servers'
    elif 'backend.etl' in module_path:
        return 'etl'
    elif 'backend.monitoring' in module_path:
        return 'monitoring'
    elif 'backend.utils' in module_path:
        return 'utils'
    else:
        return 'other'

def classify_target_layer(module_path):
    """Classify where module should go in new architecture"""
    parts = module_path.split('.')

    # API layer
    if 'api' in parts or 'routes' in parts:
        return 'api'

    # Domain layer
    if 'models' in parts or 'entities' in parts:
        return 'domain'

    # Infrastructure layer
    if any(x in parts for x in ['integrations', 'mcp_servers', 'etl', 'monitoring', 'security']):
        return 'infrastructure'

    # Core layer
    if any(x in parts for x in ['agents', 'services', 'workflows', 'orchestration', 'use_cases']):
        return 'core'

    # Shared layer
    if any(x in parts for x in ['utils', 'prompts', 'constants']):
        return 'shared'

    return 'core'  # default

if __name__ == '__main__':
    print("Analyzing backend dependencies...")
    dependencies = analyze_dependencies()
    generate_dependency_report(dependencies)
    print(f"Found {len(dependencies)} modules with dependencies")
    print("Report saved to reports/backend_dependencies.csv")
```

### 1.2 Create Migration Mapping

```python
# scripts/create_migration_map.py
import os
import json
from pathlib import Path

def create_migration_map():
    """Create detailed file migration mapping"""
    migration_map = {
        'api': {},
        'core': {},
        'domain': {},
        'infrastructure': {},
        'shared': {}
    }

    # API migrations
    migration_map['api'] = {
        'backend/api/': 'api/',
        'backend/fastapi_main.py': 'api/main.py',
        'backend/app/main.py': 'api/app.py',  # merge into main.py
        'backend/app/api_models.py': 'api/models/',
        'backend/presentation/': 'api/serializers/'
    }

    # Core migrations
    migration_map['core'] = {
        'backend/agents/core/': 'core/agents/',
        'backend/agents/specialized/': 'core/use_cases/',
        'backend/orchestration/': 'core/workflows/',
        'backend/application/': 'core/application/',
        'backend/services/': 'core/services/',  # business logic only
        'backend/workflows/': 'core/workflows/'
    }

    # Domain migrations
    migration_map['domain'] = {
        'backend/models/': 'domain/models/',
        'backend/domain/': 'domain/',
        'backend/core/models/': 'domain/models/'
    }

    # Infrastructure migrations
    migration_map['infrastructure'] = {
        'backend/integrations/': 'infrastructure/integrations/',
        'backend/mcp_servers/': 'infrastructure/mcp_servers/',
        'backend/etl/': 'infrastructure/etl/',
        'backend/monitoring/': 'infrastructure/monitoring/',
        'backend/security/': 'infrastructure/security/',
        'backend/database/': 'infrastructure/database/',
        'backend/services/external/': 'infrastructure/services/'
    }

    # Shared migrations
    migration_map['shared'] = {
        'backend/utils/': 'shared/utils/',
        'backend/prompts/': 'shared/prompts/',
        'backend/core/constants.py': 'shared/constants.py',
        'backend/core/config.py': 'shared/config.py',
        'backend/rag/': 'shared/rag/'
    }

    # Save mapping
    os.makedirs('config', exist_ok=True)
    with open('config/migration_map.json', 'w') as f:
        json.dump(migration_map, f, indent=2)

    return migration_map

def generate_file_list(migration_map):
    """Generate detailed file-by-file migration list"""
    file_migrations = []

    for layer, mappings in migration_map.items():
        for old_path, new_path in mappings.items():
            if os.path.exists(old_path):
                if os.path.isdir(old_path):
                    for root, dirs, files in os.walk(old_path):
                        for file in files:
                            if file.endswith('.py'):
                                old_file = os.path.join(root, file)
                                new_file = old_file.replace(old_path, new_path)
                                file_migrations.append({
                                    'old': old_file,
                                    'new': new_file,
                                    'layer': layer
                                })
                else:
                    file_migrations.append({
                        'old': old_path,
                        'new': new_path,
                        'layer': layer
                    })

    with open('config/file_migrations.json', 'w') as f:
        json.dump(file_migrations, f, indent=2)

    return file_migrations

if __name__ == '__main__':
    print("Creating migration map...")
    migration_map = create_migration_map()
    file_migrations = generate_file_list(migration_map)
    print(f"Migration map created with {len(file_migrations)} files to migrate")
```

## Phase 2: Directory Structure Creation

### 2.1 Create New Directory Structure

```bash
#!/bin/bash
# scripts/create_clean_architecture.sh

echo "Creating clean architecture directories..."

# Create main directories
mkdir -p api/{routes,models,dependencies,middleware}
mkdir -p core/{agents,services,use_cases,workflows,ports}
mkdir -p domain/{models,entities,events,value_objects}
mkdir -p infrastructure/{integrations,mcp_servers,etl,monitoring,security,services,database}
mkdir -p shared/{utils,prompts,constants,exceptions}

# Create __init__.py files
find api core domain infrastructure shared -type d -exec touch {}/__init__.py \;

# Create reports directory
mkdir -p reports

echo "Directory structure created successfully"
```

### 2.2 Create Port Interfaces

```python
# core/ports/__init__.py
"""Port interfaces for dependency inversion"""

from .ai_gateway import AIGatewayPort
from .file_storage import FileStoragePort
from .message_queue import MessageQueuePort
from .database import DatabasePort
from .cache import CachePort
from .search import SearchPort

__all__ = [
    'AIGatewayPort',
    'FileStoragePort',
    'MessageQueuePort',
    'DatabasePort',
    'CachePort',
    'SearchPort'
]
```

```python
# core/ports/ai_gateway.py
from typing import Protocol, List, Dict, Any, Optional
from abc import abstractmethod

class AIGatewayPort(Protocol):
    """Port for AI model interactions"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text from AI model"""
        ...

    @abstractmethod
    async def embed(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings for texts"""
        ...

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream text generation"""
        ...
```

```python
# core/ports/database.py
from typing import Protocol, List, Dict, Any, Optional
from abc import abstractmethod

class DatabasePort(Protocol):
    """Port for database operations"""

    @abstractmethod
    async def execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        ...

    @abstractmethod
    async def execute_many(
        self,
        query: str,
        params_list: List[Dict[str, Any]]
    ) -> None:
        """Execute a query with multiple parameter sets"""
        ...

    @abstractmethod
    async def transaction(self):
        """Context manager for database transactions"""
        ...
```
