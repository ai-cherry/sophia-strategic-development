# Foundational Knowledge Unified Implementation Plan
## Combining Notion Integration with Sample Data Approach

**Author:** Sophia AI Team
**Date:** January 8, 2025
**Implementation Timeline:** 5-7 Days to Production

---

## 🎯 Executive Summary

This plan combines Manus AI's comprehensive Notion-based system with our practical sample data approach. We'll use Notion as the primary UI for data entry and management while building the technical infrastructure to support Sophia AI integration.

### Key Decisions:
1. **Notion as Primary Interface**: Leverage existing Notion workspace for immediate usability
2. **Sample Data First**: Start with real exports to design perfect schema
3. **Incremental Integration**: Build bridges to external systems as needed
4. **Fast Path to Value**: Working system in 5 days, full integration in 2 weeks

---

## 📊 Implementation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Notion Workspace                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Employees │ │Customers │ │Competitors│ │Products  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │ Notion API
                      ▼
         ┌────────────────────────┐
         │ Enhanced Notion MCP    │ Port: 9003
         │ Server (Simplified)    │
         └────────────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│   Snowflake     │      │   Sophia AI     │
│ (Long-term)     │      │ (Immediate)     │
└─────────────────┘      └─────────────────┘
```

---

## 🚀 Day-by-Day Implementation Plan

### Day 1: Sample Data Analysis & Notion Setup (4 hours)

**Morning (2 hours): Data Collection**
```bash
# 1. Export sample data from existing systems
- Employee roster (20-30 records) from HR/Slack
- Customer list (20-30 records) from CRM
- Gong user list via API
- Competitor intel from existing docs

# 2. Analyze data together
python scripts/analyze_sample_data.py data_exports/
```

**Afternoon (2 hours): Notion Workspace Setup**
```python
# Run simplified Notion setup
python scripts/setup_notion_simple.py

# This creates:
- 👥 Employees (10 fields based on sample data)
- 🏢 Customers (12 fields based on sample data)
- 🥊 Competitors (8 fields)
- 📦 Products (10 fields)
```

### Day 2: Data Import & Correlation (4 hours)

**Morning: Import Sample Data to Notion**
```python
# Use staging app to review and import
streamlit run scripts/foundational_knowledge_staging.py

# Features:
- Upload CSV/JSON files
- Map columns to Notion fields
- Preview before import
- Handle duplicates
```

**Afternoon: Cross-System Correlation**
```python
# Correlate employees across systems
python scripts/correlate_entities.py \
  --employees data_exports/employees.csv \
  --gong data_exports/gong_users.json \
  --slack data_exports/slack_users.json
```

### Day 3: Simplified MCP Server (6 hours)

**Create Minimal Notion MCP Server**
```python
# infrastructure/mcp_servers/notion_simple/server.py
from fastapi import FastAPI
from notion_client import Client
import os

app = FastAPI(title="Notion Knowledge MCP")
notion = Client(auth=os.getenv("NOTION_API_KEY"))

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "notion_simple"}

@app.post("/search")
async def search(query: str, entity_type: str = None):
    """Search foundational knowledge"""
    databases = {
        "employees": os.getenv("EMPLOYEES_DB_ID"),
        "customers": os.getenv("CUSTOMERS_DB_ID"),
        "competitors": os.getenv("COMPETITORS_DB_ID"),
        "products": os.getenv("PRODUCTS_DB_ID")
    }

    results = []
    for db_type, db_id in databases.items():
        if entity_type and entity_type != db_type:
            continue

        response = notion.databases.query(
            database_id=db_id,
            filter={
                "or": [
                    {"property": "Name", "title": {"contains": query}},
                    {"property": "Email", "email": {"contains": query}}
                ]
            }
        )
        results.extend(response["results"])

    return {"results": results, "count": len(results)}

@app.get("/employees/{email}")
async def get_employee(email: str):
    """Get employee by email"""
    response = notion.databases.query(
        database_id=os.getenv("EMPLOYEES_DB_ID"),
        filter={"property": "Email", "email": {"equals": email}}
    )
    return response["results"][0] if response["results"] else None
```

### Day 4: Sophia AI Integration (4 hours)

**Morning: Connect to Sophia AI**
```python
# Add to existing chat service
class EnhancedChatService:
    def __init__(self):
        self.notion_mcp = NotionMCPClient(
            base_url="http://localhost:9003"
        )

    async def process_query(self, query: str):
        # Check for foundational knowledge queries
        if "who is" in query.lower():
            # Search employees
            results = await self.notion_mcp.search(
                query=query.split("who is")[-1].strip(),
                entity_type="employees"
            )

        elif "customer" in query.lower():
            # Search customers
            results = await self.notion_mcp.search(
                query=extract_company_name(query),
                entity_type="customers"
            )
```

**Afternoon: Test Natural Language Queries**
```python
# Test queries
test_queries = [
    "Who is John Smith?",
    "What do we know about Acme Corp?",
    "Show me our main competitors",
    "What products do we offer?",
    "Who handles the Acme Corp account?"
]

for query in test_queries:
    response = await chat_service.process_query(query)
    print(f"Q: {query}\nA: {response}\n")
```

### Day 5: Production Deployment (4 hours)

**Morning: Deploy Services**
```bash
# 1. Deploy Notion MCP Server
cd infrastructure/mcp_servers/notion_simple
docker build -t notion-mcp .
docker run -d -p 9003:9003 --env-file .env notion-mcp

