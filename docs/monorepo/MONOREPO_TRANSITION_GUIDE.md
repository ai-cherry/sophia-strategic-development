# Monorepo Transition Guide

## 🚨 IMPORTANT: Quality-First Transition Approach

**Status**: We are carefully transitioning to a monorepo structure, prioritizing stability and code quality for CEO operations.

**Development Context**:
- Primary User: CEO (sole user for 3+ months)
- Priority: Zero disruption to current functionality
- Approach: Careful, tested migration with no breaking changes

### Current State (December 2024)

The project has **TWO directory structures coexisting**:

#### 1. Old Structure (Still Active)
```
sophia-main/
├── backend/              # Current Python services
│   ├── agents/          # AI agents
│   ├── api/             # API routes  
│   ├── services/        # Business logic
│   └── mcp_servers/     # MCP implementations
├── frontend/             # Current React frontend
├── mcp-servers/         # Standalone MCP servers
└── infrastructure/      # Pulumi IaC
```

#### 2. New Structure (Being Populated)
```
sophia-main/
├── apps/                # Monorepo applications
│   ├── api/            # Will contain backend/api
│   ├── frontend/       # Will contain frontend
│   ├── mcp-servers/    # Will contain all MCP servers
│   └── n8n-bridge/     # Will contain N8N integration
├── libs/                # Shared libraries
│   ├── ui/             # Shared UI components
│   ├── utils/          # Shared utilities
│   ├── types/          # Shared TypeScript types
│   └── core/           # Core business logic
└── config/             # Centralized configurations
```

### ⚠️ CRITICAL: Where to Put New Code

**For NOW (During Transition)**:
- Continue adding new code to the **OLD structure** (`backend/`, `frontend/`, etc.)
- The new structure is being prepared but is NOT yet active

**After Migration** (Target: February 2025):
- All new code will go in the **NEW structure** (`apps/`, `libs/`)
- Imports will change from `backend.core` to `libs.core`

### Why This Transition?

We're moving to a monorepo structure to achieve:
- **Build times**: 15-20 min → <5 min (with Turborepo caching)
- **CI/CD**: 15+ duplicate workflows → 5-10 reusable templates
- **Dependencies**: Unified management with UV (Python) and PNPM (JavaScript)
- **Developer Experience**: One-command setup, consistent tooling

### Migration Status

| Component | Current Location | Future Location | Status |
|-----------|-----------------|-----------------|--------|
| Backend API | `backend/api/` | `apps/api/` | 🔴 Not Started |
| Frontend | `frontend/` | `apps/frontend/` | 🔴 Not Started |
| MCP Servers | `mcp-servers/` | `apps/mcp-servers/` | 🔴 Not Started |
| Core Utils | `backend/core/` | `libs/core/` | 🔴 Not Started |
| Shared UI | N/A | `libs/ui/` | 🔴 Not Started |

### Tools Installed

✅ **Already Set Up**:
- Turborepo configuration (`turbo.json`)
- PNPM workspace (`pnpm-workspace.yaml`)
- Migration scripts (`scripts/monorepo/`)
- CI/CD templates (`.github/workflow-templates/`)

### For AI Coders

**IMPORTANT RULES**:

1. **Check Migration Status First**
   - Look at this file to see which components have been migrated
   - If not migrated, use the OLD structure

2. **Don't Create Duplicate Code**
   - Don't add the same functionality in both old and new structures
   - Wait for official migration of each component

3. **Follow Import Patterns**
   - Old: `from backend.core.config import get_config_value`
   - New (after migration): `from libs.core.config import get_config_value`

4. **Use Existing Tools**
   - Python dependencies: UV (already configured in `pyproject.toml`)
   - JavaScript dependencies: NPM for now, PNPM after migration
   - Docker: Continue using existing Dockerfiles

### Migration Commands (For Reference)

When components are ready to migrate:
```bash
# Migrate a service (DO NOT RUN YET)
./scripts/monorepo/migrate-service.sh backend/api app

# Test the monorepo structure
pnpm turbo run echo --filter=api

# Bootstrap workspace (already done)
./scripts/monorepo/bootstrap-workspace.sh
```

### Timeline

- **Phase 0** ✅: Infrastructure setup (Complete)
- **Phase 1** 🔄: Planning & Design (Current - January 2025)
- **Phase 2**: Migration execution (February 2025)
- **Phase 3**: Testing & validation (March 2025)
- **Phase 4**: Cleanup old structure (April 2025)

### Questions?

If you're unsure where to put code:
1. Check the migration status table above
2. Default to the OLD structure if not migrated
3. Look for similar code and follow its pattern
4. The System Handbook remains authoritative for architecture

---

**Last Updated**: December 31, 2024  
**Next Review**: January 15, 2025 