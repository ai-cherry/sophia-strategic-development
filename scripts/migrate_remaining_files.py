import os
import subprocess
from pathlib import Path

def migrate_remaining_files():
    """Migrate remaining files from backend directory"""
    
    # Define mappings for remaining directories
    remaining_mappings = {
        'backend/websocket': 'infrastructure/websocket',
        'backend/core': 'core',  # Most core files should go to core
        'backend/database': 'infrastructure/database',
        'backend/scripts': 'scripts/backend',
        'backend/app': 'api/app',
        'backend/n8n_bridge': 'infrastructure/n8n_bridge',
        'backend/agents': 'core/agents',  # Remaining agent files
        'backend/infrastructure': 'infrastructure',
        'backend/etl': 'infrastructure/etl',  # Any remaining ETL files
        'backend/api': 'api',  # Any remaining API files
        'backend/snowflake_setup': 'infrastructure/snowflake_setup',
        'backend/rag': 'shared/rag',
    }
    
    # Special handling for core files that should go to infrastructure
    infra_core_files = [
        'snowflake_production_config.py',
        'snowflake_config_manager.py',
        'optimized_connection_manager.py',
        'database.py',
        'comprehensive_memory_manager.py',
        'enhanced_cache_manager.py',
        'snowflake_abstraction.py',
        'snowflake_schema_integration.py',
        'snowflake_config_override.py',
        'unified_connection_manager.py',
        'hierarchical_cache.py',
        'secure_snowflake_config.py',
        'optimized_database_manager.py',
        'snowflake_override.py',
        'connection_pool.py',
        'enhanced_snowflake_config.py',
        'comprehensive_snowflake_config.py',
        'real_time_streaming.py',
        'snowflake_production_config.py',
        'database.py',
        'snowflake_abstraction.py',
        'snowflake_schema_integration.py',
        'snowflake_config_override.py',
        'unified_connection_manager.py',
        'connection_pool.py'
    ]
    
    # Shared core files
    shared_core_files = [
        'auth.py',
        'config_manager.py',
        'security.py',
        'auto_esc_config.py',
        'security_config.py',
        'dependencies.py'
    ]
    
    moved_count = 0
    
    # Process each remaining file
    for root, dirs, files in os.walk('backend'):
        if '__pycache__' in root:
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
                
            old_path = os.path.join(root, file)
            
            # Determine destination
            destination = None
            
            # Check if it's a core file that should go to infrastructure
            if 'backend/core' in root and file in infra_core_files:
                destination = old_path.replace('backend/core', 'infrastructure/core')
            elif 'backend/core' in root and file in shared_core_files:
                destination = old_path.replace('backend/core', 'shared')
            else:
                # Use general mappings
                for old_prefix, new_prefix in remaining_mappings.items():
                    if root.startswith(old_prefix):
                        destination = old_path.replace(old_prefix, new_prefix)
                        break
            
            if destination:
                # Create destination directory
                dest_dir = os.path.dirname(destination)
                os.makedirs(dest_dir, exist_ok=True)
                
                # Move file
                try:
                    subprocess.run(['git', 'mv', old_path, destination], check=True)
                    print(f"Moved: {old_path} -> {destination}")
                    moved_count += 1
                except subprocess.CalledProcessError:
                    try:
                        os.rename(old_path, destination)
                        print(f"Moved (non-git): {old_path} -> {destination}")
                        moved_count += 1
                    except Exception as e:
                        print(f"Error moving {old_path}: {e}")
    
    print(f"\nMoved {moved_count} files")
    
    # Check if backend directory is empty
    remaining = list(Path('backend').rglob('*.py'))
    if remaining:
        print(f"\nWarning: {len(remaining)} Python files still remain in backend/")
        for f in remaining[:10]:
            print(f"  - {f}")
    else:
        print("\nAll Python files have been migrated from backend/")

if __name__ == '__main__':
    migrate_remaining_files() 