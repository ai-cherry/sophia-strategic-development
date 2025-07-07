# Backend Clean Architecture Implementation - Part 3

## Phase 5: Testing and Validation

### 5.1 Architecture Validation Script

```python
# scripts/validate_architecture.py
import os
import ast
from pathlib import Path
from typing import List, Dict, Set, Tuple
import json

class ArchitectureValidator:
    def __init__(self):
        self.layers = ['api', 'core', 'domain', 'infrastructure', 'shared']
        self.allowed_dependencies = {
            'domain': ['shared'],
            'core': ['domain', 'shared'],
            'api': ['core', 'shared'],
            'infrastructure': ['core', 'domain', 'shared'],
            'shared': []
        }
        self.violations = []

    def validate_layer_dependencies(self):
        """Validate that layer dependencies follow clean architecture rules"""
        for layer in self.layers:
            layer_path = Path(layer)
            if not layer_path.exists():
                continue

            violations = self.check_layer_imports(layer_path, layer)
            self.violations.extend(violations)

    def check_layer_imports(self, layer_path: Path, layer_name: str) -> List[Dict]:
        """Check imports in a specific layer"""
        violations = []
        allowed = self.allowed_dependencies.get(layer_name, [])

        for py_file in layer_path.rglob('*.py'):
            imports = self.extract_imports(py_file)

            for imp in imports:
                # Check if import is from another layer
                for other_layer in self.layers:
                    if other_layer != layer_name and imp.startswith(other_layer):
                        if other_layer not in allowed:
                            violations.append({
                                'file': str(py_file),
                                'layer': layer_name,
                                'illegal_import': imp,
                                'imported_layer': other_layer,
                                'rule': f"{layer_name} cannot import from {other_layer}"
                            })

        return violations

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract all imports from a Python file"""
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

    def check_no_backend_imports(self):
        """Ensure no files still import from 'backend' package"""
        backend_imports = []

        for layer in self.layers:
            layer_path = Path(layer)
            if not layer_path.exists():
                continue

            for py_file in layer_path.rglob('*.py'):
                with open(py_file, 'r') as f:
                    content = f.read()

                if 'from backend' in content or 'import backend' in content:
                    backend_imports.append(str(py_file))

        if backend_imports:
            self.violations.append({
                'type': 'backend_imports',
                'files': backend_imports,
                'rule': 'No imports from backend package allowed'
            })

    def validate_port_implementations(self):
        """Ensure all ports have implementations"""
        ports_dir = Path('core/ports')
        infra_dir = Path('infrastructure')

        if not ports_dir.exists():
            return

        ports = []
        implementations = []

        # Find all port definitions
        for port_file in ports_dir.glob('*.py'):
            if port_file.name == '__init__.py':
                continue

            with open(port_file, 'r') as f:
                content = f.read()

            # Extract class names that end with 'Port'
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith('Port'):
                    ports.append(node.name)

        # Find implementations
        for impl_file in infra_dir.rglob('*.py'):
            with open(impl_file, 'r') as f:
                content = f.read()

            for port in ports:
                if f'class.*\\({port}\\)' in content:
                    implementations.append(port)

        # Check for missing implementations
        missing = set(ports) - set(implementations)
        if missing:
            self.violations.append({
                'type': 'missing_implementations',
                'ports': list(missing),
                'rule': 'All ports must have implementations'
            })

    def generate_report(self):
        """Generate validation report"""
        report = {
            'timestamp': str(Path.ctime(Path('.'))),
            'violations': self.violations,
            'summary': {
                'total_violations': len(self.violations),
                'layer_violations': len([v for v in self.violations if 'layer' in v]),
                'backend_imports': len([v for v in self.violations if v.get('type') == 'backend_imports']),
                'missing_implementations': len([v for v in self.violations if v.get('type') == 'missing_implementations'])
            }
        }

        with open('reports/architecture_validation.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def run(self):
        """Run all validations"""
        print("Validating clean architecture...")

        self.validate_layer_dependencies()
        self.check_no_backend_imports()
        self.validate_port_implementations()

        report = self.generate_report()

        if self.violations:
            print(f"\n❌ Found {len(self.violations)} architecture violations!")
            for violation in self.violations[:10]:  # Show first 10
                print(f"  - {violation}")
            if len(self.violations) > 10:
                print(f"  ... and {len(self.violations) - 10} more")
        else:
            print("\n✅ Architecture validation passed!")

        print(f"\nFull report saved to reports/architecture_validation.json")

if __name__ == '__main__':
    validator = ArchitectureValidator()
    validator.run()
```

### 5.2 Test Update Script

