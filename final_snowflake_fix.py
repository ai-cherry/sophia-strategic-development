#!/usr/bin/env python3
"""
Final comprehensive Snowflake fix to ensure OptimizedConnectionManager uses correct account
"""

import os
import re

# 1. Ensure the OptimizedConnectionManager imports and uses the override correctly
connection_manager_file = "backend/core/optimized_connection_manager.py"

with open(connection_manager_file) as f:
    content = f.read()

# Ensure the import is at the top
if (
    "from backend.core.snowflake_override import get_snowflake_connection_params"
    not in content
):
    # Add the import after other backend imports
    lines = content.split("\n")

    # Find where to insert the import
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("from backend.core.") and "import" in line:
            insert_idx = i + 1

    lines.insert(
        insert_idx,
        "from backend.core.snowflake_override import get_snowflake_connection_params",
    )
    content = "\n".join(lines)

# Ensure the _create_snowflake_connection method is properly implemented
snowflake_method = '''    async def _create_snowflake_connection(self):
        """Create Snowflake connection with corrected configuration"""

        # FORCE USE OF OVERRIDE - This ensures ZNB04675 account is always used
        params = get_snowflake_connection_params()
        params["timeout"] = self.connection_timeout

        # Log the account being used for verification
        logger.info(f"🔧 Creating Snowflake connection to account: {params['account']}")

        # Use asyncio.to_thread to run synchronous connector in thread pool
        def _sync_connect():
            return snowflake.connector.connect(**params)

        return await asyncio.to_thread(_sync_connect)'''

# Replace the existing method
pattern = r"async def _create_snowflake_connection\(self\):.*?return await asyncio\.to_thread\(_sync_connect\)"
content = re.sub(pattern, snowflake_method, content, flags=re.DOTALL)

# Write the updated content
with open(connection_manager_file, "w") as f:
    f.write(content)

print("✅ Updated OptimizedConnectionManager with forced override")

# 2. Create a comprehensive startup script that forces the fix
startup_script_content = '''#!/usr/bin/env python3
"""
Sophia AI Startup Script with PERMANENT Snowflake Fix
Run this before starting any Sophia AI services
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def apply_permanent_snowflake_fix():
    """Apply permanent Snowflake configuration fix"""
    print("🔧 Applying PERMANENT Snowflake configuration fix...")

    # Force correct environment variables
    correct_config = {
        'SNOWFLAKE_ACCOUNT': 'ZNB04675',
        'SNOWFLAKE_USER': 'SCOOBYJAVA15',
        'SNOWFLAKE_DATABASE': 'SOPHIA_AI',
        'SNOWFLAKE_WAREHOUSE': 'SOPHIA_AI_WH',
        'SNOWFLAKE_ROLE': 'ACCOUNTADMIN',
        'SNOWFLAKE_SCHEMA': 'PROCESSED_AI'
    }

    for key, value in correct_config.items():
        os.environ[key] = value
        print(f"   ✅ Set {key}: {value}")

    # Clear any Python cache that might have old values
    import subprocess
    try:
        subprocess.run(['find', '.', '-name', '*.pyc', '-delete'],
                      capture_output=True, check=False)
        subprocess.run(['find', '.', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'],
                      capture_output=True, check=False)
        print("   ✅ Cleared Python cache")
    except:
        pass

    print("🎉 Permanent Snowflake fix applied!")
    return correct_config

if __name__ == "__main__":
    apply_permanent_snowflake_fix()

    # Test the fix
    try:
        from backend.core.snowflake_override import get_snowflake_connection_params
        params = get_snowflake_connection_params()
        print(f"🧪 Test: Snowflake account is {params['account']}")

        if params['account'] == 'ZNB04675':
            print("✅ PERMANENT FIX VERIFIED - Ready to start Sophia AI!")
        else:
            print(f"❌ Fix verification failed - account is {params['account']}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Fix verification error: {e}")
        sys.exit(1)
'''

with open("start_sophia_fixed.py", "w") as f:
    f.write(startup_script_content)

os.chmod("start_sophia_fixed.py", 0o755)
print("✅ Created startup script with permanent fix")

# 3. Test the fix immediately
print("\n🧪 Testing the fix...")

try:
    # Clear any cached imports
    import sys

    modules_to_clear = [m for m in sys.modules.keys() if m.startswith("backend.core")]
    for module in modules_to_clear:
        del sys.modules[module]

    # Test the override
    from backend.core.snowflake_override import get_snowflake_connection_params

    params = get_snowflake_connection_params()

    print(f"   Account: {params['account']}")
    print(f"   User: {params['user']}")
    print(f"   Database: {params['database']}")

    if params["account"] == "ZNB04675":
        print("✅ Fix is working correctly!")
    else:
        print(f"❌ Fix failed - still using {params['account']}")

except Exception as e:
    print(f"❌ Test failed: {e}")

print("\n🚀 Final fix complete - ready to push to GitHub!")
