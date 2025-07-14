# One-Time Scripts Directory

🚨 **CRITICAL RULES:**
1. All scripts in this directory are AUTOMATICALLY DELETED after 30 days
2. Add deletion date to filename: `script_name_DELETE_2025_08_15.py`
3. Include deletion reminder in script header
4. Use for: deployments, migrations, fixes, tests, setups

✅ **PERMANENT SCRIPTS GO IN:**
- `scripts/utils/` (reusable utilities)
- `scripts/monitoring/` (ongoing monitoring)  
- `scripts/maintenance/` (regular maintenance)

## Example One-Time Script Header:
```python
#!/usr/bin/env python3
"""
One-time script: Fix authentication issue
DELETE AFTER: 2025-08-15
Created: 2025-07-13
Purpose: Fix specific auth bug in production
"""
```
