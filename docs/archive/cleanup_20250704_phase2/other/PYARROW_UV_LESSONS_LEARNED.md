# PyArrow UV Dependency Management: Lessons Learned

## Executive Summary

The PyArrow dependency issue we encountered provides valuable insights into dependency management with UV package manager, particularly regarding version constraints and platform-specific compatibility. This document captures key learnings for future reference.

## The Issue

### Symptoms
- `AttributeError: module 'pyarrow' has no attribute '__version__'`
- Snowflake warning: "You have an incompatible version of 'pyarrow' installed (20.0.0), please install a version that adheres to: 'pyarrow<19.0.0'"

### Root Cause
1. UV installed PyArrow 20.0.0 (latest) by default
2. Snowflake-connector-python requires PyArrow < 19.0.0
3. The version conflict wasn't caught during UV installation

## Key Findings

### 1. UV Lock File Analysis
From `uv.lock`:
```
name = "pyarrow"
version = "20.0.0"
```
UV locked to the latest version (20.0.0) despite Snowflake's constraint.

### 2. Missing Explicit Constraints
In `pyproject.toml`:
- PyArrow is **not explicitly listed** as a dependency
- It's installed as a transitive dependency of pandas
- No version constraint specified

### 3. Dependency Chain
```
sophia-ai → pandas → pyarrow (unconstrained)
sophia-ai → snowflake-connector-python → pyarrow (<19.0.0)
```

## Lessons Learned

### 1. **Always Pin Critical Dependencies**
Even if a package is a transitive dependency, if it's critical to your application (like PyArrow for data processing), explicitly pin it:

```toml
dependencies = [
    "pandas>=2.2.3",
    "pyarrow>=18.0.0,<19.0.0",  # Explicit constraint for Snowflake compatibility
    "snowflake-connector-python>=3.6.0",
]
```

### 2. **UV Resolution Behavior**
- UV resolves to the highest compatible version by default
- It may not always catch all constraint conflicts, especially with extras
- The warning from Snowflake came at runtime, not install time

### 3. **Platform-Specific Issues**
The PyArrow troubleshooting guide highlighted macOS-specific issues:
- UV may fail to recognize Universal wheels in conda environments
- May attempt source builds instead of using wheels
- Solution: Use `--no-build` flag or pip as fallback

### 4. **Version Compatibility Matrix**
Document critical version constraints:
| Package | Our Version | Constraint | Reason |
|---------|-------------|------------|---------|
| pyarrow | 18.1.0 | <19.0.0 | Snowflake compatibility |
| pandas | 2.3.0 | >=2.2.3 | Features needed |
| snowflake-connector-python | 3.16.0 | >=3.6.0 | API requirements |

### 5. **Testing Strategy**
- Always test with actual imports, not just installation success
- Include version compatibility tests in CI/CD
- Test transitive dependencies explicitly

## Recommended Actions

### 1. Update pyproject.toml
```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "pyarrow>=18.0.0,<19.0.0",  # Pin for Snowflake compatibility
    # ... rest of dependencies ...
]
```

### 2. Create Dependency Validation Script
```python
# scripts/validate_dependencies.py
import importlib
import sys

CRITICAL_DEPS = {
    "pyarrow": {"min": "18.0.0", "max": "19.0.0"},
    "pandas": {"min": "2.2.3"},
    "snowflake.connector": {"min": "3.6.0"}
}

def validate_versions():
    for module, constraints in CRITICAL_DEPS.items():
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, "__version__", "unknown")
            print(f"{module}: {version}")
            # Add version comparison logic
        except ImportError:
            print(f"{module}: NOT INSTALLED")
            sys.exit(1)
```

### 3. UV Best Practices
1. **Lock file management**:
   - Regularly update `uv.lock` with `uv lock --upgrade`
   - Review changes before committing
   - Test after lock file updates

2. **Installation flags**:
   ```bash
   # For problematic packages on macOS
   uv pip install --no-build pyarrow

   # Force resolution refresh
   uv pip install --refresh pyarrow
   ```

3. **Debugging**:
   ```bash
   # Check what UV thinks is installed
   uv pip list | grep pyarrow

   # Show dependency tree
   uv pip tree
   ```

### 4. CI/CD Integration
Add dependency validation to CI:
```yaml
- name: Validate Dependencies
  run: |
    uv pip install -e .
    python scripts/validate_dependencies.py
```

## Platform-Specific Considerations

### macOS with UV
Based on the PyArrow troubleshooting guide:
1. Set deployment target: `export MACOSX_DEPLOYMENT_TARGET=11.0`
2. Use `--no-build` flag for binary packages
3. Consider using pip for specific packages if UV fails

### Docker/Linux
- Generally more stable with UV
- Ensure base images have required system libraries
- Pin base image versions

## Monitoring and Maintenance

### 1. Regular Audits
- Monthly dependency updates with testing
- Quarterly review of version constraints
- Track upstream breaking changes

### 2. Documentation
- Maintain a DEPENDENCIES.md with rationale for constraints
- Document any workarounds or platform-specific issues
- Keep troubleshooting guides updated

### 3. Team Communication
- Announce dependency updates in team channels
- Document resolution steps for common issues
- Share learnings from dependency conflicts

## Conclusion

The PyArrow issue highlighted the importance of:
1. Explicit dependency management
2. Understanding UV's resolution behavior
3. Testing beyond installation success
4. Maintaining compatibility matrices
5. Platform-specific considerations

By implementing these lessons, we can prevent similar issues and maintain a more stable dependency environment.

## Quick Reference

### Fix PyArrow Issue
```bash
# Option 1: Use pip for PyArrow
pip install "pyarrow<19.0.0"

# Option 2: UV with constraints
uv pip install "pyarrow<19.0.0"

# Option 3: Update pyproject.toml and sync
# Add: "pyarrow>=18.0.0,<19.0.0"
uv pip sync
```

### Verify Installation
```python
import pyarrow
import snowflake.connector
print(f"PyArrow: {pyarrow.__version__}")
print(f"Snowflake: {snowflake.connector.__version__}")
```
