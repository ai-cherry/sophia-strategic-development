# Conflict Resolution Strategy

## Overview

This document provides specific solutions for all identified conflicts and potential issues during the MCP V2+ migration. Each conflict type includes detection methods and resolution procedures.

## 1. Import Conflict Resolution

### Problem: Cross-Version Imports
V1 and V2 servers may import from each other causing circular dependencies.

### Detection Script

Create `scripts/migration/detect_import_conflicts.py`:

```python
#!/usr/bin/env python3
"""
Detect and resolve import conflicts between V1 and V2 servers
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

class ImportConflictDetector:
    def __init__(self):
        self.v1_path = Path("mcp-servers")
        self.v2_path = Path("infrastructure/mcp_servers")
        self.conflicts = []
        self.import_graph = {}

    def scan_imports(self) -> Dict[str, List[str]]:
        """Build complete import graph"""
        import_map = {}

        # Scan all Python files
        for py_file in Path(".").rglob("*.py"):
            if any(skip in str(py_file) for skip in [".venv", "__pycache__", "test"]):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)

                import_map[str(py_file)] = imports

            except Exception as e:
                print(f"Error parsing {py_file}: {e}")

        return import_map

    def detect_cross_imports(self, import_map: Dict[str, List[str]]) -> List[Dict]:
        """Detect imports crossing V1/V2 boundary"""
        conflicts = []

        for file_path, imports in import_map.items():
            is_v1 = "mcp-servers" in file_path
            is_v2 = "infrastructure/mcp_servers" in file_path

            if not (is_v1 or is_v2):
                continue

            for imp in imports:
                # Check if V1 imports from V2
                if is_v1 and ("infrastructure.mcp_servers" in imp or "mcp_servers" in imp):
                    conflicts.append({
                        "file": file_path,
                        "type": "v1_imports_v2",
                        "import": imp,
                        "severity": "high"
                    })

                # Check if V2 imports from V1
                elif is_v2 and "mcp-servers" in imp:
                    conflicts.append({
                        "file": file_path,
                        "type": "v2_imports_v1",
                        "import": imp,
                        "severity": "high"
                    })

        return conflicts

    def generate_fixes(self, conflicts: List[Dict]) -> List[Dict]:
        """Generate fix recommendations"""
        fixes = []

        for conflict in conflicts:
            if conflict["type"] == "v1_imports_v2":
                fixes.append({
                    "file": conflict["file"],
                    "action": "remove_import",
                    "old": conflict["import"],
                    "new": "# TODO: Remove cross-version import",
                    "migration_note": "V1 server should not depend on V2"
                })
            elif conflict["type"] == "v2_imports_v1":
                # Suggest using shared library
                fixes.append({
                    "file": conflict["file"],
                    "action": "use_shared_lib",
                    "old": conflict["import"],
                    "new": self._suggest_shared_import(conflict["import"]),
                    "migration_note": "Use shared library instead of V1 import"
                })

        return fixes

    def _suggest_shared_import(self, import_str: str) -> str:
        """Suggest shared library import"""
        # Map common V1 imports to shared equivalents
        mappings = {
            "mcp-servers.utils": "backend.core.utils",
            "mcp-servers.base": "infrastructure.mcp_servers.base.standardized_mcp_server",
            "mcp-servers.config": "backend.core.auto_esc_config"
        }

        for old, new in mappings.items():
            if old in import_str:
                return import_str.replace(old, new)

        return f"backend.core.{import_str.split('.')[-1]}"

def main():
    """Run import conflict detection"""
    print("🔍 Detecting import conflicts...")

    detector = ImportConflictDetector()
    import_map = detector.scan_imports()
    conflicts = detector.detect_cross_imports(import_map)
    fixes = detector.generate_fixes(conflicts)

    # Save report
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    import json
    with open(output_dir / "import_conflicts.json", "w") as f:
        json.dump({
            "conflicts": conflicts,
            "fixes": fixes,
            "total_files_scanned": len(import_map),
            "total_conflicts": len(conflicts)
        }, f, indent=2)

    # Print summary
    print(f"\n📊 Import Conflict Summary:")
    print(f"  Files scanned: {len(import_map)}")
    print(f"  Conflicts found: {len(conflicts)}")

    if conflicts:
        print("\n⚠️  Conflicts detected:")
        for conflict in conflicts[:5]:
            print(f"  {conflict['file']}: {conflict['import']}")

    print(f"\n✅ Report saved to: reports/import_conflicts.json")

if __name__ == "__main__":
    main()
```

