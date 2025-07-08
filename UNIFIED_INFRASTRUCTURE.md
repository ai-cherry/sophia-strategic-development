# Sophia AI Unified Infrastructure

## Overview

The **Unified Infrastructure** represents the single, authoritative approach for all Sophia AI components. If it's not "Unified", it's legacy and should be migrated or removed.

## ✅ Unified Components (Current Standard)

### 1. **Unified Chat** (`backend/services/unified_chat_service.py`)
- Single chat interface for all AI interactions
- Integrates all data sources (Snowflake, AI Memory, Knowledge Base)
- Natural language query processing

### 2. **Unified Dashboard** (`frontend/src/components/dashboard/UnifiedDashboard.tsx`)
- Single dashboard component for all views
- No separate dashboards - everything extends UnifiedDashboard
- Tabbed interface for different features

### 3. **Unified Secret Management**
- **Sync Script**: `scripts/unified_secret_sync.py`
- **Docker Secrets**: `unified_docker_secrets.sh`
- **Strategy Doc**: `UNIFIED_SECRET_MANAGEMENT_STRATEGY.md`
- **Workflow**: `.github/workflows/sync_secrets.yml` → Unified Secret Sync

### 4. **Unified Deployment**
- **Deploy Script**: `unified_deployment.sh`
- **Monitoring**: `unified_monitoring.sh`
- **Troubleshooting**: `unified_troubleshooting.sh`
- **Docker Compose**: `docker-compose.cloud.yml`

### 5. **Unified API Client** (`frontend/src/services/apiClient.js`)
- Single API client for all frontend requests
- No separate API clients per feature

### 6. **Unified KPI Card** (`frontend/src/components/dashboard/UnifiedKPICard.tsx`)
- Single component for all KPI displays
- Configurable for different metrics

## ❌ Legacy Components (To Be Removed/Migrated)

### Scripts Directory Cleanup Needed:
```bash
# Legacy secret management (DELETE ALL)
scripts/ci/sync_from_gh_to_pulumi.py  # → Use unified_secret_sync.py
scripts/sync_secrets_to_esc.py         # → Use unified_secret_sync.py
scripts/test_esc_secrets.py            # → Use test_secret_access.py
create_docker_secrets.sh               # → Use unified_docker_secrets.sh

# Legacy deployment scripts (DELETE ALL)
scripts/deploy_to_lambda.sh            # → Use unified_deployment.sh
scripts/setup_docker_swarm.sh          # → Use unified_deployment.sh
scripts/k3s_deploy.sh                  # → Use unified_deployment.sh
deploy_production_complete.sh          # → Use unified_deployment.sh

# Legacy monitoring (DELETE ALL)
scripts/check_swarm_health.sh          # → Use unified_monitoring.sh
scripts/monitor_k3s.sh                 # → Use unified_monitoring.sh
```

### Backend Services Cleanup:
```bash
# Legacy chat services (DELETE ALL)
backend/services/chat_service.py       # → Use unified_chat_service.py
backend/services/ai_chat_service.py    # → Use unified_chat_service.py
backend/services/simple_chat.py        # → Use unified_chat_service.py

# Legacy API routes (CONSOLIDATE)
backend/api/chat_routes.py             # → Integrate into unified routes
backend/api/ai_routes.py               # → Integrate into unified routes
```

### Frontend Components Cleanup:
```bash
# Legacy dashboards (DELETE ALL)
frontend/src/components/CEODashboard.tsx    # → Use UnifiedDashboard
frontend/src/components/AdminDashboard.tsx  # → Use UnifiedDashboard
frontend/src/components/SimpleDashboard.tsx # → Use UnifiedDashboard

# Legacy KPI components (DELETE ALL)
frontend/src/components/KPICard.tsx         # → Use UnifiedKPICard
frontend/src/components/MetricCard.tsx      # → Use UnifiedKPICard
```

## 🔄 Migration Checklist

### Phase 1: Immediate Actions
- [ ] Delete all legacy secret management scripts
- [ ] Delete all legacy deployment scripts
- [ ] Update all documentation to reference unified components
- [ ] Update README.md to highlight unified approach

### Phase 2: Code Consolidation
- [ ] Migrate remaining chat services to unified_chat_service
- [ ] Consolidate all API routes
- [ ] Remove duplicate dashboard components
- [ ] Update all imports to use unified components

### Phase 3: Documentation Update
- [ ] Update all docs to reference unified components
- [ ] Create migration guide for developers
- [ ] Update onboarding documentation
- [ ] Archive legacy documentation

## 📋 Unified Naming Convention

All new components MUST follow this pattern:
- `unified_[component].py` for Python files
- `Unified[Component].tsx` for React components
- `unified-[component].yml` for config files
- `unified_[component].sh` for shell scripts

## 🚀 Benefits of Unified Approach

1. **Clarity**: Immediately obvious what's current vs legacy
2. **Consistency**: Single approach for each concern
3. **Maintainability**: No duplicate code or confusion
4. **Onboarding**: New developers know exactly what to use
5. **Cleanup**: Easy to identify and remove legacy code

## 📝 Implementation Status

| Component | Unified Version | Legacy Versions | Status |
|-----------|----------------|-----------------|---------|
| Chat Service | ✅ unified_chat_service.py | 3+ legacy versions | Ready |
| Dashboard | ✅ UnifiedDashboard.tsx | 3+ legacy versions | Ready |
| Secret Sync | ✅ unified_secret_sync.py | 2+ legacy versions | Ready |
| Deployment | ✅ unified_deployment.sh | 4+ legacy versions | Ready |
| Monitoring | ✅ unified_monitoring.sh | 2+ legacy versions | Ready |
| API Client | ✅ apiClient.js | Multiple versions | Ready |
| Docker Secrets | ✅ unified_docker_secrets.sh | 2+ legacy versions | Ready |

## 🎯 Next Steps

1. **Immediate**: Run cleanup script to remove all legacy files
2. **This Week**: Update all imports and references
3. **Next Week**: Full documentation update
4. **Month End**: Complete migration verification

## ⚠️ Important Rules

1. **No New Non-Unified Components**: Everything new must be "unified"
2. **No Duplicate Functionality**: One unified solution per problem
3. **Delete Legacy Code**: Don't keep "just in case" - we have git
4. **Update Imports**: All code must use unified components
5. **Document Decisions**: Update this file when adding unified components

---

**Remember**: If it's not "Unified", it's legacy and needs to go!