```python
# scripts/update_test_imports.py
import os
import re
from pathlib import Path

def update_test_imports():
    """Update all test files to use new import structure"""

    test_dirs = ['tests', 'backend/tests']
    import_mappings = {
        'from backend.api': 'from api',
        'from backend.core': 'from core',
        'from backend.domain': 'from domain',
        'from backend.agents': 'from core.agents',
        'from backend.services': 'from core.services',
        'from backend.models': 'from domain.models',
        'from backend.integrations': 'from infrastructure.integrations',
        'from backend.utils': 'from shared.utils',
    }

    updated_files = 0

    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue

        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file

                    with open(file_path, 'r') as f:
                        content = f.read()

                    original = content

                    # Update imports
                    for old_import, new_import in import_mappings.items():
                        content = re.sub(
                            rf'{re.escape(old_import)}',
                            new_import,
                            content
                        )

                    if content != original:
                        with open(file_path, 'w') as f:
                            f.write(content)
                        updated_files += 1
                        print(f"Updated: {file_path}")

    print(f"\nUpdated {updated_files} test files")

if __name__ == '__main__':
    update_test_imports()
```

### 5.3 CI/CD Configuration Updates

```yaml
# .github/workflows/test-clean-architecture.yml
name: Test Clean Architecture

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate-architecture:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install networkx matplotlib
        pip install -r requirements.txt

    - name: Validate architecture
      run: |
        python scripts/validate_architecture.py

    - name: Check for circular dependencies
      run: |
        python scripts/detect_circular_imports.py

    - name: Upload validation report
      uses: actions/upload-artifact@v3
      with:
        name: architecture-validation
        path: reports/architecture_validation.json

  test:
    runs-on: ubuntu-latest
    needs: validate-architecture

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov

    - name: Run tests
      run: |
        pytest -v --cov=api --cov=core --cov=domain --cov=infrastructure --cov=shared

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### 5.4 Docker and Deployment Updates

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code - new structure
COPY api/ ./api/
COPY core/ ./core/
COPY domain/ ./domain/
COPY infrastructure/ ./infrastructure/
COPY shared/ ./shared/

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml updates
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - ENVIRONMENT=prod
    volumes:
      - ./api:/app/api
      - ./core:/app/core
      - ./domain:/app/domain
      - ./infrastructure:/app/infrastructure
      - ./shared:/app/shared
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Phase 6: Configuration and Documentation Updates

### 6.1 Update Configuration Files

```python
# scripts/update_configs.py
import os
import json
import yaml
import re

def update_pyproject_toml():
    """Update pyproject.toml with new structure"""
    pyproject_path = 'pyproject.toml'

    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r') as f:
            content = f.read()

        # Update module paths
        content = re.sub(
            r'backend\.fastapi_main:app',
            'api.main:app',
            content
        )

        # Update package configuration
        content = re.sub(
            r'packages = \["backend"\]',
            'packages = ["api", "core", "domain", "infrastructure", "shared"]',
            content
        )

        with open(pyproject_path, 'w') as f:
            f.write(content)

        print("Updated pyproject.toml")

def update_ruff_config():
    """Update ruff configuration"""
    ruff_config = {
        "include": ["api/**/*.py", "core/**/*.py", "domain/**/*.py",
                   "infrastructure/**/*.py", "shared/**/*.py"],
        "exclude": ["backend/**/*.py"],  # Exclude old backend
        "line-length": 88,
        "select": ["E", "F", "I"],
        "ignore": ["E501"],
        "per-file-ignores": {
            "api/__init__.py": ["F401"],
            "core/__init__.py": ["F401"],
            "shared/__init__.py": ["F401"]
        }
    }

    with open('.ruff.toml', 'w') as f:
        for key, value in ruff_config.items():
            if isinstance(value, list):
                f.write(f'{key} = {json.dumps(value)}\n')
            elif isinstance(value, dict):
                f.write(f'\n[{key}]\n')
                for k, v in value.items():
                    f.write(f'"{k}" = {json.dumps(v)}\n')
            else:
                f.write(f'{key} = {value}\n')

    print("Updated .ruff.toml")

def update_vscode_settings():
    """Update VS Code settings"""
    vscode_dir = '.vscode'
    os.makedirs(vscode_dir, exist_ok=True)

    settings = {
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": False,
        "python.linting.flake8Enabled": False,
        "python.formatting.provider": "black",
        "python.analysis.extraPaths": [
            "${workspaceFolder}"
        ],
        "python.analysis.importFormat": "absolute",
        "python.autoComplete.extraPaths": [
            "${workspaceFolder}"
        ]
    }

    with open(f'{vscode_dir}/settings.json', 'w') as f:
        json.dump(settings, f, indent=2)

    print("Updated VS Code settings")

if __name__ == '__main__':
    update_pyproject_toml()
    update_ruff_config()
    update_vscode_settings()