### Resolution Procedures

1. **Immediate Fixes** (for blocking issues):
```python
# backend/core/shared_imports.py
"""
Shared imports for both V1 and V2 servers
Prevents cross-version dependencies
"""

from backend.core.auto_esc_config import get_config_value
from backend.core.cache_manager import get_cache
from backend.core.monitoring import setup_prometheus

# Re-export common utilities
__all__ = ['get_config_value', 'get_cache', 'setup_prometheus']
```

2. **Import Rewriter** (automated fix):
```python
# scripts/migration/fix_imports.py
#!/usr/bin/env python3
"""
Automatically fix import conflicts
"""

import re
from pathlib import Path

IMPORT_MAPPINGS = {
    # V1 → Shared mappings
    r'from mcp-servers\.utils import (.*)': r'from backend.core.utils import \1',
    r'from mcp-servers\.config import (.*)': r'from backend.core.auto_esc_config import \1',
    r'import mcp-servers\.(.*)': r'import backend.core.\1',
}

def fix_imports(file_path: Path):
    """Fix imports in a single file"""
    content = file_path.read_text()
    original = content

    for pattern, replacement in IMPORT_MAPPINGS.items():
        content = re.sub(pattern, replacement, content)

    if content != original:
        file_path.write_text(content)
        print(f"✅ Fixed imports in {file_path}")

def main():
    """Fix all import conflicts"""
    import json

    # Load conflicts from detection
    with open("reports/import_conflicts.json") as f:
        data = json.load(f)

    for conflict in data["conflicts"]:
        fix_imports(Path(conflict["file"]))

if __name__ == "__main__":
    main()
```

## 2. Port Conflict Resolution

### Problem: Multiple servers on same port
Legacy and new servers may claim the same port.

### Resolution Strategy

1. **Port Reservation System**:
```python
# backend/core/ports/port_manager.py
"""
Central port management for MCP servers
"""

import json
from pathlib import Path
from typing import Optional

class PortManager:
    def __init__(self):
        self.config_path = Path("config/consolidated_mcp_ports.json")
        self.ports = self._load_ports()

    def _load_ports(self) -> dict:
        """Load current port allocations"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}

    def claim_port(self, server_name: str, requested_port: int) -> int:
        """Claim a port for a server"""
        # Check if port is available
        if requested_port in self.ports.values():
            # Find who owns it
            owner = [s for s, p in self.ports.items() if p == requested_port][0]
            if owner != server_name:
                raise ValueError(f"Port {requested_port} already claimed by {owner}")

        self.ports[server_name] = requested_port
        self._save_ports()
        return requested_port

    def get_port(self, server_name: str) -> Optional[int]:
        """Get assigned port for server"""
        return self.ports.get(server_name)

    def _save_ports(self):
        """Save port allocations"""
        with open(self.config_path, "w") as f:
            json.dump(self.ports, f, indent=2, sort_keys=True)

# Usage in server
port_manager = PortManager()
port = port_manager.claim_port("snowflake_v2", 9001)
```

