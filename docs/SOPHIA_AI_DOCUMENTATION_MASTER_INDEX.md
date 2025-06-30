# Sophia AI Documentation Master Index

## 🎯 Quick Navigation

### 🚀 Getting Started
- [Quick Start Guide](01-getting-started/README.md)
- [Development Environment Setup](getting-started/DEVELOPMENT_ENVIRONMENT_SETUP.md)
- [Local Development Guide](getting-started/LOCAL_DEVELOPMENT_GUIDE.md)

### 🏗️ Architecture & Development
- [Clean Architecture Guide](03-architecture/SOPHIA_AI_CLEAN_ARCHITECTURE_GUIDE.md)
- [Phase 1 Implementation Report](architecture/PHASE_1_IMPLEMENTATION_REPORT.md)
- [Advanced Data Processing Strategy](ADVANCED_DATA_PROCESSING_STRATEGY.md)

### 🔐 Secret Management (CURRENT SYSTEM)
**✅ ACTIVE: Complete GitHub Organization Secrets Integration**
- **Primary Script**: `scripts/ci/sync_from_gh_to_pulumi.py` (67 secrets mapped)
- **Workflow**: `.github/workflows/sync_secrets.yml` (auto-sync)
- **Backend**: `backend/core/auto_esc_config.py` (top-level access)
- **Verification**: `verify_complete_secrets_sync.py`
- **Audit Tool**: `comprehensive_secrets_audit.py`

**🔄 Process**: GitHub Organization Secrets → GitHub Actions → Pulumi ESC → Backend

### 🔧 Development Tools
- [AI Coder Reference](AI_CODER_REFERENCE.md)
- [Natural Language Commands](ai-coding/NATURAL_LANGUAGE_COMMANDS.md)
- [Agent Service Reference](AGENT_SERVICE_REFERENCE.md)

### 🚀 Deployment
- [Clean Architecture Deployment](04-deployment/CLEAN_ARCHITECTURE_DEPLOYMENT.md)

### 🔌 Integrations
- [MCP Servers](06-mcp-servers/README.md)
- [Sample Queries](sample_queries/enhanced_sample_developer_queries.md)

### 🔢 Performance & Monitoring
- [Performance Optimization](07-performance/README.md)
- [Security Guidelines](08-security/README.md)

## 🎉 Recent Major Updates

### ✅ Complete GitHub Organization Secrets Alignment (Latest)
- **Status**: COMPLETE - All 67 secrets mapped and synced
- **Impact**: Eliminated persistent placeholder issues
- **Lambda Labs**: Ready for deployment
- **Business Intelligence**: All services accessible

## 🛠️ Active Scripts & Tools

### Secret Management
- `scripts/ci/sync_from_gh_to_pulumi.py` - **PRIMARY** sync script
- `verify_complete_secrets_sync.py` - Real-time verification
- `comprehensive_secrets_audit.py` - Complete audit tool

### Development
- `scripts/sync_dev_environment.py` - Environment sync

### Infrastructure
- `infrastructure/esc/` - Pulumi ESC configuration
- `infrastructure/vercel/` - Vercel deployment

## 📋 Quick Commands

### Secret Verification
```bash
# Verify all secrets synced
python verify_complete_secrets_sync.py

# Manual Pulumi check
pulumi config get lambda_api_key --stack sophia-ai-production
```

### Development
```bash
# Start development environment
./activate_sophia.sh

# Run backend
cd backend && python -m uvicorn app.fastapi_app:app --reload
```

## 📊 System Status

- **Secret Management**: ✅ Complete (67/67 secrets)
- **Backend Services**: ✅ Operational
- **Infrastructure**: ✅ Ready
- **Lambda Labs**: ✅ Ready for deployment

---

*Last Updated: 2025-06-29 - Complete GitHub Organization Secrets Alignment*
