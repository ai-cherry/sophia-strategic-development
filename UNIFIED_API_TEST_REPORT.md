# Unified API Test Report

Generated: 2025-07-01 16:41:21

## Summary

- Total tests: 11
- Passed: 6
- Warnings: 4
- Failed: 1
- Success rate: 54.5%

## Passed Tests

- ✅ {'endpoint': '/', 'description': 'Root endpoint', 'status': 200}
- ✅ {'endpoint': '/health', 'description': 'Health check', 'status': 200}
- ✅ {'endpoint': '/docs', 'description': 'API documentation', 'status': 200}
- ✅ {'endpoint': '/openapi.json', 'description': 'OpenAPI schema', 'status': 200}
- ✅ {'test': 'Performance', 'endpoint': '/health', 'avg_response_time_ms': 0.6665229797363281, 'min_response_time_ms': 0.5180835723876953, 'max_response_time_ms': 0.8482933044433594}
- ✅ {'test': 'Performance', 'endpoint': '/', 'avg_response_time_ms': 0.7501840591430664, 'min_response_time_ms': 0.6310939788818359, 'max_response_time_ms': 0.8757114410400391}

## Warnings

- ⚠️  {'endpoint': '/metrics', 'description': 'Prometheus metrics', 'status': 404}
- ⚠️  {'route': '/api/v3/chat/status', 'method': 'GET', 'description': 'Chat service status', 'status': 404}
- ⚠️  {'route': '/api/mcp/servers', 'method': 'GET', 'description': 'MCP server list', 'status': 404}
- ⚠️  {'route': '/api/v3/chat/message', 'method': 'POST', 'description': 'Send chat message', 'status': 404}

## Failed Tests

- ❌ {'test': 'Service health', 'error': "'environment'"}

## Recommendations

1. Fix failed endpoints before deployment
2. Check service initialization errors
3. Verify all dependencies are installed
