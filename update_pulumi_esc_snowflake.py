#!/usr/bin/env python3
"""
Update Pulumi ESC Snowflake Configuration
Fix the configuration in Pulumi ESC to use correct values
"""

import subprocess
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_esc_config():
    """Update Pulumi ESC with correct Snowflake configuration"""
    
    logger.info("🔧 Updating Pulumi ESC Snowflake configuration...")
    
    # Get current ESC configuration
    try:
        result = subprocess.run([
            'pulumi', 'env', 'get', 'scoobyjava-org/default/sophia-ai-production', '--show-secrets'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logger.error(f"Failed to get ESC config: {result.stderr}")
            return False
            
        current_config = json.loads(result.stdout)
        logger.info("✅ Current ESC configuration retrieved")
        
        # Update Snowflake configuration
        updates = {
            'snowflake_account': 'ZNB04675',
            'snowflake_user': 'SCOOBYJAVA15', 
            'snowflake_database': 'SOPHIA_AI',
            'snowflake_warehouse': 'SOPHIA_AI_WH',
            'snowflake_role': 'ACCOUNTADMIN',
            'snowflake_schema': 'PROCESSED_AI'
        }
        
        # Apply updates
        for key, value in updates.items():
            if key in current_config:
                old_value = current_config[key]
                logger.info(f"   {key}: {old_value} → {value}")
            else:
                logger.info(f"   {key}: NEW → {value}")
        
        # Note: Pulumi ESC updates require manual intervention or API calls
        # For now, document the required changes
        logger.info("\n📝 REQUIRED ESC UPDATES:")
        logger.info("Run these commands manually:")
        
        for key, value in updates.items():
            logger.info(f"pulumi env set scoobyjava-org/default/sophia-ai-production {key} '{value}'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ESC update failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting Pulumi ESC Snowflake configuration update...")
    
    success = update_esc_config()
    
    if success:
        logger.info("✅ ESC update commands generated")
        logger.info("💡 Manual execution required for security")
    else:
        logger.error("❌ ESC update failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
