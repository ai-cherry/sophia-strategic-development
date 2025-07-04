# Sophia AI Application Structure

## Overview

As of January 2025, Sophia AI has been consolidated to use a single, unified application entry point. This document explains the current application structure and how to use it.

## Application Entry Points

### Production Application
- **File**: `backend/app/app.py`
- **Purpose**: Main production application - THE ONLY PRODUCTION ENTRY POINT
- **Usage**: `uvicorn backend.app.app:app --host 0.0.0.0 --port 8000`
- **Features**:
  - Unified chat service
  - Knowledge management
  - LLM orchestration
  - Health monitoring
  - All API routes under `/api/v1`

### Testing Application
- **File**: `backend/app/simple_app.py`
- **Purpose**: Minimal app for testing basic connectivity and environment
- **Usage**: `uvicorn backend.app.simple_app:app --host 0.0.0.0 --port 8000`
- **Features**:
  - Basic health check
  - Environment verification
  - No dependencies on services

## Archived Applications

The following applications have been archived and should NOT be used:

### Located in `backend/app/archive/`
- `main.py` - Original entry point (outdated)
- `enhanced_minimal_app.py` - LangChain enhancement attempt (incomplete)
- `unified_fastapi_app.py` - Over-engineered attempt (too complex)
- `fastapi_app.py` - Early iteration (fragmented)

These files are kept for historical reference only.

## Docker Configuration

All Dockerfiles should reference the production app:

```dockerfile
CMD ["uvicorn", "backend.app.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Development Workflow

### Running Locally
```bash
# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export ENVIRONMENT=dev
export PULUMI_ORG=scoobyjava-org

# Run the application
uvicorn backend.app.app:app --reload
```

### Testing Basic Connectivity
```bash
# Use the simple app for basic tests
uvicorn backend.app.simple_app:app
```

## API Structure

All API endpoints are under `/api/v1/`:
- `/api/v1/chat` - Unified chat endpoint
- `/api/v1/knowledge/*` - Knowledge management
- `/api/v1/dashboard/*` - Dashboard data
- `/api/v1/mcp/*` - MCP server orchestration

## Service Architecture

The application uses a modular service architecture:
- Services are initialized at startup
- Services can fail gracefully (warnings instead of crashes)
- Health endpoint reports service status

## Migration Notes

If you're migrating from an old app file:
1. Update your Docker configurations
2. Update any deployment scripts
3. Update documentation references
4. Test with the new unified app

## Troubleshooting

### Import Errors
If you see import errors, some services may not be available. The app will:
- Log warnings for missing services
- Continue running with available services
- Report service status in health endpoint

### PyArrow Issues
If PyArrow causes problems:
1. Use the simple_app.py for basic testing
2. Check the PyArrow troubleshooting guide
3. Consider using conda for complex dependencies

## Future Improvements

The following enhancements are planned:
1. Enhanced semantic caching (Phase 3.1)
2. Auto-evaluation framework (Phase 3.2)
3. LangGraph state management (Phase 3.3)

See `docs/REPOSITORY_CLEANUP_AND_ALIGNMENT_PLAN.md` for details.
