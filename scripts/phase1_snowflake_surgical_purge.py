#!/usr/bin/env python3
"""
🔪 SURGICAL SNOWFLAKE PURGE - Phase 1
Replaces all legacy SnowflakeCortexService imports with UnifiedMemoryServiceV2
Because Snowflake cancer must be excised before prod deployment.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Files identified with Snowflake Cortex imports
INFECTED_FILES = [
    "./core/workflows/cross_group_intelligence_hub.py",
    "./core/workflows/enhanced_langgraph_orchestration.py", 
    "./core/workflows/unified_intent_engine.py",
    "./core/workflows/langgraph_agent_orchestration.py",
    "./core/agents/research/orchestration_research_agent.py",
    "./core/agents/langgraph_agent_base.py",
    "./core/cross_platform_sync_orchestrator.py",
    "./core/use_cases/slack_analysis_agent.py",
    "./core/use_cases/asana_project_intelligence_agent.py",
    "./core/use_cases/linear_project_health_agent.py",
    "./core/use_cases/interactive_sales_coach_agent.py",
    "./core/use_cases/sales_intelligence_agent_core.py",
    "./core/use_cases/sales_coach_agent.py",
    "./core/use_cases/call_analysis_agent.py",
    "./core/use_cases/marketing_analysis_agent.py",
    "./core/services/natural_language_infrastructure_controller.py",
    "./backend/services/enhanced_search_service.py",
    "./backend/services/temporal_qa_learning_service.py",
    "./backend/services/enhanced_snowflake_cortex_service.py",
    "./backend/services/enhanced_multi_agent_orchestrator.py",
    "./backend/services/lambda_labs_cost_monitor.py",
    "./backend/services/lambda_labs_serverless_service.py",
    "./backend/services/gong_multi_purpose_intelligence.py",
    "./shared/utils/enhanced_snowflake_cortex_service.py",
    "./scripts/backend/batch_embed_data.py",
    "./scripts/backend/sophia_data_pipeline_ultimate.py",
    "./scripts/snowflake_migration/migrate_to_gateway.py",
    "./infrastructure/etl/enhanced_unified_data_pipeline.py",
    "./infrastructure/etl/estuary/estuary_configuration_manager.py",
    "./infrastructure/integrations/enhanced_microsoft_gong_integration.py",
    "./infrastructure/persistence/repositories/snowflake_call_repository.py",
    "./infrastructure/monitoring/deployment_tracker.py",
    "./infrastructure/services/llm_gateway/snowflake_cortex_enhanced.py",
    "./infrastructure/services/intelligent_query_router.py",
    "./infrastructure/services/foundational_knowledge_service.py",
    "./infrastructure/services/cost_engineering_service.py",
    "./infrastructure/services/semantic_layer_service.py",
    "./infrastructure/services/enhanced_snowflake_cortex_service.py",
    "./infrastructure/services/unified_intelligence_service.py"
]

# Replacement patterns
REPLACEMENTS = [
    # Import replacements
    (
        r"from shared\.utils\.snowflake_cortex_service import SnowflakeCortexService",
        "from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2"
    ),
    (
        r"from shared\.utils\.enhanced_snowflake_cortex_service import.*",
        "from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2"
    ),
    (
        r"from backend\.services\.enhanced_snowflake_cortex_service import.*",
        "from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2"
    ),
    # Class instantiation replacements
    (
        r"SnowflakeCortexService\(\)",
        "UnifiedMemoryServiceV2()"
    ),
    (
        r"self\.snowflake_cortex = SnowflakeCortexService\(\)",
        "self.memory_service = UnifiedMemoryServiceV2()"
    ),
    (
        r"snowflake_cortex = SnowflakeCortexService\(\)",
        "memory_service = UnifiedMemoryServiceV2()"
    ),
    # Method call replacements (common patterns)
    (
        r"\.snowflake_cortex\.",
        ".memory_service."
    ),
    (
        r"snowflake_cortex\.",
        "memory_service."
    ),
    # Specific method replacements
    (
        r"\.embed_text\(",
        ".generate_embedding("
    ),
    (
        r"\.search_knowledge\(",
        ".search_knowledge("
    ),
    (
        r"\.add_knowledge\(",
        ".add_knowledge("
    )
]

def surgical_replace_file(file_path: str) -> Tuple[bool, str, List[str]]:
    """
    Surgically replace Snowflake imports in a single file
    Returns: (success, new_content, changes_made)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        for pattern, replacement in REPLACEMENTS:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made.append(f"  ✅ {pattern} → {replacement}")
        
        # Check if we actually made changes
        if content != original_content:
            return True, content, changes_made
        else:
            return False, content, ["  ℹ️  No Snowflake patterns found"]
            
    except Exception as e:
        return False, "", [f"  ❌ Error: {str(e)}"]

def validate_syntax(file_path: str, content: str) -> bool:
    """
    Validate Python syntax after replacement
    """
    try:
        compile(content, file_path, 'exec')
        return True
    except SyntaxError as e:
        print(f"    ⚠️  Syntax error in {file_path}: {e}")
        return False

def main():
    """
    Execute surgical Snowflake purge across all infected files
    """
    print("🔪 SURGICAL SNOWFLAKE PURGE - Phase 1")
    print("=" * 50)
    
    total_files = len(INFECTED_FILES)
    successful_purges = 0
    failed_purges = 0
    backup_dir = "backup_snowflake_purge"
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📁 Backup directory created: {backup_dir}")
    
    for i, file_path in enumerate(INFECTED_FILES, 1):
        print(f"\n[{i}/{total_files}] 🔍 Processing: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"  ⚠️  File not found, skipping")
            continue
            
        # Create backup
        backup_path = os.path.join(backup_dir, file_path.replace("/", "_").replace(".", "_") + ".backup")
        try:
            with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
        except Exception as e:
            print(f"  ❌ Backup failed: {e}")
            failed_purges += 1
            continue
        
        # Perform surgical replacement
        success, new_content, changes = surgical_replace_file(file_path)
        
        if success and changes and not changes[0].startswith("  ℹ️"):
            # Validate syntax
            if validate_syntax(file_path, new_content):
                # Write the purged file
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"  ✅ PURGED successfully")
                    for change in changes:
                        print(change)
                    successful_purges += 1
                    
                except Exception as e:
                    print(f"  ❌ Write failed: {e}")
                    failed_purges += 1
            else:
                print(f"  ❌ Syntax validation failed")
                failed_purges += 1
        else:
            if changes:
                for change in changes:
                    print(change)
            if not success:
                failed_purges += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("🏥 SURGICAL SUMMARY")
    print(f"✅ Successful purges: {successful_purges}")
    print(f"❌ Failed purges: {failed_purges}")
    print(f"📁 Backups saved to: {backup_dir}")
    
    if successful_purges > 0:
        print(f"\n🎉 PHASE 1 PURGE: {successful_purges} files surgically cleaned!")
        print("🔬 Next: Run validation tests to confirm GPU memory service works")
        return 0
    else:
        print(f"\n💀 PURGE FAILED: No files successfully cleaned")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 