2. **Runtime Port Validation**:
```python
# infrastructure/mcp_servers/base/port_validator.py
"""
Runtime port validation for MCP servers
"""

import socket
from contextlib import closing

def is_port_available(port: int) -> bool:
    """Check if port is available"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex(('localhost', port)) != 0

def find_available_port(start: int = 9000, end: int = 9999) -> int:
    """Find next available port in range"""
    for port in range(start, end):
        if is_port_available(port):
            return port
    raise RuntimeError(f"No available ports in range {start}-{end}")
```

## 3. Dependency Version Conflicts

### Problem: Different FastAPI/Pydantic versions
V1 uses FastAPI 0.68, V2 requires FastAPI 0.100+

### Resolution Strategy

1. **Version Pinning**:
```toml
# pyproject.toml
[project]
dependencies = [
    "fastapi>=0.111.0,<0.112.0",  # Force latest
    "pydantic>=2.6.0,<3.0.0",      # V2 only
    "pydantic-settings>=2.0.0",     # New settings
    "uvicorn[standard]>=0.27.0",
]

[tool.uv]
upgrade-package = [
    "fastapi",  # Always upgrade these
    "pydantic",
]
```

2. **Compatibility Layer**:
```python
# backend/core/compat/fastapi_compat.py
"""
FastAPI compatibility layer for migration
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

def create_app_compat(lifespan=None, **kwargs):
    """Create FastAPI app with compatibility"""
    # Remove deprecated parameters
    kwargs.pop('on_startup', None)
    kwargs.pop('on_shutdown', None)

    # Use lifespan for all apps
    if not lifespan:
        @asynccontextmanager
        async def default_lifespan(app: FastAPI):
            # Startup
            yield
            # Shutdown

        lifespan = default_lifespan

    return FastAPI(lifespan=lifespan, **kwargs)
```

## 4. Secret Management Conflicts

### Problem: Mixed .env files and ESC usage
Some servers use .env files, others use Pulumi ESC.

### Resolution Strategy

1. **Unified Secret Access**:
```python
# backend/core/secrets/unified_secrets.py
"""
Unified secret access - ESC only, no .env files
"""

from backend.core.auto_esc_config import get_config_value
import os
import warnings

class UnifiedSecrets:
    @staticmethod
    def get(key: str, default=None):
        """Get secret - ESC first, env fallback with warning"""
        # Try ESC first
        try:
            value = get_config_value(key)
            if value:
                return value
        except:
            pass

        # Fallback to env with warning
        if key in os.environ:
            warnings.warn(
                f"Secret '{key}' loaded from environment. "
                f"Should be in Pulumi ESC!",
                DeprecationWarning
            )
            return os.environ[key]

        return default

    @staticmethod
    def require(key: str):
        """Get required secret"""
        value = UnifiedSecrets.get(key)
        if not value:
            raise ValueError(f"Required secret '{key}' not found in ESC or env")
        return value

# Usage
secrets = UnifiedSecrets()
api_key = secrets.require("OPENAI_API_KEY")
```

2. **Migration Helper**:
```python
# scripts/migration/migrate_env_to_esc.py
#!/usr/bin/env python3
"""
Migrate .env files to Pulumi ESC
"""

from pathlib import Path
import re

def extract_env_vars(env_file: Path) -> dict:
    """Extract variables from .env file"""
    vars = {}

    if not env_file.exists():
        return vars

    content = env_file.read_text()
    for line in content.split('\n'):
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            vars[key.strip()] = value.strip().strip('"\'')

    return vars

def generate_esc_commands(vars: dict) -> list:
    """Generate Pulumi ESC commands"""
    commands = []

    for key, value in vars.items():
        # Determine ESC path based on key
        if 'SNOWFLAKE' in key:
            path = f"sophia.data.{key.lower()}"
        elif 'OPENAI' in key or 'ANTHROPIC' in key:
            path = f"sophia.ai.{key.lower()}"
        else:
            path = f"sophia.services.{key.lower()}"

        commands.append(f"pulumi env set {path} '{value}' --secret")

    return commands

def main():
    """Migrate all .env files to ESC"""
    env_files = list(Path(".").rglob(".env*"))

    all_commands = []
    for env_file in env_files:
        print(f"Processing {env_file}...")
        vars = extract_env_vars(env_file)
        commands = generate_esc_commands(vars)
        all_commands.extend(commands)

    # Save commands
    with open("migrate_secrets.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# Migrate secrets to Pulumi ESC\n\n")
        for cmd in all_commands:
            f.write(f"{cmd}\n")

    print(f"\n✅ Generated {len(all_commands)} ESC commands")
    print("Run: bash migrate_secrets.sh")

if __name__ == "__main__":
    main()
```

