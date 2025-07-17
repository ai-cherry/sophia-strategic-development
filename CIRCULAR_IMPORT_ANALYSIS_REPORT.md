
# 🔍 CIRCULAR IMPORT ANALYSIS REPORT

## Summary
- **Modules analyzed**: 33
- **Circular import cycles found**: 0
- **Problematic modules**: 1
- **Long dependency chains**: 20

## 🚨 Circular Import Cycles

✅ No circular import cycles detected!


## ⚠️ Problematic Modules


### backend.services.unified_memory_service
- **File**: `backend/services/unified_memory_service.py`
- **Complexity Score**: 11.0
- **Direct Dependencies**: 6
- **Issues**: High complexity


## 🔗 Long Dependency Chains


### Chain 1
backend.services.unified_memory_service → mcp_servers.postgresql.structured_data_store → backend.core.auto_esc_config → backend.core.config.service_configs → backend.core.config.secret_manager → backend.core.config.base_config

### Chain 2
backend.services.unified_memory_service → mcp_servers.postgresql.structured_data_store → backend.core.auto_esc_config → backend.core.config.config_container → backend.core.config.secret_manager → backend.core.config.base_config

### Chain 3
backend.services.unified_memory_service → mcp_servers.postgresql.structured_data_store → backend.core.auto_esc_config → backend.core.config.config_container → backend.core.config.service_configs → backend.core.config.secret_manager

### Chain 4
backend.services.unified_memory_service → backend.services.lambda_inference_service → backend.core.auto_esc_config → backend.core.config.service_configs → backend.core.config.secret_manager → backend.core.config.base_config

### Chain 5
backend.services.unified_memory_service → backend.services.lambda_inference_service → backend.core.auto_esc_config → backend.core.config.config_container → backend.core.config.secret_manager → backend.core.config.base_config
