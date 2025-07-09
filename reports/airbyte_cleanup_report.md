# Airbyte to Estuary Flow Cleanup Report

Generated: 2025-07-08 15:50:36

## Summary
- Files updated: 4
- Total replacements: 28
- Backup location: airbyte_cleanup_backup_20250708_155036

## Files Updated

- infrastructure/snowflake_setup/apollo_io_schema.sql
- reports/airbyte_references_report.md
- scripts/cleanup_airbyte_references.py
- scripts/cleanup_outdated_models.py

## Replacement Patterns

| Old Pattern | New Pattern |
|-------------|-------------|
| RAW_AIRBYTE | RAW_ESTUARY |
| raw_airbyte | raw_estuary |
| AIRBYTE_INTERNAL | ESTUARY_INTERNAL |
| airbyte_internal | estuary_internal |
| _AIRBYTE_ | _ESTUARY_ |
| _airbyte_ | _estuary_ |
| AirbyteGongOrchestrator | EstuaryFlowOrchestrator |
| AirbyteConfiguration | EstuaryFlowConfiguration |
| AirbyteIntegration | EstuaryFlowIntegration |
| airbyte_configuration_manager | estuary_flow_configuration_manager |
| airbyte_gong_setup | estuary_flow_gong_setup |
| AIRBYTE_API_KEY | ESTUARY_API_KEY |
| AIRBYTE_API_TOKEN | ESTUARY_API_TOKEN |
| LAMBDA_AIRBYTE_TOKEN | ESTUARY_FLOW_TOKEN |
| AIRBYTE_HOST | ESTUARY_HOST |
| AIRBYTE_PORT | ESTUARY_PORT |
| Airbyte integration | Estuary Flow integration |
| Airbyte connector | Estuary Flow connector |
| Airbyte pipeline | Estuary Flow pipeline |
| Airbyte sync | Estuary Flow sync |
