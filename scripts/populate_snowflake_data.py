#!/usr/bin/env python3
"""
Populate ModernStack with test data for Sophia AI
"""
import os
# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3
from pathlib import Path

# Load environment
env_file = Path(__file__).parent.parent / "local.env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value.strip('"').strip("'")

print("🔍 Populating ModernStack with Sophia AI data...")

try:
    # Connect
    conn = self.modern_stack_connection(
        account=os.environ.get("modern_stack_ACCOUNT"),
        user=os.environ.get("modern_stack_USER"),
        password=os.environ.get("modern_stack_PAT"),
        role=os.environ.get("modern_stack_ROLE", "ACCOUNTADMIN"),
        warehouse=os.environ.get("modern_stack_WAREHOUSE", "SOPHIA_AI_COMPUTE_WH"),
        database=os.environ.get("modern_stack_DATABASE", "AI_MEMORY"),
        schema=os.environ.get("modern_stack_SCHEMA", "VECTORS"),
    )

    cursor = conn.cursor()
    print("✅ Connected to ModernStack")

    # Add business insights using simpler approach
    print("\n📝 Adding business insights...")

    # Deployment status
    cursor.execute(
        """
        INSERT INTO KNOWLEDGE_BASE 
        SELECT 
            'sophia_deploy_001' as id,
            'Sophia AI successfully deployed with full ModernStack integration' as content,
            'sophia_ai_deployment' as source,
            OBJECT_CONSTRUCT(
                'version', '4.0.0',
                'date', '2025-07-10',
                'components', ARRAY_CONSTRUCT('backend', 'frontend', 'modern_stack', 'redis')
            ) as metadata,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
    """
    )
    print("✅ Added deployment status")

    # System capabilities
    cursor.execute(
        """
        INSERT INTO KNOWLEDGE_BASE 
        SELECT 
            'sophia_cap_001' as id,
            'System can store and retrieve business intelligence insights using ModernStack AI_MEMORY database' as content,
            'sophia_ai_capabilities' as source,
            OBJECT_CONSTRUCT(
                'features', ARRAY_CONSTRUCT('knowledge_base', 'memory_records', 'business_insights'),
                'database', 'AI_MEMORY',
                'warehouse', 'SOPHIA_AI_COMPUTE_WH'
            ) as metadata,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
    """
    )
    print("✅ Added system capabilities")

    # User information
    cursor.execute(
        """
        INSERT INTO KNOWLEDGE_BASE 
        SELECT 
            'sophia_user_001' as id,
            'CEO user Lynn Musil has full access to Sophia AI system with executive dashboard' as content,
            'sophia_ai_users' as source,
            OBJECT_CONSTRUCT(
                'user', 'ceo_user',
                'name', 'Lynn Musil',
                'role', 'CEO',
                'permissions', 'full_access'
            ) as metadata,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
    """
    )
    print("✅ Added user information")

    # Add memory record
    print("\n📝 Adding memory records...")
    cursor.execute(
        """
        INSERT INTO MEMORY_RECORDS 
        SELECT 
            'mem_deploy_001' as id,
            'ceo_user' as user_id,
            'deployment_test' as session_id,
            'System deployment completed successfully with all components operational' as content,
            ARRAY_CONSTRUCT() as embedding,
            OBJECT_CONSTRUCT(
                'timestamp', CURRENT_TIMESTAMP()::STRING,
                'status', 'success',
                'components_tested', ARRAY_CONSTRUCT('backend', 'frontend', 'modern_stack', 'redis')
            ) as metadata,
            'deployment' as memory_type,
            CURRENT_TIMESTAMP() as created_at
    """
    )
    print("✅ Added deployment memory")

    # Add business insight
    cursor.execute(
        """
        INSERT INTO BUSINESS_INSIGHTS 
        SELECT 
            'insight_001' as id,
            'deployment_success' as insight_type,
            'Sophia AI platform successfully deployed and ready for executive use' as content,
            ARRAY_CONSTRUCT() as embedding,
            OBJECT_CONSTRUCT(
                'confidence', 1.0,
                'source', 'system_deployment',
                'date', '2025-07-10'
            ) as metadata,
            1.0 as confidence_score,
            CURRENT_TIMESTAMP() as created_at
    """
    )
    print("✅ Added business insight")

    # Query and show results
    print("\n📊 Current Data Summary:")

    cursor.execute("SELECT COUNT(*) FROM KNOWLEDGE_BASE")
    kb_count = cursor.fetchone()[0]
    print(f"   Knowledge Base: {kb_count} records")

    cursor.execute("SELECT COUNT(*) FROM MEMORY_RECORDS")
    mem_count = cursor.fetchone()[0]
    print(f"   Memory Records: {mem_count} records")

    cursor.execute("SELECT COUNT(*) FROM BUSINESS_INSIGHTS")
    bi_count = cursor.fetchone()[0]
    print(f"   Business Insights: {bi_count} records")

    print("\n📋 Recent Knowledge Base Entries:")
    cursor.execute(
        """
        SELECT id, content, source 
        FROM KNOWLEDGE_BASE 
        ORDER BY created_at DESC 
        LIMIT 5
    """
    )
    rows = cursor.fetchall()
    for row in rows:
        print(f"   [{row[0]}] {row[1][:60]}...")

    cursor.close()
    conn.close()

    print("\n✅ ModernStack populated successfully!")
    print("\n🎉 Sophia AI is now fully operational with:")
    print("   - Backend API: http://localhost:8001")
    print("   - Frontend UI: http://localhost:5173")
    print("   - ModernStack Database: AI_MEMORY")
    print("   - Knowledge Base: Ready for use")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()
