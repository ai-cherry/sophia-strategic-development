# Foundational Knowledge Quick Start Guide
## Get Running in 30 Minutes

This guide will help you set up the foundational knowledge system using Notion as the UI and integrating with Sophia AI.

---

## 🚀 Prerequisites

1. **Notion Account** with API access
2. **Sample Data Files** (employees, customers, Gong users)
3. **Python 3.11+** installed
4. **Sophia AI** development environment

---

## 📋 Step-by-Step Setup

### Step 1: Create Notion Workspace (5 minutes)

1. Open Notion and create a new page called "Pay Ready Foundational Knowledge"
2. Copy the page ID from the URL:
   ```
   https://www.notion.so/Pay-Ready-Foundational-Knowledge-[PAGE_ID_HERE]
   ```
3. Save this PAGE_ID - you'll need it!

### Step 2: Run Setup Script (5 minutes)

```bash
# Navigate to Sophia main directory
cd /Users/lynnmusil/sophia-main

# Run the setup script with your page ID
python scripts/setup_notion_simple.py YOUR_PAGE_ID_HERE

# This creates 5 databases:
# - 👥 Employees
# - 🏢 Customers
# - 🥊 Competitors
# - 📦 Products
# - 🥇 Power Users
```

The script will output database IDs - save these!

### Step 3: Configure Environment (2 minutes)

```bash
# Copy the environment template
cp infrastructure/mcp_servers/notion_simple/env.template infrastructure/mcp_servers/notion_simple/.env

# Edit the .env file and add your database IDs
# EMPLOYEES_DB_ID=xxx
# CUSTOMERS_DB_ID=xxx
# COMPETITORS_DB_ID=xxx
# PRODUCTS_DB_ID=xxx
# POWER_USERS_DB_ID=xxx
```

### Step 4: Start Notion MCP Server (3 minutes)

```bash
# Navigate to the server directory
cd infrastructure/mcp_servers/notion_simple

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py

# You should see:
# 🚀 Starting Notion Simple MCP Server on port 9003
# ✅ Employees database configured
# ✅ Customers database configured
# ✅ Competitors database configured
# ✅ Products database configured
# ✅ Power Users database configured
```

### Step 5: Import Sample Data (10 minutes)

In a new terminal:

```bash
# Use the staging app to import data
streamlit run scripts/foundational_knowledge_staging.py

# This opens a web UI where you can:
# 1. Upload CSV/JSON files
# 2. Map columns to Notion fields
# 3. Preview data
# 4. Import to Notion
```

### Step 6: Test the System (5 minutes)

```bash
# Run validation script
python scripts/validate_foundational_knowledge.py

# This tests:
# ✅ Notion connection
# ✅ Database existence
# ✅ MCP server health
# ✅ Search functionality
# ✅ Natural language queries
```

---

## 🧪 Quick Tests

### Test 1: Search API
```bash
# Search for an employee
curl -X POST http://localhost:9003/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Smith", "entity_type": "employees"}'

# Search for a customer
curl -X POST http://localhost:9003/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Acme", "entity_type": "customers"}'

# Search for power users
curl -X POST http://localhost:9003/search \
  -H "Content-Type: application/json" \
  -d '{"query": "CEO", "entity_type": "power_users"}'
```

### Test 2: Employee Lookup
```bash
curl -X POST http://localhost:9003/employees/lookup \
  -H "Content-Type: application/json" \
  -d '{"email": "jane.smith@payready.com"}'
```

### Test 3: List Entities
```bash
# List employees
curl http://localhost:9003/employees

# List customers
curl http://localhost:9003/customers

# List power users
curl http://localhost:9003/power_users
```

---

## 🔗 Sophia AI Integration

To integrate with Sophia AI chat:

1. **Update Sophia Configuration**:
   ```python
   # In your chat service configuration
   NOTION_MCP_ENDPOINT = "http://localhost:9003"
   ```

2. **Test Natural Language Queries**:
   - "Who is Jane Smith?"
   - "Tell me about Acme Corp"
   - "What are our main competitors?"
   - "Show me our products"
   - "Who are our power users?"
   - "Show me executive leadership team"

---

## 📊 Sample Data Format

### 🥇 Power Users (Executive Leadership)

Power Users are key internal stakeholders with high privileges and strategic influence. These are typically C-suite executives, VPs, and strategic decision-makers.

