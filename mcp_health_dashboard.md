# 📊 MCP Server Health Check Dashboard

**Generated:** 2025-07-17 01:02:29 UTC
**Environment:** Production (Pulumi ESC)

## 📈 Summary
- **Total Servers:** 8
- **✅ Connected:** 0
- **❌ Failed:** 1
- **⚠️  Warnings:** 7
- **Success Rate:** 0.0%

## 🔍 Detailed Results


### ⚠️  Servers with Warnings

- **lambda-labs** - ⚠️  lambda-labs configured but connection failed
- **qdrant** - ⚠️  qdrant configured but connection failed
- **mem0** - ⚠️  mem0 configured but connection failed
  - ⚠️  No API key or token found in environment
- **n8n** - ⚠️  n8n configured but connection failed
  - ⚠️  No API key or token found in environment
- **hubspot** - ⚠️  hubspot configured but connection failed
  - ⚠️  No API key or token found in environment
- **slack** - ⚠️  slack configured but connection failed
- **estuary-flow** - ⚠️  estuary-flow configured but connection failed
  - ⚠️  No API key or token found in environment

### ❌ Failed Servers

- **gong** - ❌ gong configuration or environment issues
  - ❌ Missing required GONG_ACCESS_KEY_SECRET
  - ❌ GONG_ACCESS_KEY seems too short for a valid key
  - ❌ GONG_ACCESS_KEY_SECRET is empty
  - ❌ GONG_CLIENT_ACCESS_KEY seems too short for a valid key
  - ❌ GONG_CLIENT_SECRET seems too short for a valid key
  - ❌ Startup test failed: expected str, bytes or os.PathLike object, not NoneType
  - ❌ Gong MCP server module not found

## 🔧 Configuration Issues

### gong
- **Configuration:** ❌ Invalid
- **Environment Variables:** ❌ Missing or invalid
- Missing required GONG_ACCESS_KEY_SECRET
- GONG_ACCESS_KEY seems too short for a valid key
- GONG_ACCESS_KEY_SECRET is empty
- GONG_CLIENT_ACCESS_KEY seems too short for a valid key
- GONG_CLIENT_SECRET seems too short for a valid key
- Startup test failed: expected str, bytes or os.PathLike object, not NoneType
- Gong MCP server module not found

## 🛠️ Recommended Actions

### For Failed Servers:
1. Check API keys in Pulumi ESC / GitHub Organization Secrets
2. Verify server modules are installed: `pip install -r requirements.txt`
3. Run validation: `python scripts/utils/generate_mcp_config.py --validate`
4. Check server-specific documentation

### For Servers with Warnings:
1. Review warning messages above
2. Test individual servers manually
3. Check network connectivity and firewall rules

## 📊 Connection Metrics
