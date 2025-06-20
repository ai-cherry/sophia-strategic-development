# Repository Cleanup Plan
## Sophia AI Codebase Organization Strategy

### Current Issues
- **67 one-time scripts** in root directory
- **25+ one-time .md files** scattered throughout
- **Multiple duplicate/obsolete files** with similar functionality
- **Test files mixed with production code**
- **Configuration files not properly organized**

### Cleanup Strategy

## Phase 1: Archive Historical Files
Move completed migration and one-time files to `archive/` directory:

### Migration & Enhancement Files (COMPLETED - Archive)
```
archive/migrations/
├── enhanced_migration_report_enhanced-migration-1750480853.json
├── next_level_enhancement_report_next-level-1750481373.json
├── ENHANCED_MIGRATION_SUCCESS_REPORT.md
├── COMPLETE_TRANSFORMATION_SUMMARY.md
├── PULUMI_IDP_MIGRATION_PLAN.md
├── scripts/
│   ├── migrate_to_pulumi_idp.py
│   ├── enhanced_migration_with_improvements.py
│   └── implement_next_level_enhancements.py
```

### Validation Files (COMPLETED - Archive)
```
archive/validation/
├── CODEBASE_VALIDATION_PLAN.md
├── VALIDATION_COMPLETION_SUMMARY.md
├── validation_fixes_report.json
├── scripts/
│   ├── comprehensive_validation.sh
│   └── fix_validation_issues.py
```

### Historical Development Files (Archive)
```
archive/development/
├── enhanced_gong_integration_demo_20250617_143948.json
├── enhanced_gong_api_testing_20250617_153452.json
├── enhanced_gong_test_20250617_141528.json
├── enhanced_migration_report_enhanced-migration-1750480853.json
├── ai_memory_test_results.json
├── architecture_consistency_report.md
├── architecture_inconsistencies_report.md
├── architecture_migration_plan.md
├── architecture_migration_report.md
├── architecture_migration_summary.md
```

## Phase 2: Consolidate One-Time Scripts

### Development Utilities (Keep in `scripts/dev/`)
```
scripts/dev/
├── setup_wizard.py
├── automated_health_check.py
├── test_infrastructure.py
├── validate_infrastructure.py
├── start_mcp_servers.py
└── load_env.py
```

### Deployment Scripts (Keep in `scripts/deploy/`)
```
scripts/deploy/
├── deploy_production_mcp.py
├── deploy_schema.py
├── start_all_services.sh
└── deploy_all_dashboards.py
```

### Integration Testing (Keep in `scripts/test/`)
```
scripts/test/
├── test_linear_integration.py
├── test_claude_as_code.py
├── test_integrations.py
├── test_ai_memory_deployment.py
└── unified_integration_test.py
```

## Phase 3: Remove Obsolete/Duplicate Files

### Files to DELETE (Obsolete/Duplicates)
```
# Obsolete Gong Integration Files (replaced by backend/integrations/gong/)
- advanced_gong_integration_prototype.py
- enhanced_gong_integration.py
- enhanced_gong_api_integration.py
- enhanced_gong_api_tester.py
- enhanced_gong_test.py
- gong_app_integration_analyzer.py
- gong_webhook_system.py
- gong_calls_api_fixed.py
- gong_api_alternative.py
- sophia_immediate_gong_extraction.py
- sophia_live_gong_integration.py
- sophia_fixed_gong_extraction.py
- sophia_updated_gong_extraction.py
- quick_setup_gong_integration.py

# Obsolete Setup/Configuration Files (replaced by infrastructure/)
- simplified_api_test.py
- manage_integrations.py
- setup_new_repo.py
- multitenant_gong_architecture.py
- fix_call_participation_mapping.py
- configure_github_secrets.py
- configure_github_org_secrets.py
- sophia_secrets.py
- import_secrets_to_github.py

# Obsolete Test Files (replaced by tests/ directory)
- test_mcp_client.py
- sophia_test_aggregator.py
- sophia_intelligence_test.py
- sophia_live_test_suite.py
- test_scripts.py
- test_setup.py

# Obsolete Admin/API Files (replaced by backend/app/)
- enhanced_sophia_admin_api.py
- sophia_admin_api.py
- enhanced_sophia_integration.py

# Obsolete Data Files (replaced by backend/data_connectors/)
- sophia_data_importer.py
- production_data_populator.py
- team_client_data_analysis.py
- schema_aligned_storage.py
- sophia_enhanced_schema.py

# Obsolete Fix Scripts (issues resolved)
- automated_health_check_fixed.py
- fix_database_storage.py
- fix_ssl_certificates.py
- fix_dependencies.py
- fix_sophia_insights.py
- run_with_ssl_fix.py
- unified_command_interface_fixed.py
- unified_command_interface.py

# Obsolete Retool Files (migration completed)
- build_retool_dashboards_modified.py
- retool_*.json files (move to archive/retool/)
- RETOOL_*.md files (move to archive/retool/)
```

