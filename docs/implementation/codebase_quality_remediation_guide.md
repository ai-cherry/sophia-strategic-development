# 🤖 AI CODING AGENT: COMPREHENSIVE CODEBASE REVIEW PROMPT
## Sophia AI - Python/TypeScript Linting & Syntax Analysis

**Target Agent**: OpenAI Codex / GPT-4 Code Assistant
**Repository**: ai-cherry/sophia-main
**Focus Areas**: Linting, Indentation, Syntax Errors
**Approach**: Systematic, prioritized, safe fixes

---

## 📋 MISSION BRIEFING

You are an expert Python and TypeScript developer tasked with performing a comprehensive codebase review for the Sophia AI platform. Your mission is to identify and systematically fix linting issues, indentation problems, and syntax errors while maintaining code functionality and following established patterns.

### **Primary Objectives**:
1. **Identify all linting violations** reported by ruff, black, and mypy
2. **Fix indentation inconsistencies** across Python and TypeScript files
3. **Resolve syntax errors** that prevent code execution
4. **Maintain code functionality** - never break existing logic
5. **Follow established patterns** in the codebase

### **Success Criteria**:
- Zero syntax errors preventing code execution
- <100 remaining linting violations (from current 5,000+)
- Consistent indentation throughout codebase
- All fixes preserve existing functionality
- Code follows PEP 8 and project style guidelines

---

## 🔍 CURRENT CODEBASE STATE

### **Known Issues (From Recent Analysis)**:
```
Found 5079 errors.
No fixes available (1851 hidden fixes can be enabled with the --unsafe-fixes option).

Common Issue Categories:
- S101: Use of assert detected (very frequent in test files)
- E402: Module-level import not at top of file
- S603 & S607: Subprocess call with untrusted input
- UP007 & UP035: Deprecated type annotations
- C901: Function is too complex
- S104 & S105: Security warnings (hardcoded passwords, network binding)
- F821: Undefined name errors
- S608: Possible SQL injection vectors
```

### **Repository Structure**:
```
sophia-main/
├── backend/               # Python FastAPI application
├── frontend/             # TypeScript/React application (if present)
├── mcp-servers/          # MCP server implementations
├── scripts/              # Python automation scripts
├── tests/                # Test suites
├── infrastructure/       # Pulumi/deployment configs
└── docs/                 # Documentation
```

---

## 🎯 SYSTEMATIC REVIEW APPROACH

### **Phase 1: Critical Syntax Errors (PRIORITY 1)**

**Objective**: Fix all syntax errors that prevent code execution

**Instructions**:
1. **Scan for syntax errors** in all `.py` files using AST parsing
2. **Identify broken imports** and undefined references
3. **Fix indentation errors** that cause SyntaxError
4. **Resolve bracket/parentheses mismatches**
5. **Fix string/quote inconsistencies**

**Example Fixes**:
```python
# BEFORE (Syntax Error)
def function(
    param1,
    param2
  # Missing closing parenthesis

# AFTER (Fixed)
def function(
    param1,
    param2
):
    pass
```

**Commands to Run**:
```bash
# Test syntax validity
python -m py_compile backend/**/*.py
python -c "import ast; [ast.parse(open(f).read()) for f in glob.glob('**/*.py', recursive=True)]"
```

### **Phase 2: Import Organization (PRIORITY 2)**

**Objective**: Fix E402 errors and organize imports properly

**Instructions**:
1. **Move all imports to top of file** (after module docstring)
2. **Group imports correctly**: standard library → third-party → local
3. **Sort imports alphabetically** within each group
4. **Remove unused imports**
5. **Fix relative import issues**

**Example Fixes**:
```python
# BEFORE (E402 Error)
"""Module docstring"""

def some_function():
    pass

import os  # Import not at top
import sys
from typing import Dict

# AFTER (Fixed)
"""Module docstring"""

import os
import sys
from typing import Dict

def some_function():
    pass
```

