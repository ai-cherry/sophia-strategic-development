# CEO Dashboard Deployment Guide

## Quick Start (Without Pulumi)

This guide helps you deploy the Sophia AI CEO Dashboard without requiring Pulumi ESC setup.

### Step 1: Start the Backend

```bash
# Option A: Use the simple backend starter
python scripts/start_backend_simple.py

# Option B: Start manually
cd backend
python main_simple.py
```

The backend will start on http://localhost:8000

### Step 2: Test the Backend

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test executive summary (requires auth)
curl -H "X-Admin-Key: sophia_admin_2024" \
     http://localhost:8000/api/executive/summary

# Test executive alerts
curl -H "X-Admin-Key: sophia_admin_2024" \
     http://localhost:8000/api/executive/alerts
```

### Step 3: Test Retool API (Optional)

If you have a Retool API token:

```bash
# Set your Retool API token
export RETOOL_API_TOKEN='your-token-here'

# Run the Retool API test
python scripts/test_retool_api_direct.py
```

### Step 4: Create Retool Dashboard

1. **Log into Retool** at https://retool.com

2. **Create a New App** called "Sophia CEO Dashboard"

3. **Add a REST API Resource**:
   - Name: `SophiaAPI`
   - Base URL: `http://localhost:8000`
   - Headers: 
     - Key: `X-Admin-Key`
     - Value: `sophia_admin_2024`

4. **Create Queries**:

   ```javascript
   // Query: getExecutiveSummary
   // Method: GET
   // URL: /api/executive/summary
   
   // Query: getExecutiveAlerts  
   // Method: GET
   // URL: /api/executive/alerts
   ```

5. **Build Your Dashboard**:
   - Add a Statistics component for KPIs
   - Add a Table for alerts
   - Add Charts for metrics visualization

## Available API Endpoints

### Public Endpoints
- `GET /` - API root information
- `GET /health` - Health check

### Executive Dashboard Endpoints (Requires X-Admin-Key header)
- `GET /api/executive/summary` - Executive summary with KPIs
- `GET /api/executive/alerts` - Priority alerts and notifications
- `GET /api/executive/metrics` - Detailed performance metrics
- `GET /api/executive/insights` - AI-generated insights

## Testing Infrastructure Components

### 1. Test Without Pulumi ESC

```bash
# Run the CEO dashboard deployment test
python scripts/deploy_ceo_dashboard.py

# This will:
# - Check backend health
# - Test all API endpoints
# - Generate Retool configuration
# - Provide deployment instructions
```

### 2. Infrastructure Testing Framework

If you want to test the full infrastructure:

```bash
# Run all infrastructure tests
cd tests/infrastructure
python run_all_tests.py

# Run specific test suites
pytest unit/test_snowflake_component.py -v
pytest integration/test_snowflake_gong_integration.py -v
pytest e2e/test_complete_infrastructure.py -v
```

### 3. Component Health Checks

```python
# Test individual components
import asyncio
from backend.core.config_manager import health_check

# Check service health
async def test_services():
    services = ['snowflake', 'pinecone', 'gong', 'slack']
    for service in services:
        try:
            result = await health_check(service)
            print(f"{service}: {'✓' if result else '✗'}")
        except Exception as e:
            print(f"{service}: ✗ ({str(e)})")

asyncio.run(test_services())
```

## Manual Dashboard Creation in Retool

### Step 1: Create Main Dashboard Layout

```javascript
// Add a Container with 3 columns
// Column 1: KPI Cards
// Column 2: Alerts Table  
// Column 3: Charts
```

### Step 2: KPI Cards

```javascript
// Revenue Card
{{getExecutiveSummary.data.data.revenue.current_month.toLocaleString('en-US', {style: 'currency', currency: 'USD'})}}

// Growth Rate
{{getExecutiveSummary.data.data.revenue.growth}}%

// Active Clients
{{getExecutiveSummary.data.data.clients.total}}
```

### Step 3: Alerts Table

```javascript
// Table Data Source
{{getExecutiveAlerts.data.alerts}}

// Columns:
// - Priority (with color coding)
// - Type (opportunity/risk)
// - Message
// - Timestamp
```

### Step 4: Performance Charts

```javascript
// Chart component with data from metrics endpoint
// X-axis: Time periods
// Y-axis: Metric values
// Series: Different KPIs
```

## Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill $(lsof -t -i:8000)

# Try a different port
PORT=8001 python backend/main_simple.py
```

### API Authentication Errors
```bash
# Make sure to include the header
curl -H "X-Admin-Key: sophia_admin_2024" http://localhost:8000/api/executive/summary

# Check the admin key in your environment
echo $SOPHIA_ADMIN_KEY
```

### Retool Connection Issues
1. Ensure backend is running
2. Check CORS is enabled (it is in our backend)
3. Use correct authentication header
4. Try using ngrok for HTTPS if needed

## Next Steps

1. **Enhance the Backend**: Add real data connections
2. **Add More Endpoints**: Implement additional analytics
3. **Deploy to Production**: Use Vercel or Lambda Labs
4. **Add Real-time Updates**: Implement WebSocket connections
5. **Integrate AI Features**: Connect to OpenRouter/Claude

## Support

For issues or questions:
- Check the logs: `backend/logs/`
- Review the API docs: http://localhost:8000/docs
- Test individual endpoints with curl
- Use the deployment scripts in `scripts/`
