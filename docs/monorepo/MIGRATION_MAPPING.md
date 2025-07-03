# Migration Mapping

## Directory Mapping

| Current Location | New Location | Status |
|-----------------|--------------|--------|
| `backend/api/` | `apps/api/` | Pending |
| `backend/agents/` | `apps/api/src/agents/` | Pending |
| `backend/services/` | `apps/api/src/services/` | Pending |
| `frontend/` | `apps/frontend/` | Pending |
| `mcp-servers/` | `apps/mcp-servers/` | Pending |
| `backend/utils/` | `libs/utils/` | Pending |
| `backend/core/` | `libs/core/` | Pending |

## Import Updates Required

### Python Imports
- `from backend.core.x` → `from libs.core.x`
- `from backend.utils.x` → `from libs.utils.x`

### TypeScript Imports
- `from '../components'` → `from '@sophia-ai/ui'`
- `from '../utils'` → `from '@sophia-ai/utils'`

## Configuration Files

### To Centralize
- ESLint configs → `/config/eslint/`
- Prettier config → `/config/prettier/`
- TypeScript configs → `/config/typescript/`
- Ruff config → `/config/ruff/`
