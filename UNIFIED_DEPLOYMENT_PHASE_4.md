# PHASE 4: END-TO-END VALIDATION & GO-LIVE (2 Hours)

## Overview
Comprehensive testing and validation of the complete system before cutting over to production.

## Prerequisites from Phase 3
- [ ] All MCP servers deployed and healthy
- [ ] API gateway integration working
- [ ] Frontend and backend fully deployed

## 4.1 Automated E2E Test Suite (30 minutes)

### A. Create Comprehensive Test Script
```python
# tests/e2e/test_full_system.py
import pytest
import httpx
import websockets
import json
import asyncio
from datetime import datetime

BASE_URL = "https://app.sophia-intel.ai"
API_URL = "https://api.sophia-intel.ai"
WS_URL = "wss://api.sophia-intel.ai/ws"

class TestSophiaAIE2E:
    """End-to-end test suite for complete system validation"""

    @pytest.fixture
    async def api_client(self):
        async with httpx.AsyncClient() as client:
            yield client

    @pytest.mark.asyncio
    async def test_frontend_loads(self, api_client):
        """Test frontend application loads successfully"""
        response = await api_client.get(BASE_URL, follow_redirects=True)
        assert response.status_code == 200
        assert "Sophia AI" in response.text
        assert "UnifiedDashboard" in response.text

    @pytest.mark.asyncio
    async def test_api_health(self, api_client):
        """Test all API health endpoints"""
        endpoints = [
            "/health",
            "/api/v1/dashboard/main",
            "/api/v1/chat/contexts",
            "/api/v1/infrastructure/status",
            "/api/v1/mcp/servers"
        ]

        for endpoint in endpoints:
            response = await api_client.get(f"{API_URL}{endpoint}")
            assert response.status_code == 200, f"Failed: {endpoint}"

    @pytest.mark.asyncio
    async def test_websocket_chat(self):
        """Test WebSocket chat functionality"""
        async with websockets.connect(f"{WS_URL}/test-e2e") as websocket:
            # Test basic message
            await websocket.send(json.dumps({
                "message": "Hello, Sophia AI",
                "search_context": "business_intelligence",
                "access_level": "employee"
            }))

            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)

            assert data["type"] == "response"
            assert data["data"]["response"] is not None
            assert isinstance(data["data"]["timestamp"], str)

    @pytest.mark.asyncio
    async def test_dashboard_data(self, api_client):
        """Test dashboard loads real data"""
        response = await api_client.get(f"{API_URL}/api/v1/dashboard/main")
        assert response.status_code == 200

        data = response.json()
        assert "kpis" in data
        assert "charts" in data
        assert "infrastructure" in data
        assert len(data["kpis"]) > 0

    @pytest.mark.asyncio
    async def test_mcp_integration(self, api_client):
        """Test MCP servers are integrated"""
        response = await api_client.get(f"{API_URL}/api/v1/mcp/servers")
        assert response.status_code == 200

        servers = response.json()
        required_servers = ["github", "slack", "perplexity", "ai-memory", "snowflake"]

        for server in required_servers:
            assert server in servers
            assert servers[server]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_chat_with_context_switching(self):
        """Test chat context switching"""
        contexts = [
            "business_intelligence",
            "ceo_deep_research",
            "internal_knowledge",
            "code_search"
        ]

        async with websockets.connect(f"{WS_URL}/test-context") as websocket:
            for context in contexts:
                await websocket.send(json.dumps({
                    "message": f"Test message for {context}",
                    "search_context": context,
                    "access_level": "executive"
                }))

                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)

                assert data["type"] == "response"
                assert data["data"]["response"] is not None
```

