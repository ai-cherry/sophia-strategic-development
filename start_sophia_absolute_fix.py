#!/usr/bin/env python3
"""
Sophia AI Startup with ABSOLUTE Snowflake Fix
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ABSOLUTE environment setup
os.environ["SNOWFLAKE_ACCOUNT"] = "ZNB04675"
os.environ["SNOWFLAKE_USER"] = "SCOOBYJAVA15"
os.environ["SNOWFLAKE_DATABASE"] = "SOPHIA_AI"
os.environ["SNOWFLAKE_WAREHOUSE"] = "SOPHIA_AI_WH"
os.environ["SNOWFLAKE_ROLE"] = "ACCOUNTADMIN"
os.environ["SNOWFLAKE_SCHEMA"] = "PROCESSED_AI"


# Import absolute override to force settings

# Test the fix
try:
    from backend.core.absolute_snowflake_override import get_snowflake_connection_params

    params = get_snowflake_connection_params()

    if params["account"] == "ZNB04675":
        pass
    else:
        sys.exit(1)

except Exception:
    sys.exit(1)

if __name__ == "__main__":
    # Start the FastAPI application
    import uvicorn

    uvicorn.run(
        "backend.app.fastapi_app:app",
        host="127.0.0.1",  # Changed from 0.0.0.0 for security. Use environment variable for production,
        port=8000,
        reload=False,
        log_level="info",
    )
