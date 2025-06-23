---
title: Python Syntax Best Practices for Sophia AI
description: This guide documents common Python syntax issues encountered in the Sophia AI codebase and provides best practices to avoid them.
tags: 
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Python Syntax Best Practices for Sophia AI


## Table of Contents

- [Common Issues and Solutions](#common-issues-and-solutions)
  - [1. Docstring Formatting](#1.-docstring-formatting)
  - [2. Module-Level Docstrings and Imports](#2.-module-level-docstrings-and-imports)
  - [3. Trailing Periods on Statements](#3.-trailing-periods-on-statements)
  - [4. Try Blocks Without Handlers](#4.-try-blocks-without-handlers)
  - [5. Multiline String Formatting](#5.-multiline-string-formatting)
- [Automated Tools](#automated-tools)
  - [Python Syntax Validator](#python-syntax-validator)
  - [Pre-commit Hook](#pre-commit-hook)
- [IDE Configuration](#ide-configuration)
  - [VS Code Settings](#vs-code-settings)
  - [PyCharm Settings](#pycharm-settings)
- [Code Review Checklist](#code-review-checklist)
- [Common Patterns to Avoid](#common-patterns-to-avoid)
  - [1. Concatenated Statements](#1.-concatenated-statements)
  - [2. Inconsistent Indentation](#2.-inconsistent-indentation)
  - [3. Missing Error Handling](#3.-missing-error-handling)
- [Automated Fixes](#automated-fixes)
- [Integration with CI/CD](#integration-with-ci-cd)
- [Best Practices Summary](#best-practices-summary)
- [Troubleshooting](#troubleshooting)
  - [Issue: Pre-commit hook not running](#issue:-pre-commit-hook-not-running)
  - [Issue: Auto-fix not working](#issue:-auto-fix-not-working)
  - [Issue: False positives](#issue:-false-positives)
- [Contributing](#contributing)

This guide documents common Python syntax issues encountered in the Sophia AI codebase and provides best practices to avoid them.

## Common Issues and Solutions

### 1. Docstring Formatting

**Issue**: Docstrings concatenated with following code without proper spacing.

```python
# Example usage:
python
```python

**Best Practice**: Always leave a blank line after docstrings before the first line of code.

### 2. Module-Level Docstrings and Imports

**Issue**: Module docstring immediately followed by import statements.

```python
# Example usage:
python
```python

**Best Practice**: Always leave a blank line between module docstrings and import statements.

### 3. Trailing Periods on Statements

**Issue**: Unnecessary periods at the end of Python statements.

```python
# Example usage:
python
```python

**Best Practice**: Python statements don't end with periods. Remove any trailing periods.

### 4. Try Blocks Without Handlers

**Issue**: Try blocks without except or finally clauses.

```python
# Example usage:
python
```python

**Best Practice**: Every try block must have at least one except or finally clause.

### 5. Multiline String Formatting

**Issue**: Inconsistent indentation in multiline strings.

```python
# Example usage:
python
```python

**Best Practice**: Maintain consistent indentation within multiline strings.

## Automated Tools

### Python Syntax Validator

We provide a custom syntax validator that can automatically detect and fix common issues:

```bash
# Example usage:
bash
```python

### Pre-commit Hook

A pre-commit hook is available to catch syntax errors before committing:

```bash
# Example usage:
bash
```python

The hook will:
- Block commits with syntax errors
- Show warnings for style issues (non-blocking)
- Suggest running the auto-fix tool

## IDE Configuration

### VS Code Settings

Add these settings to your `.vscode/settings.json`:

```json
# Example usage:
json
```python

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
# Example usage:
python
```python

### 2. Inconsistent Indentation

```python
# Example usage:
python
```python

### 3. Missing Error Handling

```python
# Example usage:
python
```python

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
# Example usage:
yaml
```python

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
# Example usage:
bash
```python

### Issue: Auto-fix not working
```bash
# Example usage:
bash
```python

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
