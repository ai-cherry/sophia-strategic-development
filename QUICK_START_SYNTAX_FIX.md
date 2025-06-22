# Quick Start: Fix Sophia AI Backend Syntax

## 🚀 Immediate Actions

### 1. Check Current Status
```bash
# See how many files are still broken
find backend -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -c "Error"
```

### 2. Fix Critical Blocker (auto_esc_config.py)
```bash
# This file MUST be fixed first
python -m py_compile backend/core/auto_esc_config.py
# If it shows errors, fix them manually or with a script
```

### 3. Run Existing Fix Script
```bash
# Try the automated fixer
python scripts/fix_docstring_corruption.py

# Check if it helped
find backend -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -c "Error"
```

### 4. Test Minimal Backend
```bash
# Set up environment
export PULUMI_ORG=scoobyjava-org

# Run minimal backend with ESC secrets
pulumi env run scoobyjava-org/default/sophia-ai-production -- python3 backend/minimal_main.py
```

### 5. Quick Health Check
```bash
# Once backend is running
curl http://localhost:8000/health
curl http://localhost:8000/config
```

## 🔥 Emergency Fix for auto_esc_config.py

If the file is completely broken, recreate it:

```python
"""Auto ESC configuration loader for Pulumi ESC integration."""

import os
import json
import subprocess
from typing import Optional, Dict, Any


class AutoESCConfig:
    """Singleton configuration manager for Pulumi ESC."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from Pulumi ESC."""
        try:
            # Get Pulumi org from environment
            pulumi_org = os.getenv('PULUMI_ORG', 'scoobyjava-org')
            
            # Run pulumi env command
            cmd = [
                'pulumi', 'env', 'open',
                f'{pulumi_org}/default/sophia-ai-production',
                '--format', 'json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self._config = json.loads(result.stdout)
            else:
                print(f"Failed to load ESC config: {result.stderr}")
                self._config = {}
                
        except Exception as e:
            print(f"Error loading ESC config: {e}")
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        return self.get('OPENAI_API_KEY')
    
    @property
    def gong_access_key(self) -> Optional[str]:
        """Get Gong access key."""
        return self.get('GONG_ACCESS_KEY')
    
    @property
    def snowflake_account(self) -> Optional[str]:
        """Get Snowflake account."""
        return self.get('SNOWFLAKE_ACCOUNT')


# Create singleton instance
config = AutoESCConfig()
```

## 📝 Common Fix Patterns

### Pattern 1: Simple Docstring Fix
```bash
# Find and fix simple docstring merges
sed -i 's/\."""\([^"]\)/."""\n\n\1/g' backend/core/*.py
```

### Pattern 2: Class Docstring Fix
```bash
# Fix class docstrings
sed -i 's/\."""def /."""\n    \n    def /g' backend/**/*.py
```

### Pattern 3: Multi-line String Fix
```bash
# Fix multi-line strings
sed -i 's/\"""[[:space:]]*\([^[:space:]]\)/"""\n\1/g' backend/**/*.py
```

## 🎯 Success Checklist

- [ ] `auto_esc_config.py` compiles without errors
- [ ] Minimal backend starts successfully
- [ ] Health endpoint returns 200 OK
- [ ] ESC secrets are accessible
- [ ] No import errors in console

## 💡 Pro Tips

1. **Start Small**: Fix one file at a time, starting with `auto_esc_config.py`
2. **Test Often**: Run `python -m py_compile` after each fix
3. **Use the Minimal Backend**: It bypasses most imports for faster testing
4. **Check Dependencies**: Fix files in import order
5. **Commit Working Fixes**: Save progress frequently

## 🆘 If All Else Fails

1. **Recreate Critical Files**: Sometimes it's faster to rewrite than fix
2. **Use Git History**: Check previous versions if available
3. **Focus on Core Path**: Just get the minimal backend running first
4. **Ask for Help**: The infrastructure team can provide clean versions

Remember: The goal is to get the backend running on port 8000. Everything else can wait!