```

### 6.2 Documentation Generator

```python
# scripts/generate_architecture_docs.py
import os
from pathlib import Path
import ast

def generate_layer_documentation():
    """Generate documentation for each architectural layer"""

    layers = {
        'api': 'API Layer - HTTP endpoints and request/response handling',
        'core': 'Core Layer - Business logic and use cases',
        'domain': 'Domain Layer - Entities and domain models',
        'infrastructure': 'Infrastructure Layer - External integrations',
        'shared': 'Shared Layer - Common utilities and constants'
    }

    doc_content = """# Sophia AI Clean Architecture Documentation

## Overview

The Sophia AI backend follows Clean Architecture principles with clear separation of concerns and dependency rules.

## Layers

"""

    for layer, description in layers.items():
        doc_content += f"### {layer.capitalize()} Layer\n\n"
        doc_content += f"{description}\n\n"

        # List modules in layer
        layer_path = Path(layer)
        if layer_path.exists():
            doc_content += "**Modules:**\n"
            for module in sorted(layer_path.glob('**/*.py')):
                if module.name != '__init__.py':
                    module_path = str(module).replace('/', '.')
                    doc_content += f"- `{module_path}`\n"
            doc_content += "\n"

    # Add dependency rules
    doc_content += """## Dependency Rules

1. **Domain Layer** - No dependencies (pure Python)
2. **Core Layer** - Depends on Domain and Shared only
3. **API Layer** - Depends on Core and Shared (never Infrastructure)
4. **Infrastructure Layer** - Depends on Core, Domain, and Shared
5. **Shared Layer** - No dependencies on other layers

## Import Examples

```python
# ✅ Good - API imports from Core
from core.use_cases.chat_orchestration import ChatOrchestrator

# ✅ Good - Core imports from Domain
from domain.models.user import User

# ❌ Bad - Core imports from API
from api.routes.chat_routes import router  # Violation!

# ❌ Bad - Domain imports from Core
from core.services.user_service import UserService  # Violation!
```
"""

    with open('docs/CLEAN_ARCHITECTURE.md', 'w') as f:
        f.write(doc_content)

    print("Generated architecture documentation")

if __name__ == '__main__':
    generate_layer_documentation()
```

## Phase 7: Execution Commands

### 7.1 Complete Migration Script

```bash
#!/bin/bash
# scripts/execute_clean_architecture_migration.sh

set -e

echo "🏗️ Starting Sophia AI Clean Architecture Migration..."

# Step 1: Create reports directory
mkdir -p reports

# Step 2: Analyze current dependencies
echo "📊 Analyzing current dependencies..."
python scripts/analyze_backend_dependencies.py

# Step 3: Create migration map
echo "🗺️ Creating migration map..."
python scripts/create_migration_map.py

# Step 4: Create new directory structure
echo "📁 Creating clean architecture directories..."
bash scripts/create_clean_architecture.sh

# Step 5: Split service layer
echo "🔀 Analyzing service layer split..."
python scripts/split_service_layer.py

# Step 6: Execute migration (dry run first)
echo "🚚 Running migration (dry run)..."
python scripts/migrate_backend_files.py

read -p "Review dry run results. Execute actual migration? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python scripts/migrate_backend_files.py --execute
fi

# Step 7: Update all imports
echo "📝 Updating import statements..."
python scripts/update_all_imports.py

# Step 8: Update test imports
echo "🧪 Updating test imports..."
python scripts/update_test_imports.py

# Step 9: Validate architecture
echo "✅ Validating clean architecture..."
python scripts/validate_architecture.py

# Step 10: Update configurations
echo "⚙️ Updating configuration files..."
python scripts/update_configs.py

# Step 11: Generate documentation
echo "📚 Generating architecture documentation..."
python scripts/generate_architecture_docs.py

# Step 12: Run tests
echo "🧪 Running tests..."
pytest -v

echo "✨ Clean Architecture migration complete!"
echo "📊 Check reports/ directory for detailed reports"
```

## Summary

This comprehensive guide provides everything needed to refactor the Sophia AI backend into a clean architecture. The migration:

1. **Preserves all functionality** - Uses git mv to maintain history
2. **Automates the process** - Scripts handle file moves and import updates
3. **Validates the result** - Architecture validation ensures compliance
4. **Updates all configurations** - CI/CD, Docker, and IDE settings
5. **Provides clear documentation** - Auto-generated architecture docs

The new structure provides:
- Clear separation of concerns
- Testable business logic
- Swappable infrastructure components
- Maintainable codebase
- Scalable architecture

Execute the migration with:
```bash
chmod +x scripts/execute_clean_architecture_migration.sh
./scripts/execute_clean_architecture_migration.sh
```