**Pattern to Follow**:
```python
#!/usr/bin/env python3
"""Module docstring"""

# Standard library imports
import os
import sys
from typing import Any, Dict, List

# Third-party imports
import requests
from fastapi import FastAPI

# Local imports
from backend.core.config import settings
from backend.services.base import BaseService
```

### **Phase 3: Type Annotation Modernization (PRIORITY 3)**

**Objective**: Fix UP007 and UP035 errors - modernize type hints

**Instructions**:
1. **Replace deprecated typing imports**:
   - `typing.Dict` → `dict`
   - `typing.List` → `list`
   - `typing.Tuple` → `tuple`
   - `typing.Union[X, Y]` → `X | Y`
2. **Update function signatures** with modern annotations
3. **Maintain backward compatibility** for Python 3.10+

**Example Fixes**:
```python
# BEFORE (Deprecated)
from typing import Dict, List, Union, Optional

def process_data(items: List[Dict[str, Any]]) -> Optional[Union[str, int]]:
    pass

# AFTER (Modern)
from typing import Any

def process_data(items: list[dict[str, Any]]) -> str | int | None:
    pass
```

### **Phase 4: Security Issue Resolution (PRIORITY 4)**

**Objective**: Address S603, S607, S608 security warnings safely

**Instructions**:
1. **Subprocess Security (S603/S607)**:
   - Never use `shell=True`
   - Use `shlex.split()` for command parsing
   - Replace `python` with `sys.executable`
   - Validate input parameters

2. **SQL Injection Prevention (S608)**:
   - Verify parameterized queries are used
   - Check if table names come from safe enums
   - Add `# noqa: S608` with justification if safe

**Example Fixes**:
```python
# BEFORE (Security Issue)
import subprocess
subprocess.run("python script.py", shell=True)  # S603

# AFTER (Secure)
import subprocess
import sys
import shlex
subprocess.run([sys.executable, "script.py"])  # Secure

# SQL Example (if safe)
query = f"SELECT * FROM {table_name}"  # noqa: S608 - table_name from safe enum
```

### **Phase 5: Test File Handling (PRIORITY 5)**

**Objective**: Handle S101 assert warnings in test files appropriately

