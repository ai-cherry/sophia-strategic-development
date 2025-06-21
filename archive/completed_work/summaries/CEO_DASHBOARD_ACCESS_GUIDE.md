# How to Access Your CEO Dashboard in Retool

## Quick Access Steps

### 1. Backend is Already Running ✅
Your backend is running at: http://localhost:8000
- Health endpoint: http://localhost:8000/health ✅
- Executive API: http://localhost:8000/api/executive/summary ✅

### 2. Access Retool Dashboard

#### Option A: If You Already Have a Retool Account
1. **Log into Retool**: https://retool.com/
2. **Create a New App**: Click "Create new" → "App"
3. **Name it**: "Sophia AI CEO Dashboard"

#### Option B: If You Need a Retool Account
1. **Sign up for Retool**: https://retool.com/signup
2. **Choose the free tier** (sufficient for testing)
3. **Create your first app** named "Sophia AI CEO Dashboard"

### 3. Configure Your Retool App

#### Step 1: Add the API Resource
1. In Retool, go to **Resources** (left sidebar)
2. Click **"Create new"** → **"REST API"**
3. Configure as follows:
   - **Name**: SophiaAPI
   - **Base URL**: http://localhost:8000
   - **Headers**: 
     - Key: `X-Admin-Key`
     - Value: `sophia_admin_2024`

#### Step 2: Create the Dashboard
1. In your Retool app, add a **Container** component
2. Inside the container, add:
   - **Text** component with title "Executive Summary"
   - **Statistics** components for KPIs
   - **Table** component for data display

#### Step 3: Add Queries
1. Click **"Create new query"**
2. Select **SophiaAPI** as the resource
3. Create these queries:

**Query 1: Get Executive Summary**
- Method: GET
- URL: `/api/executive/summary`
- Run this query on page load

**Query 2: Get Alerts**
- Method: GET  
- URL: `/api/executive/alerts`
- Run this query on page load

#### Step 4: Connect Data to Components
1. Select your Statistics components
2. Set their values to:
   - Revenue: `{{ query1.data.data.revenue.current_month }}`
   - Growth: `{{ query1.data.data.revenue.growth }}%`
   - Total Clients: `{{ query1.data.data.clients.total }}`
   - At Risk: `{{ query1.data.data.clients.at_risk }}`

3. For the alerts table:
   - Data source: `{{ query2.data.alerts }}`

### 4. View Your Dashboard
1. Click **"Preview"** in the top right
2. Your dashboard should now display:
   - Current month revenue: $125,000
   - Growth: 8.7%
   - Total clients: 45
   - Alerts about opportunities and risks

## Alternative: Quick Demo Dashboard

If you want to see the data immediately without setting up Retool:

1. Open your browser
2. Go to: http://localhost:8000/api/executive/summary
3. You'll see the raw JSON data that would power your dashboard

## Troubleshooting

### If Retool Can't Connect to Your Backend:
1. Make sure your backend is still running (check the terminal)
2. Try using `http://host.docker.internal:8000` instead of `localhost` if running Retool in Docker
3. Check that CORS is enabled (it is in our simplified backend)

### If You See Authentication Errors:
1. Double-check the admin key: `sophia_admin_2024`
2. Make sure it's added as a header, not a parameter

### Need the Full Template?
The complete Retool template is available in:
`scripts/retool_ceo_dashboard_template.js`

You can copy sections from this template into your Retool app for a more complete dashboard experience.

## Next Steps

Once you have the basic dashboard working:
1. Add more visualizations (charts, graphs)
2. Implement the strategic chat interface
3. Add real-time updates with polling
4. Connect to production data sources

---

**Backend Status**: ✅ Running
**API Endpoints**: ✅ Working
**Next Action**: Log into Retool and create your dashboard
