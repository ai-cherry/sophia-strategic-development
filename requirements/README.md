# Requirements Directory

This directory contains organized dependency files for the Sophia AI platform.

## File Structure

- **`base.txt`** - Core application dependencies required for all environments
- **`development.txt`** - Development tools, testing frameworks, and code quality tools
- **`production.txt`** - Production-optimized dependencies with performance enhancements
- **`cleanup.txt`** - Dependencies for technical debt cleanup and validation scripts

## Usage

### Development Environment
```bash
pip install -r requirements/development.txt
```

### Production Environment
```bash
pip install -r requirements/production.txt
```

### Cleanup and Validation Scripts
```bash
pip install -r requirements/cleanup.txt
```

## Migration from Legacy Files

- `requirements.txt` → `requirements/base.txt` (core dependencies)
- `requirements-phase2.txt` → `requirements/cleanup.txt` (cleanup tools)
- `requirements.docker.txt` → Still used for Docker builds

## Workflow Integration

GitHub Actions workflows use these files with dependency caching for improved performance:

```yaml
- name: Cache Dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements/*.txt') }}
```

## Maintenance

- Keep `base.txt` minimal with only essential dependencies
- Add development tools only to `development.txt`
- Use production optimizations in `production.txt`
- Update security patches across all files regularly