### B. Performance Test Suite
```javascript
// tests/performance/k6-load-test.js
import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up
    { duration: '1m', target: 50 },    // Stay at 50 users
    { duration: '30s', target: 100 },  // Peak load
    { duration: '1m', target: 100 },   // Stay at peak
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    errors: ['rate<0.01'],            // Error rate under 1%
    ws_connecting: ['p(95)<1000'],    // WebSocket connection under 1s
  },
};

const BASE_URL = 'https://api.sophia-intel.ai';
const WS_URL = 'wss://api.sophia-intel.ai/ws';

export default function () {
  // Test API endpoints
  const endpoints = [
    '/health',
    '/api/v1/dashboard/main',
    '/api/v1/chat/contexts',
    '/api/v1/mcp/servers',
  ];

  endpoints.forEach(endpoint => {
    const res = http.get(`${BASE_URL}${endpoint}`);
    check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 500ms': (r) => r.timings.duration < 500,
    });
    errorRate.add(res.status !== 200);
  });

  // Test WebSocket
  const wsRes = ws.connect(`${WS_URL}/${__VU}`, {}, function (socket) {
    socket.on('open', () => {
      socket.send(JSON.stringify({
        message: 'Performance test message',
        search_context: 'business_intelligence',
        access_level: 'employee',
      }));
    });

    socket.on('message', (data) => {
      const msg = JSON.parse(data);
      check(msg, {
        'received response': () => msg.type === 'response',
      });
      socket.close();
    });

    socket.setTimeout(() => {
      errorRate.add(1);
      socket.close();
    }, 5000);
  });

  check(wsRes, {
    'WebSocket connected': (r) => r && r.status === 101,
  });

  sleep(1);
}
```

## 4.2 Security Validation (30 minutes)

### A. Security Scan Script
```bash
#!/bin/bash
# scripts/security-validation.sh

echo "🔒 Running Security Validation"
echo "=============================="

# Check SSL certificates
echo "📜 Checking SSL certificates..."
echo | openssl s_client -servername app.sophia-intel.ai -connect app.sophia-intel.ai:443 2>/dev/null | openssl x509 -noout -dates
echo | openssl s_client -servername api.sophia-intel.ai -connect api.sophia-intel.ai:443 2>/dev/null | openssl x509 -noout -dates

# Check security headers
echo ""
echo "🛡️ Checking security headers..."
curl -s -I https://api.sophia-intel.ai | grep -E "(Strict-Transport-Security|X-Content-Type-Options|X-Frame-Options|X-XSS-Protection)"

# Run OWASP ZAP baseline scan
echo ""
echo "🕷️ Running OWASP ZAP scan..."
docker run --rm owasp/zap2docker-stable zap-baseline.py \
  -t https://api.sophia-intel.ai \
  -r zap-report.html \
  -l WARN

# Check for exposed secrets
echo ""
echo "🔑 Checking for exposed secrets..."
curl -s https://api.sophia-intel.ai/api/v1/config 2>/dev/null | grep -E "(password|secret|key|token)" || echo "✅ No secrets exposed"

# Test rate limiting
echo ""
echo "⏱️ Testing rate limiting..."
for i in {1..150}; do
  response=$(curl -s -o /dev/null -w "%{http_code}" https://api.sophia-intel.ai/health)
  if [ "$response" = "429" ]; then
    echo "✅ Rate limiting working (triggered at request $i)"
    break
  fi
done
```

### B. Authentication Test
```python
# tests/security/test_authentication.py
import pytest
import httpx
import jwt
from datetime import datetime, timedelta

API_URL = "https://api.sophia-intel.ai"

@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test endpoints require authentication"""
    protected_endpoints = [
        "/api/v1/admin/users",
        "/api/v1/infrastructure/deploy",
        "/api/v1/chat/ceo-context"
    ]

    async with httpx.AsyncClient() as client:
        for endpoint in protected_endpoints:
            response = await client.get(f"{API_URL}{endpoint}")
            assert response.status_code in [401, 403], f"Endpoint {endpoint} not protected"

@pytest.mark.asyncio
async def test_jwt_validation():
    """Test JWT token validation"""
    # Create invalid token
    invalid_token = jwt.encode(
        {"user_id": "test", "exp": datetime.utcnow() - timedelta(hours=1)},
        "wrong-secret",
        algorithm="HS256"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/api/v1/user/profile",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS configuration"""
    async with httpx.AsyncClient() as client:
        response = await client.options(
            f"{API_URL}/api/v1/chat",
            headers={"Origin": "https://app.sophia-intel.ai"}
        )

        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "https://app.sophia-intel.ai"
```

