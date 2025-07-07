# Foundational Knowledge Quick Start Guide

## 🚀 TL;DR - Get Started in 30 Minutes

### Step 1: Deploy Minimal Schema (5 min)
```sql
-- Run in Snowflake
USE DATABASE SOPHIA_AI;
source scripts/create_foundational_knowledge_schema.sql
```

### Step 2: Add Your First Data (10 min)
```sql
-- Add yourself as an employee
INSERT INTO FOUNDATIONAL_KNOWLEDGE.EMPLOYEES 
(FIRST_NAME, LAST_NAME, EMAIL, JOB_TITLE, DEPARTMENT)
VALUES ('Your', 'Name', 'you@company.com', 'Your Title', 'Your Dept');

-- Add a key customer
INSERT INTO FOUNDATIONAL_KNOWLEDGE.CUSTOMERS 
(COMPANY_NAME, INDUSTRY, STATUS, TIER)
VALUES ('Your Best Customer', 'Their Industry', 'active', 'enterprise');
```

### Step 3: Test Search (5 min)
```sql
-- Search for entities
CALL FOUNDATIONAL_KNOWLEDGE.SEARCH_KNOWLEDGE('customer');

-- View all data
SELECT * FROM FOUNDATIONAL_KNOWLEDGE.VW_KNOWLEDGE_SEARCH;
```

### Step 4: Import More Data (10 min)
Create a CSV with these columns and import:
- **Employees**: email, first_name, last_name, job_title, department
- **Customers**: company_name, industry, status, tier

## 📋 What We Built vs What We Skipped

### ✅ Built (Essential Framework)
- 4 simple tables (Employees, Customers, Products, Competitors)
- Basic fields only (10-15 per table)
- Simple search view
- Basic CRUD operations
- CSV import capability

### ❌ Skipped (For Later)
- Vector embeddings (no content to embed yet)
- AI summaries (need real data first)
- Complex JSON fields (wait for patterns)
- Real-time sync (batch is fine)
- Advanced RBAC (basic roles work)

## 🎯 Smart First Steps for Real Data

### Week 1: Manual Entry
1. **Add 10 employees** - Start with leadership team
2. **Add 10 customers** - Your most important ones
3. **Add 5 products** - Core offerings only
4. **Add 3 competitors** - Direct competitors

### Week 2: Bulk Import
1. **Export from existing systems**:
   - Employee list from HR
   - Customer list from CRM
   - Product catalog from docs

2. **Use simple CSV format**:
   ```csv
   email,first_name,last_name,job_title,department
   john.doe@company.com,John,Doe,CEO,Executive
   jane.smith@company.com,Jane,Smith,CTO,Engineering
   ```

3. **Import via Python script**:
   ```python
   import pandas as pd
   
   df = pd.read_csv('employees.csv')
   for _, row in df.iterrows():
       handler.create_employee(row.to_dict())
   ```

### Week 3: Connect Systems
1. **Gong Integration**:
   - Just map user IDs first
   - Don't sync call data yet

2. **HubSpot Integration**:
   - Sync company records only
   - Skip contacts initially

3. **Slack Integration**:
   - Map user IDs only
   - No message import

## 🔍 What to Look For

As you add real data, watch for:
1. **Empty fields** - Remove from schema
2. **Missing fields** - Add as needed
3. **Data patterns** - Inform JSON structure
4. **Relationships** - Guide foreign keys
5. **Search needs** - Drive indexing

## 📈 Success Metrics

### Week 1 Success:
- [ ] Schema deployed
- [ ] 20+ manual records
- [ ] Search working
- [ ] Team can add data

### Week 2 Success:
- [ ] 100+ employees imported
- [ ] 50+ customers imported
- [ ] Import process documented
- [ ] Data quality validated

### Week 3 Success:
- [ ] External IDs mapped
- [ ] Basic integration working
- [ ] Schema adjustments identified
- [ ] Ready for enhancement

## 🚫 Common Mistakes to Avoid

1. **Don't over-design fields** - Add only what you use
2. **Don't build complex UIs** - Use SQL directly first
3. **Don't automate too early** - Manual process reveals needs
4. **Don't optimize performance** - Get data in first
5. **Don't add AI features** - Need content to work with

## 💡 Pro Tips

1. **Start with executives** - They're most searched
2. **Focus on active data** - Skip historical records
3. **Use spreadsheets** - Easiest for initial data prep
4. **Document as you go** - Track what fields mean
5. **Get feedback early** - Show search to users

## 🎉 Next Steps

Once you have 100+ records:
1. **Analyze usage** - What do people search for?
2. **Identify patterns** - What fields are always empty?
3. **Plan enhancements** - Vector search, AI summaries
4. **Build integrations** - Real-time sync with source systems
5. **Add intelligence** - Embeddings, recommendations

Remember: **Simple and working beats complex and planned!** 