#### Power Users CSV
```csv
Employee ID,Full Name,Email,Job Title,Department,Manager ID,Manager Name,Level,Role Code,Competitors,Segments,Functions,Regions,Rating,Type,Skills,Experience Years,Performance Score
emp_lynn_musil,Lynn Patrick Musil,lynn@payready.com,Chief Executive Officer,Executive,,,1,CEO,"EliseAI,Entrata",Multifamily,Strategic Planning,National,85.0,full,,2,78.5
emp_tiffany_york,Tiffany York,tiffany@payready.com,Chief Product Officer,Product,emp_lynn_musil,Lynn Patrick Musil,2,CPO,EliseAI,Multifamily,Product Strategy,West Coast,82.0,full,,5,75.2
emp_steve_gabel,Steve Gabel,steve@payready.com,VP Strategic Initiatives,Strategy,emp_lynn_musil,Lynn Patrick Musil,2,VP_Strategic,"Market Analysis","All Segments",Strategic Planning,National,78.0,full,,3,73.1
```

#### Power Users JSON
```json
[
  {
    "employee_id": "emp_lynn_musil",
    "full_name": "Lynn Patrick Musil",
    "email": "lynn@payready.com",
    "job_title": "Chief Executive Officer",
    "department": "Executive",
    "manager_id": null,
    "manager_name": null,
    "level": 1,
    "role_code": "CEO",
    "competitors": ["EliseAI", "Entrata"],
    "segments": ["Multifamily"],
    "functions": ["Strategic Planning"],
    "regions": ["National"],
    "rating": 85.0,
    "type": "full",
    "skills": null,
    "experience_years": 2,
    "performance_score": 78.5
  },
  {
    "employee_id": "emp_tiffany_york",
    "full_name": "Tiffany York",
    "email": "tiffany@payready.com",
    "job_title": "Chief Product Officer",
    "department": "Product",
    "manager_id": "emp_lynn_musil",
    "manager_name": "Lynn Patrick Musil",
    "level": 2,
    "role_code": "CPO",
    "competitors": ["EliseAI"],
    "segments": ["Multifamily"],
    "functions": ["Product Strategy"],
    "regions": ["West Coast"],
    "rating": 82.0,
    "type": "full",
    "skills": null,
    "experience_years": 5,
    "performance_score": 75.2
  },
  {
    "employee_id": "emp_steve_gabel",
    "full_name": "Steve Gabel",
    "email": "steve@payready.com",
    "job_title": "VP Strategic Initiatives",
    "department": "Strategy",
    "manager_id": "emp_lynn_musil",
    "manager_name": "Lynn Patrick Musil",
    "level": 2,
    "role_code": "VP_Strategic",
    "competitors": ["Market Analysis"],
    "segments": ["All Segments"],
    "functions": ["Strategic Planning"],
    "regions": ["National"],
    "rating": 78.0,
    "type": "full",
    "skills": null,
    "experience_years": 3,
    "performance_score": 73.1
  }
]
```

### Employees CSV
```csv
Full Name,Email,Job Title,Department,Location
Jane Smith,jane.smith@payready.com,VP of Sales,Sales,New York
John Doe,john.doe@payready.com,Senior Engineer,Engineering,San Francisco
```

### Gong Users JSON
```json
[
  {
    "userId": "gong_123",
    "email": "jane.smith@payready.com",
    "name": "Jane Smith"
  }
]
```

### Slack Users JSON
```json
{
  "members": [
    {
      "id": "U123456",
      "profile": {
        "email": "jane.smith@payready.com",
        "real_name": "Jane Smith"
      }
    }
  ]
}
```

---

## 🚨 Troubleshooting

### Issue: "Database not configured"
**Solution**: Make sure you've added the database IDs to your .env file

### Issue: "Cannot connect to MCP server"
**Solution**: Ensure the server is running on port 9003

### Issue: "No results found"
**Solution**: Check that you've imported data to Notion

### Issue: "Notion API error"
**Solution**: Verify your NOTION_API_KEY is correct

### Issue: "Power Users not found"
**Solution**: Ensure POWER_USERS_DB_ID is configured and the database exists

---

## 🎯 Next Steps

Once the basic system is working:

1. **Add More Data**: Import full employee and customer lists
2. **Enhance Search**: Add fuzzy matching and semantic search
3. **Build Relationships**: Create employee-customer mappings
4. **Add Integrations**: Connect Slack and Gong for auto-updates
5. **Deploy to Production**: Use Docker for production deployment
6. **Power User Analytics**: Track power user engagement and system usage

---

## 📞 Need Help?

1. Check the validation report: `validation_report_*.json`
2. Review server logs for errors
3. Ensure all database IDs are correctly configured
4. Verify data was imported to Notion

The system should be fully operational in 30 minutes!
