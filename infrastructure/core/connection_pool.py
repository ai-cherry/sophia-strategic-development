"""
DEPRECATED: This module has been replaced by CortexGateway.

All Snowflake connections must now go through the unified CortexGateway
to ensure proper credit tracking, monitoring, and governance.

Migration guide:
1. Replace imports:
   OLD: from infrastructure.core.connection_pool import ConnectionPoolManager
   NEW: from core.infra.cortex_gateway import get_gateway

2. Update usage:
   OLD: pool = ConnectionPoolManager(); conn = pool.get_connection()
   NEW: gateway = get_gateway(); results = await gateway.execute_sql(query)

See docs/04-deployment/SNOWFLAKE_MIGRATION_README.md for details.
"""

raise ImportError(
    "connection_pool.py is deprecated. Use 'from core.infra.cortex_gateway import get_gateway' instead. "
    "See migration guide above."
)