# 2. Update Sophia AI configuration
python scripts/update_sophia_config.py \
  --add-service notion_mcp \
  --endpoint http://localhost:9003
```

**Afternoon: Validation & Documentation**
```python
# Run validation suite
python scripts/validate_foundational_knowledge.py

# Generates report:
- ✅ Notion databases created and populated
- ✅ MCP server responding
- ✅ Search functionality working
- ✅ Sophia AI integration active
- ✅ Natural language queries functional
```

---

## 📁 Simplified File Structure

```
infrastructure/mcp_servers/notion_simple/
├── server.py           # Minimal FastAPI server (200 lines)
├── handlers.py         # Notion operations (150 lines)
├── models.py          # Data models (50 lines)
├── requirements.txt   # Just 5 dependencies
└── Dockerfile         # Simple deployment

scripts/
├── setup_notion_simple.py         # Create databases (150 lines)
├── analyze_sample_data.py         # Analyze exports (100 lines)
├── foundational_knowledge_staging.py  # Streamlit UI (200 lines)
├── correlate_entities.py          # Match across systems (150 lines)
└── validate_foundational_knowledge.py # Test everything (100 lines)
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Notion (already have this)
NOTION_API_KEY=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

# Database IDs (will be set after creation)
EMPLOYEES_DB_ID=
CUSTOMERS_DB_ID=
COMPETITORS_DB_ID=
PRODUCTS_DB_ID=

# Server config
NOTION_MCP_PORT=9003
LOG_LEVEL=INFO
```

### Minimal Dependencies
```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
notion-client==2.2.1
pydantic==2.5.0
pandas==2.1.4
streamlit==1.29.0  # Only for staging UI
```

---

## 📊 Schema Design (Based on Real Data)

### Employees (Simplified from Sample Data)
```python
employee_properties = {
    "Full Name": {"title": {}},
    "Email": {"email": {}},
    "Job Title": {"rich_text": {}},
    "Department": {"select": {
        "options": ["Sales", "Engineering", "Marketing", "Operations"]
    }},
    "Slack ID": {"rich_text": {}},
    "Gong ID": {"rich_text": {}},
    "Manager Email": {"email": {}},
    "Start Date": {"date": {}},
    "Location": {"rich_text": {}},
    "Status": {"select": {
        "options": ["Active", "On Leave", "Former"]
    }}
}
```

### Customers (Simplified from Sample Data)
```python
customer_properties = {
    "Company Name": {"title": {}},
    "Industry": {"select": {
        "options": ["Technology", "Healthcare", "Finance", "Retail"]
    }},
    "Customer Since": {"date": {}},
    "Annual Revenue": {"number": {"format": "dollar"}},
    "Employee Count": {"rich_text": {}},
    "Website": {"url": {}},
    "Account Owner": {"relation": {"database_id": employees_db_id}},
    "Health Score": {"select": {
        "options": ["Green", "Yellow", "Red"]
    }},
    "CRM ID": {"rich_text": {}},
    "Last Activity": {"date": {}},
    "Notes": {"rich_text": {}},
    "Status": {"select": {
        "options": ["Prospect", "Active", "Churned"]
    }}
}
```

---

## 🎯 Success Criteria

### Day 1 Success
- [ ] Sample data analyzed and patterns documented
- [ ] Notion workspace created with 4 databases
- [ ] Initial schema designed based on real data

### Day 3 Success
- [ ] Sample data imported to Notion
- [ ] Employees correlated across systems
- [ ] Basic MCP server running

### Day 5 Success
- [ ] Natural language queries working in Sophia AI
- [ ] "Who is X?" queries return Notion data
- [ ] "Tell me about customer Y" works
- [ ] Production deployment complete

---

## 🚀 Next Phase (Week 2)

Once the basic system is working:

1. **Add Slack Integration** (from Manus AI plan)
   - Sync team members automatically
   - Keep Slack IDs updated

2. **Add Snowflake Pipeline**
   - Move mature data to Snowflake
   - Enable advanced analytics

3. **Enhance Search**
   - Add fuzzy matching
   - Implement relationship traversal
   - Add semantic search

4. **Build Relationships**
   - Create employee-customer mappings
   - Add interaction history
   - Track engagement metrics

---

## 💡 Key Advantages of This Approach

1. **Immediate Value**: Working system in 5 days
2. **Real Data**: No assumptions, actual patterns
3. **Simple Architecture**: 1000 lines of code total
4. **Notion UI**: No custom UI needed initially
5. **Incremental Growth**: Add complexity as needed

---

## 📝 Implementation Checklist

**Before Starting:**
- [ ] Gather sample data exports (employees, customers, Gong users)
- [ ] Have Notion API key ready
- [ ] Ensure Sophia AI development environment is accessible

**Day 1:**
- [ ] Run data analysis script
- [ ] Create Notion databases
- [ ] Document field mappings

**Day 2:**
- [ ] Import sample data
- [ ] Correlate entities
- [ ] Validate data quality

**Day 3:**
- [ ] Deploy MCP server
- [ ] Test API endpoints
- [ ] Verify search functionality

**Day 4:**
- [ ] Integrate with Sophia AI
- [ ] Test natural language queries
- [ ] Document query patterns

**Day 5:**
- [ ] Production deployment
- [ ] Run validation suite
- [ ] Create user documentation

This unified plan gives us the best of both worlds: Notion's excellent UI with our practical, data-driven approach!
