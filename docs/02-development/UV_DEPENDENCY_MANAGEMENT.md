# UV Dependency Management Guide

## Overview

Sophia AI uses **UV + pyproject.toml** as the single source of truth for all Python dependencies. This modern approach eliminates the need for multiple `requirements.txt` files and provides faster, more reliable dependency resolution.

## Quick Start

### Installing Dependencies

```bash
# Install UV (if not already installed)
pip install uv

# Install all runtime dependencies
uv pip install .

# Install with development dependencies
uv pip install .[dev]

# Install with all optional dependencies
uv pip install .[dev,docs]
```

### Adding New Dependencies

```bash
# Add a runtime dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Add with specific version
uv add "fastapi>=0.115.0"
```

## Project Structure

All dependencies are defined in `pyproject.toml`:

```toml
[project]
dependencies = [
    # Runtime dependencies
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    # ... more runtime deps
]

[project.optional-dependencies]
dev = [
    # Development dependencies
    "pytest>=8.0.0",
    "black>=24.0.0",
    # ... more dev deps
]
docs = [
    # Documentation dependencies
    "mkdocs>=1.5.3",
    "sphinx>=7.2.6",
]
```

## Docker Integration

All Dockerfiles use UV for dependency installation:

```dockerfile
FROM python:3.11-slim as dependencies
COPY pyproject.toml* ./
RUN pip install --no-cache-dir uv && \
    uv pip install --system .
```

## CI/CD Integration

GitHub Actions workflows use UV:

```yaml
- name: Install dependencies
  run: |
    pip install uv
    uv pip install .[dev]
```

## Benefits

1. **Speed**: UV is 10-100x faster than pip
2. **Reliability**: Consistent dependency resolution
3. **Simplicity**: Single source of truth
4. **Modern**: Follows Python packaging standards
5. **Lock Files**: Automatic `uv.lock` generation

## Migration from requirements.txt

The migration has been completed. All `requirements*.txt` files have been:
- Consolidated into `pyproject.toml`
- Categorized (runtime vs dev vs docs)
- Cleaned of invalid/local imports
- Removed from the repository

## Common Commands

```bash
# Update all dependencies
uv pip compile --upgrade

# Check for outdated packages
uv pip list --outdated

# Generate lock file
uv pip compile

# Install in editable mode
uv pip install -e .

# Clean unused dependencies
uv pip sync
```

## Troubleshooting

### Issue: Package not found
```bash
# Clear UV cache
uv cache clean

# Reinstall
uv pip install . --force-reinstall
```

### Issue: Version conflicts
```bash
# Show dependency tree
uv pip tree

# Check specific package
uv pip show <package>
```

## Best Practices

1. **Always use UV** for dependency management
2. **Never create requirements.txt** files
3. **Categorize dependencies** appropriately (runtime vs dev)
4. **Pin major versions** for stability
5. **Update regularly** but test thoroughly

## Environment Variables

UV respects standard pip environment variables:
- `UV_INDEX_URL`: Custom package index
- `UV_EXTRA_INDEX_URL`: Additional indexes
- `UV_CACHE_DIR`: Cache location

## References

- [UV Documentation](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org)
- [PEP 621](https://peps.python.org/pep-0621/) - pyproject.toml specification