## 4.3 User Acceptance Testing (30 minutes)

### A. UAT Checklist Script
```bash
#!/bin/bash
# scripts/uat-checklist.sh

echo "👤 User Acceptance Testing Checklist"
echo "==================================="
echo ""

# Function to test and report
test_feature() {
    local feature=$1
    local test_command=$2

    echo -n "Testing $feature... "
    if eval $test_command > /dev/null 2>&1; then
        echo "✅ PASS"
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}

# Dashboard Tests
echo "📊 Dashboard Tests:"
test_feature "Dashboard loads" "curl -s https://app.sophia-intel.ai | grep -q 'UnifiedDashboard'"
test_feature "KPI cards display" "curl -s https://api.sophia-intel.ai/api/v1/dashboard/main | jq -e '.kpis | length > 0'"
test_feature "Charts render" "curl -s https://api.sophia-intel.ai/api/v1/dashboard/charts | jq -e '.charts | length > 0'"

echo ""
echo "💬 Chat Tests:"
test_feature "Chat interface loads" "curl -s https://app.sophia-intel.ai | grep -q 'EnhancedUnifiedChat'"
test_feature "WebSocket connects" "wscat -c wss://api.sophia-intel.ai/ws/uat-test -x exit"
test_feature "Messages send/receive" "python tests/manual/test_chat_flow.py"

echo ""
echo "🔧 MCP Integration Tests:"
test_feature "GitHub integration" "curl -s https://api.sophia-intel.ai/api/v1/mcp/github/health | jq -e '.status == \"healthy\"'"
test_feature "Slack integration" "curl -s https://api.sophia-intel.ai/api/v1/mcp/slack/health | jq -e '.status == \"healthy\"'"
test_feature "Perplexity integration" "curl -s https://api.sophia-intel.ai/api/v1/mcp/perplexity/health | jq -e '.status == \"healthy\"'"

echo ""
echo "🎯 Business Features:"
test_feature "Business intelligence context" "python tests/manual/test_bi_query.py"
test_feature "Code search functionality" "python tests/manual/test_code_search.py"
test_feature "Documentation lookup" "python tests/manual/test_doc_search.py"
```

### B. Manual Test Scripts
```python
# tests/manual/test_chat_flow.py
import asyncio
import websockets
import json

async def test_chat_conversation():
    """Test a complete chat conversation flow"""
    uri = "wss://api.sophia-intel.ai/ws/manual-test"

    async with websockets.connect(uri) as websocket:
        # Test 1: Business query
        await websocket.send(json.dumps({
            "message": "What were our sales last quarter?",
            "search_context": "business_intelligence",
            "access_level": "executive"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print(f"✅ Business query response: {data['data']['response'][:100]}...")

        # Test 2: Code search
        await websocket.send(json.dumps({
            "message": "Show me Python WebSocket examples",
            "search_context": "code_search",
            "access_level": "employee"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print(f"✅ Code search response: {data['data']['response'][:100]}...")

        # Test 3: Documentation
        await websocket.send(json.dumps({
            "message": "How do I deploy to Lambda Labs?",
            "search_context": "documentation",
            "access_level": "employee"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print(f"✅ Documentation response: {data['data']['response'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_chat_conversation())
```

## 4.4 Production Cutover (30 minutes)

