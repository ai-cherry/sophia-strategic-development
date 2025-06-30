#!/usr/bin/env python3
"""
Fix the OptimizedConnectionManager indentation issue
"""

import re

# Read the file
with open("backend/core/optimized_connection_manager.py", "r") as f:
    content = f.read()

# Fix the indentation issue around _create_snowflake_connection
# The method should be properly indented as part of the class

fixed_content = content.replace(
    """        async def _create_snowflake_connection(self):
        \"\"\"Create Snowflake connection with corrected configuration\"\"\"
        
        # Get corrected connection parameters from override
        params = get_snowflake_connection_params()
        params["timeout"] = self.connection_timeout

        # Use asyncio.to_thread to run synchronous connector in thread pool
        def _sync_connect():
            return snowflake.connector.connect(**params)

        return await asyncio.to_thread(_sync_connect)""",
    """
    async def _create_snowflake_connection(self):
        \"\"\"Create Snowflake connection with corrected configuration\"\"\"
        
        # Get corrected connection parameters from override
        params = get_snowflake_connection_params()
        params["timeout"] = self.connection_timeout

        # Use asyncio.to_thread to run synchronous connector in thread pool
        def _sync_connect():
            return snowflake.connector.connect(**params)

        return await asyncio.to_thread(_sync_connect)""",
)

# Write the fixed content
with open("backend/core/optimized_connection_manager.py", "w") as f:
    f.write(fixed_content)

print("✅ Fixed OptimizedConnectionManager indentation")
