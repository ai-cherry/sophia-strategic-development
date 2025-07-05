# Ruff Linting Report

## Summary

- **Total Issues Found**: 8,635
- **Issues Fixed Automatically**: 5,834 (67.6%)
  - Standard fixes: 1,204
  - Unsafe fixes: 4,630
- **Remaining Issues**: 3,665 (42.4%)

## Top Issues Requiring Manual Attention

### 1. Module Import Order (E402) - 1,389 issues
- Imports that are not at the top of the file
- Common in scripts that modify sys.path before imports

### 2. Unused Method Arguments (ARG002) - 585 issues
- Method parameters that aren't used in the method body
- Often found in abstract methods, callbacks, or interface implementations

### 3. Syntax Errors - 348 issues
- Files with Python syntax errors that need manual fixing
- These prevent the files from being parsed properly

### 4. Assert Statements (S101) - 203 issues
- Use of assert statements (mostly in test files)
- Generally acceptable in tests but not in production code

### 5. Security Issues - Various
- S607: Starting process with partial path (164)
- S603: Subprocess without shell=True (126)
- S110: Try-except-pass without logging (93)
- S608: Hardcoded SQL expressions (93)
- S113: Requests without timeout (60)
- S104: Hardcoded bind to all interfaces (40)

## Recommendations

1. **Fix Syntax Errors First**: These 348 files won't run at all
2. **Address Security Issues**: Especially subprocess and SQL injection risks
3. **Review Unused Arguments**: May indicate incomplete implementations
4. **Consider Disabling Some Rules**:
   - S101 (assert) for test files
   - ARG002 for abstract methods/interfaces
5. **Module Import Order**: Can be fixed systematically but requires careful review

## Next Steps

1. Run `ruff check . --select E999` to focus on syntax errors
2. Fix critical security issues (S6xx series)
3. Consider adding per-file ignores for legitimate cases
4. Set up pre-commit hooks to prevent new issues