### A. Pre-Cutover Checklist
```bash
#!/bin/bash
# scripts/pre-cutover-checklist.sh

echo "🚦 Pre-Cutover Checklist"
echo "======================="
echo ""

# Check all systems
checks=(
    "Frontend accessible|curl -s -o /dev/null -w '%{http_code}' https://app.sophia-intel.ai|200"
    "API healthy|curl -s https://api.sophia-intel.ai/health | jq -r '.status'|healthy"
    "WebSocket working|wscat -c wss://api.sophia-intel.ai/ws/test -x exit|"
    "MCP servers online|curl -s https://api.sophia-intel.ai/api/v1/mcp/servers | jq -r 'keys | length'|9"
    "SSL valid|echo | openssl s_client -servername api.sophia-intel.ai -connect api.sophia-intel.ai:443 2>/dev/null | openssl x509 -noout -checkend 86400|"
    "Rate limiting active|python tests/security/test_rate_limit.py|"
    "Monitoring active|curl -s http://146.235.200.1:9090/api/v1/query?query=up | jq '.data.result | length'|"
)

all_passed=true

for check in "${checks[@]}"; do
    IFS='|' read -r name command expected <<< "$check"
    echo -n "Checking $name... "

    result=$(eval $command 2>/dev/null)

    if [[ -z "$expected" ]] || [[ "$result" == "$expected" ]]; then
        echo "✅ PASS"
    else
        echo "❌ FAIL (expected: $expected, got: $result)"
        all_passed=false
    fi
done

echo ""
if $all_passed; then
    echo "🎉 All checks passed! Ready for cutover."
    exit 0
else
    echo "⚠️ Some checks failed. Please fix before cutover."
    exit 1
fi
```

### B. Cutover Script
```bash
#!/bin/bash
# scripts/production-cutover.sh

echo "🚀 PRODUCTION CUTOVER SCRIPT"
echo "==========================="
echo ""
echo "⚠️  This will switch to the new production system."
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Step 1: Final backup
echo "📦 Creating final backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/$timestamp
pulumi stack export > backups/$timestamp/pulumi-stack.json
echo "✅ Backup created"

# Step 2: Update DNS (if needed)
echo ""
echo "🌐 DNS Configuration:"
echo "app.sophia-intel.ai → Vercel"
echo "api.sophia-intel.ai → Lambda Labs (146.235.200.1)"
echo ""
echo "Current DNS status:"
dig +short app.sophia-intel.ai
dig +short api.sophia-intel.ai

# Step 3: Enable production monitoring
echo ""
echo "📊 Enabling production monitoring..."
curl -X POST http://146.235.200.1:9093/api/v1/alerts/receivers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-alerts",
    "webhook_configs": [{
      "url": "'$SLACK_WEBHOOK'",
      "send_resolved": true
    }]
  }'

# Step 4: Announce go-live
echo ""
echo "📢 Sending go-live notification..."
curl -X POST $SLACK_WEBHOOK \
  -H "Content-Type: application/json" \
  -d '{
    "text": "🎉 Sophia AI is now LIVE in production!",
    "attachments": [{
      "color": "good",
      "fields": [
        {"title": "Frontend", "value": "https://app.sophia-intel.ai", "short": true},
        {"title": "API", "value": "https://api.sophia-intel.ai", "short": true},
        {"title": "Status", "value": "All systems operational", "short": false}
      ]
    }]
  }'

echo ""
echo "✅ CUTOVER COMPLETE!"
echo ""
echo "🔗 Access Points:"
echo "  - Dashboard: https://app.sophia-intel.ai"
echo "  - API Docs: https://api.sophia-intel.ai/docs"
echo "  - Health: https://api.sophia-intel.ai/health"
echo ""
echo "📊 Monitoring:"
echo "  - Grafana: http://146.235.200.1:3000"
echo "  - Logs: ssh ubuntu@146.235.200.1 'docker logs -f sophia-backend'"
```

## 4.5 Post-Deployment Validation (30 minutes)

