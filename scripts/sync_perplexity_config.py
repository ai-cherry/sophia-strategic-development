#!/usr/bin/env python3
"""
Sync Perplexity MCP configuration from Pulumi ESC
"""
import json
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.auto_esc_config import EnhancedAutoESCConfig, get_config_value, logger


def sync_perplexity_configuration():
    """Sync Perplexity MCP configuration from Pulumi ESC"""
    try:
        # Initialize the enhanced config
        config = EnhancedAutoESCConfig()
        
        # Get Perplexity configuration
        perplexity_config = config.get_perplexity_config()
        
        if not perplexity_config.get('api_key'):
            logger.error("❌ No Perplexity API key found in Pulumi ESC")
            logger.info("Please set PERPLEXITY_API_KEY in Pulumi ESC")
            return False
        
        # Update environment variables
        os.environ['PERPLEXITY_API_KEY'] = perplexity_config['api_key']
        
        # Generate MCP configurations for different use cases
        mcp_servers = {
            "perplexity-coding": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-perplexity-ask"],
                "env": {
                    "PERPLEXITY_API_KEY": perplexity_config['api_key'],
                    "PERPLEXITY_MODEL": perplexity_config['model_preferences']['coding']
                }
            },
            "perplexity-business": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-perplexity-ask"],
                "env": {
                    "PERPLEXITY_API_KEY": perplexity_config['api_key'],
                    "PERPLEXITY_MODEL": perplexity_config['model_preferences']['business']
                }
            },
            "perplexity-research": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-perplexity-ask"],
                "env": {
                    "PERPLEXITY_API_KEY": perplexity_config['api_key'],
                    "PERPLEXITY_MODEL": perplexity_config['model_preferences']['research']
                }
            }
        }
        
        # Read current MCP configuration
        mcp_config_path = '.cursor/mcp.json'
        current_config = {"mcpServers": {}}
        
        if os.path.exists(mcp_config_path):
            try:
                with open(mcp_config_path, 'r') as f:
                    current_config = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read existing MCP config: {e}")
        
        # Update with Perplexity servers
        if 'mcpServers' not in current_config:
            current_config['mcpServers'] = {}
        
        current_config['mcpServers'].update(mcp_servers)
        
        # Create .cursor directory if it doesn't exist
        os.makedirs('.cursor', exist_ok=True)
        
        # Write updated configuration
        with open(mcp_config_path, 'w') as f:
            json.dump(current_config, f, indent=2)
        
        logger.info("✅ Perplexity MCP configuration synced from Pulumi ESC")
        logger.info(f"  - API Key: {'*' * 8}{perplexity_config['api_key'][-4:]}")
        logger.info(f"  - Coding Model: {perplexity_config['model_preferences']['coding']}")
        logger.info(f"  - Business Model: {perplexity_config['model_preferences']['business']}")
        logger.info(f"  - Research Model: {perplexity_config['model_preferences']['research']}")
        
        # Show settings
        settings = perplexity_config['settings']
        logger.info(f"  - Temperature: {settings['temperature']}")
        logger.info(f"  - Max Tokens: {settings['max_tokens']}")
        logger.info(f"  - Citations: {settings['return_citations']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to sync Perplexity configuration: {e}")
        return False


def main():
    """Main entry point"""
    # Activate virtual environment
    activate_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'activate_sophia_env.sh')
    if os.path.exists(activate_script):
        logger.info("🔧 Activating Sophia virtual environment...")
        os.system(f'source {activate_script}')
    
    # Sync configuration
    success = sync_perplexity_configuration()
    
    if success:
        logger.info("\n✨ Perplexity is now configured and ready to use!")
        logger.info("You can use the following MCP servers in Cursor:")
        logger.info("  - perplexity-coding: For code-related queries")
        logger.info("  - perplexity-business: For business intelligence")
        logger.info("  - perplexity-research: For in-depth research")
    else:
        logger.error("\n❌ Failed to configure Perplexity MCP servers")
        sys.exit(1)


if __name__ == "__main__":
    main()
