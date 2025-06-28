# Function Length Compliance Report

## Summary
- **Total Functions Analyzed**: 5,007
- **Functions Exceeding 50 Lines**: 758
- **Compliance Rate**: 84.9%
- **Average Function Length**: 28.9 lines

## Top Violations (Longest Functions)

| Function | Lines | File | Complexity |
|----------|-------|------|------------|
| `deploy_asana_transformation_procedures` | 390 | `./backend/scripts/deploy_asana_snowflake_setup.py` | 1 |
| `enhance_sophia_intelligence_mcp` | 325 | `./scripts/mcp_orchestration_optimizer.py` | 1 |
| `create_chrome_extension` | 298 | `./setup_enhanced_coding_workflow.py` | 1 |
| `_initialize_patterns` | 292 | `./backend/mcp_servers/ai_memory_auto_discovery.py` | 1 |
| `setup_handlers` | 279 | `./mcp-servers/notion/notion_mcp_server.py` | 13 |
| `create_transformation_procedures` | 246 | `./backend/etl/netsuite/estuary_netsuite_setup.py` | 2 |
| `setup_handlers` | 246 | `./mcp-servers/linear/linear_mcp_server.py` | 12 |
| `setup_handlers` | 246 | `./mcp-servers/asana/asana_mcp_server.py` | 12 |
| `demo_enhanced_workflow` | 239 | `./example_enhanced_workflow.py` | 12 |
| `prepare_vscode_integration` | 235 | `./setup_enhanced_coding_workflow.py` | 1 |
| `handle_list_tools` | 235 | `./mcp-servers/notion/notion_mcp_server.py` | 1 |
| `process_call_webhook` | 217 | `./backend/integrations/gong_webhook_processor.py` | 9 |
| `generate_coaching_recommendations` | 215 | `./backend/agents/specialized/sales_coach_agent.py` | 19 |
| `__init__` | 209 | `./scripts/enhanced_batch_embed_data.py` | 1 |
| `handle_list_tools` | 204 | `./mcp-servers/linear/linear_mcp_server.py` | 1 |
| `handle_list_tools` | 204 | `./mcp-servers/asana/asana_mcp_server.py` | 1 |
| `create_flow_yaml` | 202 | `./deploy_estuary_foundation_corrected.py` | 1 |
| `vector_search_business_table` | 202 | `./backend/utils/snowflake_cortex_service.py` | 29 |
| `store_gong_call_insight` | 200 | `./backend/mcp_servers/enhanced_ai_memory_mcp_server.py` | 27 |
| `deploy_asana_ai_enrichment_procedures` | 196 | `./backend/scripts/deploy_asana_snowflake_setup.py` | 1 |

... and 738 more violations

## Compliance by File Type

- **Other**: 84.1% (94/593 violations)
- **MCP Servers**: 81.9% (38/210 violations)
- **Infrastructure**: 95.7% (1/23 violations)
- **Backend**: 86.4% (450/3301 violations)
- **Scripts**: 80.1% (175/880 violations)

## Recommendations

### Immediate Actions (>100 lines)
- Refactor `deploy_asana_transformation_procedures` in `./backend/scripts/deploy_asana_snowflake_setup.py` (390 lines)
- Refactor `enhance_sophia_intelligence_mcp` in `./scripts/mcp_orchestration_optimizer.py` (325 lines)
- Refactor `create_chrome_extension` in `./setup_enhanced_coding_workflow.py` (298 lines)
- Refactor `_initialize_patterns` in `./backend/mcp_servers/ai_memory_auto_discovery.py` (292 lines)
- Refactor `setup_handlers` in `./mcp-servers/notion/notion_mcp_server.py` (279 lines)
- Refactor `create_transformation_procedures` in `./backend/etl/netsuite/estuary_netsuite_setup.py` (246 lines)
- Refactor `setup_handlers` in `./mcp-servers/linear/linear_mcp_server.py` (246 lines)
- Refactor `setup_handlers` in `./mcp-servers/asana/asana_mcp_server.py` (246 lines)
- Refactor `demo_enhanced_workflow` in `./example_enhanced_workflow.py` (239 lines)
- Refactor `prepare_vscode_integration` in `./setup_enhanced_coding_workflow.py` (235 lines)

### Refactoring Patterns
1. **Extract Method**: Break large functions into smaller, focused methods
2. **Template Method**: Use structured initialization for large `__init__` methods
3. **Builder Pattern**: For complex object construction
4. **Configuration Objects**: Replace long parameter lists

### Tools and Automation
1. **Pre-commit Hook**: Add this checker to prevent new violations
2. **IDE Integration**: Use "Extract Method" refactoring tools
3. **Regular Monitoring**: Run weekly compliance reports
4. **Team Training**: Share refactoring best practices

### Success Metrics
- Target: <5% violation rate (currently 15.1%)
- Maximum function length: 75 lines
- Average function length: <30 lines
