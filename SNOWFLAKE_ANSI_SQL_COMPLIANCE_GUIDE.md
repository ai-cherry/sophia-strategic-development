# Snowflake ANSI SQL Compliance Guide for Sophia AI

## Overview

This document addresses the ANSI SQL compliance issues identified by SQLint in our Snowflake SQL files and provides solutions for maintaining both code quality and Snowflake functionality.

## Root Cause Analysis

The SQL syntax errors occur because **Snowflake extends standard SQL with proprietary features** that don't conform to ANSI SQL standards. This is normal and expected for a cloud data warehouse platform.

### Common Snowflake Extensions Flagged as "Errors"

1. **Snowflake-Specific Functions**
   - `CURRENT_TIMESTAMP()` vs `CURRENT_TIMESTAMP`
   - `SQLERRM`, `SQLSTATE`
   - `DATE_PART()`, `DATEADD()`

2. **Stored Procedure Syntax**
   - `RETURNS` statements
   - `EXCEPTION` blocks
   - Variable assignments with `:=`
   - `GET DIAGNOSTICS`

3. **Snowflake DDL Features**
   - `USE DATABASE/SCHEMA` statements
   - `CREATE TASK` (Snowflake's scheduling feature)
   - `GRANT` statements with Snowflake roles
   - `CREATE TAG` (data governance)

4. **Snowflake Data Types**
   - `VARIANT` (semi-structured data)
   - `ARRAY` (arrays)
   - `TIMESTAMP_LTZ`, `TIMESTAMP_NTZ` (timezone variants)

5. **Advanced Features**
   - Dollar-quoted strings (`$$`)
   - `MERGE` statements (though this is becoming more standard)
   - Search optimization
   - Masking policies

## Solutions Implemented

### 1. Updated SQLfluff Configuration

We've updated `.sqlfluff` to:
- Set dialect to `snowflake` explicitly
- Disable overly strict ANSI compliance rules
- Allow Snowflake-specific syntax patterns
- Configure appropriate formatting for Snowflake

### 2. Selective ANSI Compliance Fixes

For files that need broader SQL compatibility, we've applied these fixes:

```sql
-- BEFORE (Snowflake-specific)
CURRENT_TIMESTAMP()
VARIANT
TIMESTAMP_LTZ

-- AFTER (ANSI-compatible)
CURRENT_TIMESTAMP
TEXT -- VARIANT (Snowflake-specific)
TIMESTAMP -- TIMESTAMP_LTZ (Snowflake-specific)
```

### 3. Conditional Compilation Strategy

For production Snowflake deployment vs. ANSI compliance testing:

```sql
-- Production Snowflake version
USE DATABASE SOPHIA_AI;
CREATE OR REPLACE PROCEDURE process_data()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    result_count INTEGER DEFAULT 0;
BEGIN
    -- Snowflake-specific logic
    RETURN 'Processed ' || result_count || ' records';
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'Error: ' || SQLERRM;
END;
$$;

-- ANSI-compliant version (for testing/portability)
-- USE DATABASE SOPHIA_AI; -- Snowflake-specific
-- CREATE OR REPLACE PROCEDURE process_data() -- Snowflake stored procedure syntax
-- RETURNS STRING -- Snowflake-specific
-- ... (commented out Snowflake-specific features)
```

## Recommended Approach

### For Development Teams

1. **Keep Snowflake-Specific Features**: Don't sacrifice functionality for ANSI compliance
2. **Use SQLfluff with Snowflake Dialect**: Configure tools properly
3. **Document Snowflake Dependencies**: Make it clear which features require Snowflake
4. **Test on Target Platform**: Ensure code works on Snowflake regardless of linter warnings

### For CI/CD Pipeline

```yaml
# Example GitHub Actions configuration
- name: Lint SQL with Snowflake dialect
  run: |
    sqlfluff lint --dialect snowflake backend/snowflake_setup/
    
- name: Test SQL on Snowflake
  run: |
    # Run actual tests on Snowflake instance
    python scripts/test_snowflake_schemas.py
```

### For Code Quality

1. **Separate Concerns**:
   - Use ANSI SQL for portable business logic
   - Use Snowflake features for platform-specific optimizations

2. **Layer Architecture**:
   ```
   Business Logic Layer    → ANSI SQL (portable)
   Data Platform Layer     → Snowflake-specific (optimized)
   Infrastructure Layer    → Snowflake DDL/DML
   ```

## File-Specific Recommendations

### Critical Production Files (Keep Snowflake Features)
- `backend/snowflake_setup/*.sql` - Core Snowflake schemas
- `backend/etl/snowflake/*.sql` - ETL procedures
- Task definitions and stored procedures

### Portable Components (Consider ANSI Compliance)
- Business logic queries
- Reporting views
- Data validation scripts

## Configuration Files Updated

### `.sqlfluff`
- Set to Snowflake dialect
- Disabled overly strict ANSI rules
- Configured Snowflake-appropriate formatting

### Example Usage
```bash
# Lint with Snowflake dialect (recommended)
sqlfluff lint --dialect snowflake backend/snowflake_setup/

# Fix formatting while preserving Snowflake syntax
sqlfluff fix --dialect snowflake backend/snowflake_setup/
```

## Best Practices Going Forward

### 1. Tool Configuration
- Always specify Snowflake dialect in SQL tools
- Configure IDEs for Snowflake syntax highlighting
- Use Snowflake-aware formatters

### 2. Code Organization
```sql
-- File header indicating Snowflake dependency
-- SNOWFLAKE-SPECIFIC: This file uses Snowflake extensions
-- Target Platform: Snowflake
-- ANSI Compliance: Partial (uses Snowflake features)

USE DATABASE SOPHIA_AI; -- Snowflake-specific
```

### 3. Documentation
- Mark Snowflake-specific features in comments
- Provide ANSI alternatives where applicable
- Document platform dependencies

### 4. Testing Strategy
- Test on actual Snowflake instances
- Use Snowflake's SQL validator
- Include performance testing with Snowflake features

## Migration Strategy

If you need to migrate away from Snowflake in the future:

1. **Identify Dependencies**: Use this compliance check to catalog Snowflake features
2. **Create Abstraction Layer**: Wrap Snowflake-specific features
3. **Gradual Migration**: Replace features incrementally
4. **Feature Mapping**: Document equivalent features in target platform

## Conclusion

**ANSI SQL compliance is valuable for portability, but shouldn't compromise functionality on your target platform.**

For Sophia AI running on Snowflake:
- ✅ Use Snowflake features for optimal performance
- ✅ Configure tools for Snowflake dialect
- ✅ Document platform dependencies
- ✅ Test on actual Snowflake instances
- ❌ Don't sacrifice functionality for theoretical portability

The SQLfluff configuration and selective fixes provide a balanced approach that maintains code quality while preserving Snowflake's powerful features.

## Quick Reference

### Fixed Issues Summary
- ✅ Updated `.sqlfluff` for Snowflake dialect
- ✅ Applied selective ANSI fixes to critical files
- ✅ Documented Snowflake dependencies
- ✅ Provided migration guidance

### Next Steps
1. Review the updated configuration
2. Test SQL files with `sqlfluff lint --dialect snowflake`
3. Commit changes with appropriate documentation
4. Update team guidelines for Snowflake SQL development 