**Instructions**:
1. **Identify test files** (in `tests/` directory or `test_*.py`)
2. **Suppress S101 warnings** in test files only
3. **Add file-level noqa** for test files
4. **Maintain assert statements** in tests (they're appropriate there)

**Example Fixes**:
```python
# At top of test files
# ruff: noqa: S101
"""Test module - assert statements are appropriate here"""

def test_function():
    result = some_function()
    assert result == expected  # This is correct in tests
```

### **Phase 6: Code Complexity Reduction (PRIORITY 6)**

**Objective**: Address C901 complexity warnings

**Instructions**:
1. **Identify overly complex functions** (>10 complexity)
2. **Apply Extract Method refactoring**:
   - Break large functions into smaller helpers
   - Maintain original public interface
   - Preserve all functionality
3. **Focus on readability improvements**

**Example Refactoring**:
```python
# BEFORE (Too Complex)
def complex_function(data):
    # 50 lines of complex logic
    if condition1:
        # complex block 1
    elif condition2:
        # complex block 2
    # ... more complexity

# AFTER (Refactored)
def complex_function(data):
    if condition1:
        return _handle_condition1(data)
    elif condition2:
        return _handle_condition2(data)
    return _handle_default(data)

def _handle_condition1(data):
    # extracted logic
    pass

def _handle_condition2(data):
    # extracted logic
    pass
```

---

## 🛡️ SAFETY GUIDELINES

### **Critical Rules**:
1. **NEVER change public APIs** - maintain all function signatures
2. **NEVER remove functionality** - only reorganize and clean up
3. **NEVER fix issues in archived directories** - leave them alone
4. **ALWAYS test changes** - ensure code still runs
5. **PRESERVE comments and docstrings** - maintain documentation

### **Files to AVOID Modifying**:
```
- archive/
- backup*/
- *_backup_*/
- *.backup
- docs_backup_*/
- Any file in .gitignore patterns
```

### **Safe Modification Patterns**:
```python
# ✅ SAFE: Import reordering
import os
import sys
from typing import Any

# ✅ SAFE: Type annotation updates
def func(items: list[str]) -> str | None:

# ✅ SAFE: Adding noqa comments
assert condition  # noqa: S101 - appropriate in test

# ❌ UNSAFE: Changing function signatures
def func(old_param):  # Don't rename parameters
```

---

## 📊 EXECUTION STRATEGY

### **Step-by-Step Process**:

1. **Initial Assessment**:
   ```bash
   ruff check . --statistics
   ruff check . --output-format=json > linting_report.json
   ```

2. **Systematic Fixing** (in priority order):
   ```bash
   # Phase 1: Syntax errors first
   python -m py_compile **/*.py

   # Phase 2: Auto-fixable issues
   ruff check . --fix --unsafe-fixes

   # Phase 3: Manual review and fixes
   ruff check . --show-fixes
   ```

3. **Validation After Each Phase**:
   ```bash
   # Ensure code still works
   python -m pytest tests/ --tb=short
   python backend/app/fastapi_main.py --help  # Basic smoke test
   ```

4. **Progress Tracking**:
   ```bash
   # Count remaining issues
   ruff check . | wc -l
   echo "Remaining issues: $(ruff check . | wc -l)"
   ```

### **Expected Timeline**:
- **Phase 1** (Syntax): 30 minutes
- **Phase 2** (Imports): 45 minutes
- **Phase 3** (Types): 30 minutes
- **Phase 4** (Security): 60 minutes
- **Phase 5** (Tests): 15 minutes
- **Phase 6** (Complexity): 90 minutes
- **Total**: ~4.5 hours for comprehensive cleanup

---

## 📝 REPORTING REQUIREMENTS

### **Progress Reports**:
Provide updates after each phase:

```markdown
## Phase X Completion Report

**Issues Fixed**: [number]
**Issues Remaining**: [number]
**Files Modified**: [list]
**Key Changes**:
- [summary of major fixes]

**Validation**:
- ✅ Code syntax valid
- ✅ Tests still pass
- ✅ No functionality broken

**Next Phase**: [brief description]
```

### **Final Summary Report**:
```markdown
## Codebase Review Completion

**Total Issues Fixed**: [number]
**Remaining Issues**: [number]
**Files Modified**: [count]
**Time Taken**: [duration]

**Major Improvements**:
- Syntax errors: 100% resolved
- Import organization: 100% compliant
- Type annotations: Modernized
- Security issues: [X]% resolved
- Code complexity: [X]% improved

**Remaining Work**:
- [list any issues that need manual review]

**Recommendations**:
- [suggestions for maintaining code quality]
```

---

## 🎯 SUCCESS VALIDATION

### **Final Checks**:
```bash
# 1. Syntax validation
python -m py_compile $(find . -name "*.py" -not -path "./archive/*")

# 2. Linting check
ruff check . --statistics

# 3. Type checking
mypy backend/ --ignore-missing-imports

# 4. Test execution
python -m pytest tests/ --tb=short

# 5. Basic smoke test
python backend/app/fastapi_main.py --help
```

### **Acceptance Criteria**:
- [ ] Zero syntax errors
- [ ] <100 linting violations (95% reduction)
- [ ] All tests pass
- [ ] Application starts successfully
- [ ] No functionality regression

---

## 🚀 EXECUTION COMMAND

**To begin the comprehensive review, execute**:

```bash
# Start with assessment
ruff check . --statistics > initial_assessment.txt
echo "Starting comprehensive codebase review..."
echo "Initial issues: $(ruff check . | wc -l)"

# Then proceed through phases systematically
```

**Remember**: Quality over speed. It's better to fix issues correctly than to rush and break functionality. Focus on one phase at a time and validate thoroughly before proceeding.

**This systematic approach will transform the Sophia AI codebase from 5,000+ linting issues to enterprise-grade code quality while maintaining all existing functionality.**