## 5. Testing Conflicts

### Problem: Tests importing from wrong locations
Tests may break when servers are migrated.

### Resolution Strategy

1. **Test Fixtures**:
```python
# backend/tests/fixtures/mcp_fixtures.py
"""
Shared test fixtures for MCP servers
"""

import pytest
from httpx import AsyncClient
from typing import AsyncGenerator

@pytest.fixture
async def test_client(server_class) -> AsyncGenerator[AsyncClient, None]:
    """Create test client for any MCP server"""
    app = server_class().app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_esc(monkeypatch):
    """Mock ESC for testing"""
    mock_values = {
        "snowflake_credentials": {"account": "test"},
        "openai_api_key": "test-key"
    }

    def mock_get_config_value(key, default=None):
        return mock_values.get(key, default)

    monkeypatch.setattr(
        "backend.core.auto_esc_config.get_config_value",
        mock_get_config_value
    )
```

2. **Test Migration Helper**:
```python
# scripts/migration/migrate_tests.py
#!/usr/bin/env python3
"""
Migrate tests to use new imports
"""

import re
from pathlib import Path

TEST_IMPORT_MAPPINGS = {
    # Old test import → New test import
    r'from mcp-servers\.(\w+)\.test': r'from infrastructure.mcp_servers.\1.tests.test',
    r'from tests\.(\w+)_test': r'from backend.tests.mcp.\1_test',
}

def migrate_test_file(test_file: Path):
    """Migrate single test file"""
    content = test_file.read_text()
    original = content

    for pattern, replacement in TEST_IMPORT_MAPPINGS.items():
        content = re.sub(pattern, replacement, content)

    if content != original:
        test_file.write_text(content)
        print(f"✅ Migrated {test_file}")

def main():
    """Migrate all test files"""
    for test_file in Path(".").rglob("test_*.py"):
        migrate_test_file(test_file)

if __name__ == "__main__":
    main()
```

## 6. CI/CD Pipeline Conflicts

### Problem: Multiple CI workflows for same purpose
V1 and V2 may have conflicting CI definitions.

### Resolution Strategy

Create unified CI workflow:

```yaml
# .github/workflows/mcp_unified_ci.yml
name: MCP Unified CI

on:
  push:
    paths:
      - 'mcp-servers/**'
      - 'infrastructure/mcp_servers/**'
      - 'backend/**'
  pull_request:

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - id: set-matrix
        run: |
          # Detect which servers changed
          SERVERS=$(python scripts/ci/detect_changed_servers.py)
          echo "matrix=${SERVERS}" >> $GITHUB_OUTPUT

  test-server:
    needs: detect-changes
    strategy:
      matrix: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install UV
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: |
          uv run pytest ${{ matrix.server_path }}/tests -v

      - name: Build Docker image
        run: |
          docker build -t test-${{ matrix.server_name }} \
            -f ${{ matrix.server_path }}/Dockerfile \
            ${{ matrix.server_path }}
```

## Summary

This conflict resolution strategy provides:

1. **Automated detection** of all conflict types
2. **Specific resolution procedures** for each conflict
3. **Migration scripts** to fix issues systematically
4. **Validation procedures** to ensure fixes work

Next: [V2+ Template Architecture](./03_V2_TEMPLATE_ARCHITECTURE.md)
