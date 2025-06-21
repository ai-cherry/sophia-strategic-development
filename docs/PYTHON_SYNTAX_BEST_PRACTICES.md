# Python Syntax Best Practices for Sophia AI

This guide documents common Python syntax issues encountered in the Sophia AI codebase and provides best practices to avoid them.

## Common Issues and Solutions

### 1. Docstring Formatting

**Issue**: Docstrings concatenated with following code without proper spacing.

```python
# ❌ Bad
def my_function():
    """This is a docstring."""self.value = 10

# ✅ Good
def my_function():
    """This is a docstring."""

    self.value = 10
```

**Best Practice**: Always leave a blank line after docstrings before the first line of code.

### 2. Module-Level Docstrings and Imports

**Issue**: Module docstring immediately followed by import statements.

```python
# ❌ Bad
"""Module docstring."""
import os

# ✅ Good
"""Module docstring."""

import os
```

**Best Practice**: Always leave a blank line between module docstrings and import statements.

### 3. Trailing Periods on Statements

**Issue**: Unnecessary periods at the end of Python statements.

```python
# ❌ Bad
self.cache.clear().
result = calculate_value().

# ✅ Good
self.cache.clear()
result = calculate_value()
```

**Best Practice**: Python statements don't end with periods. Remove any trailing periods.

### 4. Try Blocks Without Handlers

**Issue**: Try blocks without except or finally clauses.

```python
# ❌ Bad
try:
    risky_operation()
# Missing except or finally

# ✅ Good
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
```

**Best Practice**: Every try block must have at least one except or finally clause.

### 5. Multiline String Formatting

**Issue**: Inconsistent indentation in multiline strings.

```python
# ❌ Bad
query = """
SELECT * FROM table
WHERE condition = true
    AND other = false
"""

# ✅ Good
query = """
    SELECT * FROM table
    WHERE condition = true
    AND other = false
"""
```

**Best Practice**: Maintain consistent indentation within multiline strings.

## Automated Tools

### Python Syntax Validator

We provide a custom syntax validator that can automatically detect and fix common issues:

```bash
# Check for issues
python scripts/python_syntax_validator.py

# Auto-fix issues
python scripts/python_syntax_validator.py --fix

# Check specific file
python scripts/python_syntax_validator.py backend/core/config.py

# Output as JSON
python scripts/python_syntax_validator.py --json
```

### Pre-commit Hook

A pre-commit hook is available to catch syntax errors before committing:

```bash
# Install the pre-commit hook
cp .githooks/pre-commit-python-syntax .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook will:
- Block commits with syntax errors
- Show warnings for style issues (non-blocking)
- Suggest running the auto-fix tool

## IDE Configuration

### VS Code Settings

Add these settings to your `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.rulers": [88],
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

### PyCharm Settings

1. Go to Settings → Editor → Code Style → Python
2. Set "Hard wrap at" to 88 columns
3. Enable "Add blank line after docstring"
4. Enable "Optimize imports on save"

## Code Review Checklist

When reviewing Python code, check for:

- [ ] Proper spacing after docstrings
- [ ] No trailing periods on statements
- [ ] All try blocks have except/finally
- [ ] Consistent multiline string indentation
- [ ] Proper import organization and spacing
- [ ] No syntax errors from `python -m py_compile`

## Common Patterns to Avoid

### 1. Concatenated Statements

```python
# ❌ Avoid
"""Docstring"""return value
self.method()another_call()

# ✅ Prefer
"""Docstring"""

return value

self.method()
another_call()
```

### 2. Inconsistent Indentation

```python
# ❌ Avoid
def function():
    if condition:
        do_something()
      do_another()  # Wrong indentation

# ✅ Prefer
def function():
    if condition:
        do_something()
        do_another()
```

### 3. Missing Error Handling

```python
# ❌ Avoid
try:
    risky_operation()
    # No error handling

# ✅ Prefer
try:
    risky_operation()
except SpecificException as e:
    logger.error(f"Expected error: {e}")
    # Handle appropriately
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

## Automated Fixes

The `python_syntax_validator.py` script can automatically fix:

1. **Docstring spacing**: Adds blank lines after docstrings
2. **Import spacing**: Adds blank lines after module docstrings
3. **Trailing periods**: Removes unnecessary periods
4. **Missing except blocks**: Adds generic exception handlers
5. **Basic indentation issues**: Fixes common indentation problems

## Integration with CI/CD

Add this to your GitHub Actions workflow:

```yaml
- name: Check Python Syntax
  run: |
    python scripts/python_syntax_validator.py --severity error
```

This will fail the build if any syntax errors are found.

## Best Practices Summary

1. **Always validate syntax** before committing
2. **Use automated tools** to catch common issues
3. **Configure your IDE** for Python best practices
4. **Follow PEP 8** with Black formatter (88 char limit)
5. **Write comprehensive docstrings** with proper formatting
6. **Handle all exceptions** appropriately
7. **Maintain consistent style** across the codebase

## Troubleshooting

### Issue: Pre-commit hook not running
```bash
# Make sure it's executable
chmod +x .git/hooks/pre-commit

# Test manually
python .githooks/pre-commit-python-syntax
```

### Issue: Auto-fix not working
```bash
# Check for syntax errors first
python -m py_compile your_file.py

# Run with verbose output
python scripts/python_syntax_validator.py --fix -v
```

### Issue: False positives
If the validator reports false positives, you can:
1. Update the patterns in `python_syntax_validator.py`
2. Add file-specific exceptions
3. Report the issue for improvement

## Contributing

When adding new syntax checks:
1. Add the pattern to `DOCSTRING_PATTERNS` or create a new category
2. Add a fix in the `fix_file` method
3. Add test cases
4. Update this documentation

Remember: Clean, consistent code is easier to maintain and debug!