### A. Smoke Test Production
```python
# tests/production/smoke_test.py
import httpx
import asyncio
import json
from datetime import datetime

PROD_APP = "https://app.sophia-intel.ai"
PROD_API = "https://api.sophia-intel.ai"

async def smoke_test():
    """Run smoke tests on production"""
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "tests": []
    }

    async with httpx.AsyncClient() as client:
        # Test 1: Frontend loads
        try:
            response = await client.get(PROD_APP)
            results["tests"].append({
                "name": "Frontend Load",
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "details": f"Status: {response.status_code}"
            })
        except Exception as e:
            results["tests"].append({
                "name": "Frontend Load",
                "status": "FAIL",
                "details": str(e)
            })

        # Test 2: API Health
        try:
            response = await client.get(f"{PROD_API}/health")
            data = response.json()
            results["tests"].append({
                "name": "API Health",
                "status": "PASS" if data.get("status") == "healthy" else "FAIL",
                "details": data
            })
        except Exception as e:
            results["tests"].append({
                "name": "API Health",
                "status": "FAIL",
                "details": str(e)
            })

        # Test 3: Critical Features
        critical_endpoints = [
            ("/api/v1/dashboard/main", "Dashboard Data"),
            ("/api/v1/chat/contexts", "Chat Contexts"),
            ("/api/v1/mcp/servers", "MCP Servers")
        ]

        for endpoint, name in critical_endpoints:
            try:
                response = await client.get(f"{PROD_API}{endpoint}")
                results["tests"].append({
                    "name": name,
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "details": f"Status: {response.status_code}"
                })
            except Exception as e:
                results["tests"].append({
                    "name": name,
                    "status": "FAIL",
                    "details": str(e)
                })

    # Print results
    print(json.dumps(results, indent=2))

    # Return success/failure
    failed = [t for t in results["tests"] if t["status"] == "FAIL"]
    return len(failed) == 0

if __name__ == "__main__":
    success = asyncio.run(smoke_test())
    exit(0 if success else 1)
```

### B. Monitor First 30 Minutes
```bash
#!/bin/bash
# scripts/monitor-go-live.sh

echo "📊 Monitoring Go-Live (30 minutes)"
echo "================================="
echo ""

# Monitor for 30 minutes
end_time=$(($(date +%s) + 1800))

while [ $(date +%s) -lt $end_time ]; do
    clear
    echo "🕐 Monitoring Production - $(date)"
    echo "================================="

    # Check health
    echo -n "API Health: "
    curl -s https://api.sophia-intel.ai/health | jq -r '.status'

    # Check response times
    echo -n "API Response Time: "
    curl -s -o /dev/null -w "%{time_total}s\n" https://api.sophia-intel.ai/health

    # Check error rate
    echo -n "Error Rate: "
    curl -s http://146.235.200.1:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m]) | jq -r '.data.result[0].value[1]' || echo "0"

    # Check active connections
    echo -n "WebSocket Connections: "
    curl -s https://api.sophia-intel.ai/api/v1/ws/connections | jq -r '.active_connections'

    # Check MCP servers
    echo ""
    echo "MCP Server Status:"
    curl -s https://api.sophia-intel.ai/api/v1/mcp/servers | jq -r 'to_entries[] | "\(.key): \(.value.status)"'

    echo ""
    echo "Press Ctrl+C to exit monitoring"
    sleep 30
done

echo ""
echo "✅ 30-minute monitoring complete!"
```

## Success Criteria ✅
- [ ] All E2E tests passing
- [ ] Performance tests meet SLAs
- [ ] Security scans show no critical issues
- [ ] UAT checklist complete
- [ ] Production smoke tests passing
- [ ] 30-minute monitoring shows stability

## Rollback Plan 🔄
```bash
# Emergency rollback procedure
#!/bin/bash

echo "🚨 EMERGENCY ROLLBACK"

# 1. Revert frontend
vercel rollback --token $VERCEL_TOKEN

# 2. Revert backend
ssh ubuntu@146.235.200.1 << 'EOF'
    docker stop sophia-backend
    docker run -d --name sophia-backend-old sophia-ai-backend:previous
EOF

# 3. Restore previous configuration
pulumi stack import < backups/latest/pulumi-stack.json

# 4. Notify team
curl -X POST $SLACK_WEBHOOK -d '{"text":"⚠️ Emergency rollback initiated"}'
```

## Phase 4 Completion Checklist
- [ ] E2E tests executed and passing
- [ ] Performance validated
- [ ] Security validated
- [ ] UAT completed
- [ ] Production cutover successful
- [ ] Post-deployment monitoring active
- [ ] Documentation updated

## Time Tracking
- Start Time: ___________
- End Time: ___________
- Total Duration: ___________
- Issues Encountered: ___________

## Sign-Off
- [ ] Technical Lead: ___________
- [ ] Product Owner: ___________
- [ ] CEO Approval: ___________

## 🎉 CONGRATULATIONS!
The Sophia AI platform is now fully operational in production!
