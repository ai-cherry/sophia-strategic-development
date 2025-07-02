# Sophia AI Deployment Action Plan

## Current Status ✅

We have a **WORKING API** with:
- FastAPI v2 running on port 8000
- Pulumi ESC connected (191 config items)
- All critical secrets configured
- Database credentials ready
- Clean foundation to build on

## Incremental Deployment Strategy

### Phase 1: Add Core Services (TODAY - Next 2 Hours)

#### 1.1 Add Actual Database Connection
```python
# Add to minimal_api_v2.py:
- Real Snowflake connection test
- Basic query execution
- Connection pooling
```

#### 1.2 Add Simple Chat Endpoint
```python
# Add basic chat functionality:
- /api/v1/chat endpoint
- Connect to OpenAI
- Simple request/response
```

#### 1.3 Add One MCP Server
```python
# Start with AI Memory:
- Fix import issues
- Basic store/retrieve
- Health endpoint
```

### Phase 2: Expand Services (TOMORROW)

#### 2.1 Enable More API Routes
- Knowledge base endpoints
- LLM strategy endpoints
- Basic dashboard data

#### 2.2 Add More MCP Servers
- Codacy MCP
- Snowflake MCP
- Asana MCP

#### 2.3 Frontend Connection
- Enable CORS properly
- Connect React frontend
- Basic dashboard

### Phase 3: Full System (THIS WEEK)

#### 3.1 Complete MCP Orchestra
- All MCP servers running
- Orchestration service
- Cross-server communication

#### 3.2 Advanced Features
- WebSocket support
- Real-time updates
- Full chat integration

#### 3.3 Production Readiness
- Health monitoring
- Error handling
- Performance optimization

## Immediate Next Steps (Do Now)

### 1. Test Database Connection
```bash
# Create test script
python scripts/test_snowflake_connection.py
```

### 2. Add Chat Endpoint
```python
# Add to minimal_api_v2.py
@app.post("/api/v1/chat")
async def chat(message: str):
    # Simple OpenAI call
    return {"response": "..."}
```

### 3. Fix One MCP Server
```bash
# Start with AI Memory
python mcp-servers/ai_memory/run_server.py
```

## Success Metrics

### Today
- [ ] Database query working
- [ ] Chat endpoint responding
- [ ] One MCP server running

### Tomorrow
- [ ] 5+ API endpoints working
- [ ] 3+ MCP servers running
- [ ] Frontend connected

### This Week
- [ ] Full system operational
- [ ] All services integrated
- [ ] Production ready

## Key Principles

1. **One Thing at a Time** - Add one service, test it, then add next
2. **Always Running** - Never break what's working
3. **Test Everything** - Verify each addition
4. **Document Progress** - Track what works

## Testing Commands

```bash
# Always running tests:
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status
curl http://localhost:8000/api/v1/config/test
curl http://localhost:8000/api/v1/database/health

# New endpoint tests:
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Current Working Endpoints

1. `GET /` - Root
2. `GET /health` - Health check
3. `GET /api/v1/status` - Full status
4. `GET /api/v1/config/test` - Config test
5. `GET /api/v1/database/health` - DB health
6. `POST /api/v1/echo` - Echo test

## Build Command

```bash
# Keep v2 API running:
python backend/app/minimal_api_v2.py

# In another terminal, add features incrementally
```

## Success! 🎉

We went from 0% to having a working API with ESC integration in one session. By following this incremental approach, we'll have the full system running within days, not weeks! 