## Phase 4: Organize Documentation

### Keep Essential Documentation in `docs/`
```
docs/
├── deployment/
│   ├── COMPLETE_DASHBOARD_DEPLOYMENT_GUIDE.md
│   └── CEO_DASHBOARD_DEPLOYMENT_GUIDE.md
├── guides/
│   ├── SECRET_MANAGEMENT_GUIDE.md
│   ├── AUTOMATED_SECRET_SYNC_GUIDE.md
│   └── AI_MEMORY_DEPLOYMENT_GUIDE.md
└── reference/
    ├── complete_command_reference_guide.md
    ├── advanced_workflow_automation_commands.md
    └── claude_mcp_integration_commands.md
```

### Archive Completed Documentation
```
archive/docs/
├── retool/
│   ├── RETOOL_DASHBOARDS_EXPORT_GUIDE.md
│   ├── RETOOL_DASHBOARDS_DEPLOYMENT_GUIDE.md
│   └── retool_*.json files
├── migration/
│   ├── api_connection_iac_strategy.md
│   └── enhanced_sophia_database_integration_plan.md
└── historical/
    ├── cursor_ai_optimization_prompt.md
    └── cursor_claude_pulumi_command_guide.md
```

## Phase 5: Clean Configuration

### Consolidate Configuration Files
```
config/
├── environment/
│   ├── env.template
│   └── env.example
├── services/
│   ├── portkey.json
│   └── pulumi-mcp.json
└── dashboards/
    └── dashboard_config.json
```

## Phase 6: Final File Structure

### Target Clean Structure
```
sophia-main/
├── backend/                 # Core application code
├── frontend/               # UI components
├── infrastructure/         # IaC and deployment
├── tests/                 # All test files
├── docs/                  # Essential documentation
├── scripts/               # Organized utility scripts
│   ├── dev/              # Development utilities
│   ├── deploy/           # Deployment scripts
│   └── test/             # Test scripts
├── config/               # Configuration files
├── examples/             # Example implementations
└── archive/              # Historical/completed files
    ├── migrations/       # Completed migrations
    ├── validation/       # Completed validations
    ├── development/      # Historical development files
    ├── retool/          # Retool migration artifacts
    └── docs/            # Archived documentation
```

## Implementation Commands

### 1. Create Archive Structure
```bash
mkdir -p archive/{migrations,validation,development,retool,docs}
mkdir -p scripts/{dev,deploy,test}
mkdir -p config/{environment,services,dashboards}
mkdir -p docs/{deployment,guides,reference}
```

### 2. Move Files to Archive
```bash
# Migration files
mv *migration* archive/migrations/
mv PULUMI_IDP_MIGRATION_PLAN.md archive/migrations/
mv scripts/migrate_to_pulumi_idp.py archive/migrations/scripts/
mv scripts/enhanced_migration_with_improvements.py archive/migrations/scripts/
mv scripts/implement_next_level_enhancements.py archive/migrations/scripts/

# Validation files
mv CODEBASE_VALIDATION_PLAN.md archive/validation/
mv VALIDATION_COMPLETION_SUMMARY.md archive/validation/
mv validation_fixes_report.json archive/validation/
mv scripts/comprehensive_validation.sh archive/validation/scripts/
mv scripts/fix_validation_issues.py archive/validation/scripts/

# Retool files
mv retool_* archive/retool/
mv RETOOL_* archive/retool/
```

### 3. Delete Obsolete Files
```bash
# Remove obsolete Gong integration files
rm -f advanced_gong_integration_prototype.py enhanced_gong_integration.py
rm -f enhanced_gong_api_integration.py enhanced_gong_api_tester.py
# ... (continue with full list)
```

### 4. Organize Remaining Scripts
```bash
# Move development utilities
mv setup_wizard.py scripts/dev/
mv automated_health_check.py scripts/dev/
mv test_infrastructure.py scripts/dev/

# Move deployment scripts
mv deploy_production_mcp.py scripts/deploy/
mv deploy_schema.py scripts/deploy/
```

## Benefits of Cleanup

### Immediate Benefits
- **Reduced repository size** by ~40%
- **Improved navigation** and code discovery
- **Cleaner git history** with relevant files
- **Faster IDE indexing** and search
- **Better new developer onboarding**

### Long-term Benefits
- **Maintainable codebase** with clear organization
- **Reduced technical debt** from obsolete files
- **Improved CI/CD performance** with fewer files to process
- **Better documentation structure** for reference
- **Preserved historical context** in organized archive

## Execution Timeline
- **Phase 1-2:** 30 minutes (archive and organize)
- **Phase 3:** 15 minutes (delete obsolete files)
- **Phase 4-5:** 20 minutes (organize docs and config)
- **Phase 6:** 10 minutes (final validation)
- **Total:** ~75 minutes for complete cleanup

This cleanup will transform the repository from a cluttered development workspace into a clean, professional codebase ready for production use and team collaboration.
