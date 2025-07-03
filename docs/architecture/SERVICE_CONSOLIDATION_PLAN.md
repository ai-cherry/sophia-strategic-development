# Service Consolidation Plan

## Summary
Analyzed service files and found opportunities for consolidation.

## Service Groups

### Snowflake Services (14 files)
- backend/services/snowflake_intelligence_service.py
- backend/services/snowflake_metadata_optimizer.py
- backend/services/enhanced_snowflake_cortex_service.py
- backend/services/snowflake_admin_chat_integration.py
- backend/services/snowflake_admin_chat_integration.py
- backend/services/snowflake_admin_chat_integration.py
- backend/services/snowflake_admin_chat_integration.py
- backend/core/aligned_snowflake_config.py
- backend/core/aligned_snowflake_config.py
- backend/core/secure_snowflake_config.py
- ... and 4 more

### Memory Services (10 files)
- backend/services/graph_memory_service.py
- backend/services/comprehensive_memory_service.py
- backend/services/memory_preservation_service.py
- backend/services/memory_preservation_service.py
- backend/services/memory_preservation_service.py
- backend/services/memory_preservation_service.py
- backend/core/comprehensive_memory_manager.py
- backend/core/simple_mcp_base.py
- backend/core/hierarchical_cache.py
- backend/core/contextual_memory_intelligence.py

### Chat Services (13 files)
- backend/services/enhanced_chat_context_service.py
- backend/services/enhanced_ceo_universal_chat_service.py
- backend/services/enhanced_ceo_universal_chat_service.py
- backend/services/enhanced_ceo_universal_chat_service.py
- backend/services/chat_driven_metadata_service.py
- backend/services/enhanced_ceo_chat_service.py
- backend/services/enhanced_ceo_chat_service.py
- backend/services/enhanced_ceo_chat_service.py
- backend/services/enhanced_ceo_chat_service.py
- backend/services/chat/base_chat_service.py
- ... and 3 more

### Config Services (33 files)
- backend/services/mcp_orchestration_service.py
- backend/services/enhanced_portkey_orchestrator.py
- backend/services/enhanced_data_ingestion.py
- backend/services/snowflake_metadata_optimizer.py
- backend/services/cortex_agent_service.py
- backend/services/cost_engineering_service.py
- backend/services/enhanced_snowflake_cortex_service.py
- backend/services/enhanced_snowflake_cortex_service.py
- backend/services/portkey_gateway.py
- backend/services/snowflake/connection_pool_manager.py
- ... and 23 more

### Connection Services (16 files)
- backend/services/snowflake/pooled_connection.py
- backend/services/snowflake/connection_pool_manager.py
- backend/services/snowflake/connection_pool_manager.py
- backend/core/optimized_connection_manager.py
- backend/core/optimized_connection_manager.py
- backend/core/optimized_connection_manager.py
- backend/core/optimized_connection_manager.py
- backend/core/optimized_connection_manager.py
- backend/core/optimized_connection_manager.py
- backend/core/unified_connection_manager.py
- ... and 6 more

## Consolidation Recommendations

### Config Services
Current: 33 separate files
Suggested structure:
- `backend/core/config/base.py`: Base configuration interfaces
- `backend/core/config/manager.py`: Main configuration manager
- `backend/core/config/snowflake.py`: Snowflake-specific config
- `backend/core/config/integrations.py`: Integration configs

### Connection Services
Current: 16 separate files
Suggested structure:
- `backend/core/connections/base.py`: Base connection interface
- `backend/core/connections/pool.py`: Connection pooling
- `backend/core/connections/snowflake.py`: Snowflake connections
- `backend/core/connections/external.py`: External service connections

## High-Priority Duplicates

### snowflake_admin_chat_integration.py ↔ snowflake_admin_chat_integration.py
- Type: snowflake
- Overlap: 100.0%
- Common methods: _format_admin_response, extract_entities, is_admin_query, parse_admin_query, classify_admin_intent

### snowflake_admin_chat_integration.py ↔ snowflake_admin_chat_integration.py
- Type: snowflake
- Overlap: 100.0%
- Common methods: _format_admin_response, extract_entities, is_admin_query, parse_admin_query, classify_admin_intent

### snowflake_admin_chat_integration.py ↔ snowflake_admin_chat_integration.py
- Type: snowflake
- Overlap: 100.0%
- Common methods: _format_admin_response, extract_entities, is_admin_query, parse_admin_query, classify_admin_intent

### snowflake_admin_chat_integration.py ↔ snowflake_admin_chat_integration.py
- Type: snowflake
- Overlap: 100.0%
- Common methods: _format_admin_response, extract_entities, is_admin_query, parse_admin_query, classify_admin_intent

### snowflake_admin_chat_integration.py ↔ snowflake_admin_chat_integration.py
- Type: snowflake
- Overlap: 100.0%
- Common methods: _format_admin_response, extract_entities, is_admin_query, parse_admin_query, classify_admin_intent

### snowflake_admin_chat_integration.py ↔ snowflake_admin_chat_integration.py
- Type: snowflake
- Overlap: 100.0%
- Common methods: _format_admin_response, extract_entities, is_admin_query, parse_admin_query, classify_admin_intent

### aligned_snowflake_config.py ↔ aligned_snowflake_config.py
- Type: snowflake
- Overlap: 100.0%
- Common methods: get_analytics_views, get_vector_search_config, validate_connection, _validate_setup, get_connection_params_for_schema

### memory_preservation_service.py ↔ memory_preservation_service.py
- Type: memory
- Overlap: 100.0%
- Common methods: _get_system_analytics, __init__, _calculate_embedding_similarity, _get_batch_analytics, __post_init__

### memory_preservation_service.py ↔ memory_preservation_service.py
- Type: memory
- Overlap: 100.0%
- Common methods: _get_system_analytics, __init__, _calculate_embedding_similarity, _get_batch_analytics, __post_init__

### memory_preservation_service.py ↔ memory_preservation_service.py
- Type: memory
- Overlap: 100.0%
- Common methods: _get_system_analytics, __init__, _calculate_embedding_similarity, _get_batch_analytics, __post_init__
