# Foundational Knowledge - Your Next Steps

## 🎯 Best Approach: Real Sample Data First

Based on your suggestion, **working with real sample data is the best approach**. Here's exactly what to do:

## 📋 Step 1: Gather Sample Data (Day 1)

### What to Export:

**Employee Roster (from HR system)**
- Export 20-30 employees as CSV
- Include: Leadership, managers, key contributors
- Fields: email, name, title, department, manager

**Gong Data (via Export)**
- User list with emails
- Don't need call transcripts yet
- Just user metadata

**Slack Data (via API or Export)**
- User directory only
- Channels and membership
- No messages needed

**Customer List (from CRM)**
- Top 20-30 customers
- Basic info: name, industry, tier, revenue

### Sample Files Structure:
```
sample_data/
├── employees_export.csv
├── customers_export.csv
├── gong_users.json
└── slack_users.json
```

## 🔍 Step 2: Analyze Together (Day 2)

### Run Analysis Script:
```bash
python scripts/analyze_sample_data.py ./sample_data/
```

This will show us:
- Which fields are always populated
- Which fields are always empty
- Data type patterns
- Correlation opportunities

### Review Session:
We'll look at the analysis together and:
1. Identify core fields to keep
2. Spot relationship patterns
3. Find correlation fields
4. Design minimal schema

## 🏗️ Step 3: Build Minimal Schema (Day 3)

Based on real data, we'll create schema with:
- Only fields that have data
- Proper data types from samples
- Correlation IDs for each system
- Simple relationships

Example discovery:
```sql
-- If we find all employees have Slack but only some have Gong:
CREATE TABLE EMPLOYEES (
    EMPLOYEE_ID VARCHAR(255) PRIMARY KEY,
    EMAIL VARCHAR(255) NOT NULL,        -- Always present
    SLACK_USER_ID VARCHAR(255),         -- Always present
    GONG_USER_ID VARCHAR(255),          -- Sometimes null
    -- Skip fields that are always empty
);
```

## 🚀 Step 4: Staging Options

### Option A: Streamlit Staging App (Recommended)
```bash
# Run the staging app
streamlit run scripts/foundational_knowledge_staging.py
```

Benefits:
- Visual data review
- Field mapping UI
- Correlation preview
- Import validation

### Option B: Direct SQL Staging
```sql
-- Create staging tables
CREATE TABLE STAGE_EMPLOYEES_RAW (
    ROW_DATA VARIANT,
    SOURCE_FILE VARCHAR(255),
    LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Load JSON/CSV directly
COPY INTO STAGE_EMPLOYEES_RAW
FROM @my_stage/employees_export.csv
FILE_FORMAT = (TYPE = CSV);
```

### Option C: Notion/Google Sheets Parking Lot
Good for:
- Collaborative editing
- Non-technical users
- Initial brainstorming

Process:
1. Create Notion database with core fields
2. Manually enter/edit sample data
3. Export as CSV
4. Import to staging

## 📊 Step 5: Correlation & Import (Day 4-5)

### Correlation Strategy:
```python
# 1. Email-based matching (primary)
# 2. Name-based matching (secondary)
# 3. Manual review for conflicts

def correlate_employees():
    # Match by email first
    matches = match_by_email()

    # Then fuzzy name matching
    fuzzy = match_by_name_similarity()

    # Review ambiguous cases
    return prepare_review_list(matches, fuzzy)
```

### Import Process:
1. Load to staging tables
2. Run correlation matching
3. Review & fix issues
4. Commit to main tables

## 🎯 Immediate Action Items

### For You:
1. **Export sample data** (sanitize if needed):
   - 20-30 employees (CSV)
   - 20-30 customers (CSV)
   - Gong user list (JSON)
   - Slack user directory (JSON)

2. **Share data structure** (not actual data if sensitive):
   - Column names
   - Sample values (anonymized)
   - File formats

### For Us Together:
1. **Analysis session** (1-2 hours):
   - Review data patterns
   - Design schema
   - Plan correlations

2. **Build & test** (2-3 hours):
   - Create schema
   - Load sample data
   - Test searches

## 💡 Why This Works Better

1. **No Assumptions**: We see exactly what data you have
2. **Right-Sized Schema**: Only fields that exist
3. **Real Correlations**: Actual ID mappings
4. **Quick Validation**: Test with real searches
5. **Fast Iteration**: Adjust based on findings

## 🚫 What We're NOT Doing Yet

- Complex JSON structures (wait for patterns)
- AI embeddings (need content first)
- Real-time sync (batch is fine)
- Full automation (manual reveals needs)
- Production scale (sample data first)

## 📈 Success Timeline

- **Day 1**: You export sample data
- **Day 2**: We analyze together
- **Day 3**: Schema designed and deployed
- **Day 4**: Sample data loaded
- **Day 5**: Correlations working
- **Week 2**: Ready for full data

## 🎉 Let's Start!

1. **Export your sample data** (even 10 records per type is enough)
2. **Run the analysis script** to see patterns
3. **We'll design the perfect schema** based on YOUR data
4. **Import and validate** with real use cases

This approach ensures we build exactly what you need, not what we think you might need!

**Ready to begin? Start with exporting those sample files!** 📊
