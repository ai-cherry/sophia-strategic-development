#!/usr/bin/env python3
"""
Clean up invalid dependencies from pyproject.toml
"""

import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Known invalid packages (local imports that were mistaken for packages)
INVALID_PACKAGES = {
    'agents', 'ai_service', 'analyze_call_sentiment', 'auto_esc_config',
    'backend', 'base', 'base_chat_service', 'base_handler', 'call',
    'call_participant', 'call_repository', 'cli', 'client', 'clients',
    'cline_v3_18_features', 'codacy_api_client', 'comprehensive_memory_manager',
    'config', 'contact', 'contact_repository', 'context_manager', 'core',
    'db_client', 'deal', 'deal_repository', 'docker', 'event_store',
    'examples', 'execute_strategic_plan', 'executive_chat_service',
    'faiss_manager', 'gemini_cli_integration', 'get_closed_ticket_conversations',
    'gong_data_quality', 'graphiti_mcp_server', 'handlers', 'hubspot_client',
    'lambda_labs_provisioner', 'lowlevel', 'manager', 'mcp_servers',
    'mcp_simple_auth', 'models', 'money', 'providers', 'qualify_deal',
    'resource_manager', 'router', 'sentiment', 'server', 'services',
    'session_manager', 'settings', 'shared', 'simple_auth_provider',
    'snowflake_call_repository', 'snowflake_mcp_server', 'sophia_chat_service',
    'sophia_mcp_base', 'sophia_universal_chat_service', 'templates',
    'token_verifier', 'tool_manager', 'unified_chat_service',
    'universal_chat_service', 'user', 'utilities', 'utils', 'write_detector',
    'dateutil', 'jose', 'pyjwt', 'pydantic_core', 'pydantic_settings',
    'sentence_transformers', 'typing_extensions', 'win32',
    # MCP server imports
    'mcp_server_fetch', 'mcp_server_git', 'mcp_server_hubspot',
    'mcp_server_snowflake', 'mcp_server_time',
    # Other invalid entries
    'git', 'n8n', 'inline_snapshot', 'pytest_examples',
    'langchain_openai', 'langgraph', 'msgpack',
    'opentelemetry', 'pydantic_ai', 'radon', 'readabilipy',
    'sqlglot', 'sqlparse', 'tzlocal', 'websockets',
}

# Packages to exclude (Flask and related)
EXCLUDE_PACKAGES = {
    'flask', 'flask-cors', 'flask-restful', 'flask-sqlalchemy',
    'gunicorn', 'werkzeug', 'itsdangerous',
}

# Packages with specific versions we want to keep
PACKAGE_VERSIONS = {
    'fastapi': '>=0.115.0',
    'uvicorn[standard]': '>=0.32.0',
    'pydantic': '>=2.10.0',
    'sqlalchemy': '>=2.0.23',
    'redis': '>=5.0.1',
    'anthropic': '>=0.25.0',
    'openai': '>=1.6.1',
    'snowflake-connector-python': '>=3.7.0',
    'httpx': '>=0.28.1',
    'pytest': '>=8.3.4',
    'black': '>=24.10.0',
    'ruff': '>=0.8.4',
    'mypy': '>=1.8.0',
}

def clean_dependencies():
    """Clean up the pyproject.toml file"""
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    # Find the dependencies section
    deps_match = re.search(r'dependencies = \[(.*?)\]', content, re.DOTALL)
    if not deps_match:
        logger.error("Could not find dependencies section")
        return
    
    deps_text = deps_match.group(1)
    deps_lines = deps_text.strip().split('\n')
    
    # Clean dependencies
    clean_deps = []
    for line in deps_lines:
        line = line.strip()
        if not line or line == ',':
            continue
        
        # Extract package name
        match = re.match(r'"([^">=<\[]+).*"', line)
        if not match:
            continue
        
        pkg_name = match.group(1).strip()
        
        # Skip invalid packages
        if pkg_name.lower() in INVALID_PACKAGES:
            logger.info(f"Removing invalid package: {pkg_name}")
            continue
        
        # Skip excluded packages
        if pkg_name.lower() in EXCLUDE_PACKAGES:
            logger.info(f"Excluding legacy package: {pkg_name}")
            continue
        
        # Skip packages marked as missing
        if "# MISSING" in line:
            logger.info(f"Skipping missing package: {pkg_name}")
            continue
        
        # Use specific version if available
        if pkg_name in PACKAGE_VERSIONS:
            clean_deps.append(f'    "{pkg_name}{PACKAGE_VERSIONS[pkg_name]}",')
        else:
            clean_deps.append(f'    {line.strip()}')
    
    # Remove trailing comma from last dependency
    if clean_deps and clean_deps[-1].endswith(','):
        clean_deps[-1] = clean_deps[-1][:-1]
    
    # Reconstruct dependencies section
    new_deps_text = '\n'.join(clean_deps)
    new_content = content.replace(deps_match.group(0), f'dependencies = [\n{new_deps_text}\n]')
    
    # Write back
    with open('pyproject.toml', 'w') as f:
        f.write(new_content)
    
    logger.info(f"Cleaned dependencies: {len(deps_lines)} -> {len(clean_deps)}")

if __name__ == "__main__":
    clean_dependencies() 