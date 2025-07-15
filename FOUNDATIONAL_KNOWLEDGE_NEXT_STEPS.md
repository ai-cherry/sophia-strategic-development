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

**🥇 Power Users (Key Stakeholders)**
- Executive leadership team
- Strategic decision-makers
- High-privilege users
- Beta testers and champions
- Fields: employee_id, role_code, competitive_focus, strategic_functions, performance_metrics

### Sample Files Structure:
```
sample_data/
├── employees_export.csv
├── customers_export.csv
├── gong_users.json
├── slack_users.json
└── power_users_export.csv
```

### 🥇 Power Users Data Strategy

**Who Qualifies as Power Users:**
- C-Suite Executives (CEO, CPO, CTO, etc.)
- VP-level strategic leaders
- Department heads with strategic influence
- Beta testers and product champions
- Key account managers
- Technical architects and senior engineers

**Core Power User Attributes:**
```csv
Employee ID,Full Name,Email,Job Title,Department,Manager ID,Role Code,Level,Competitors,Segments,Functions,Regions,Rating,Type,Experience Years,Performance Score
```

**Sample Power Users (Pre-populate):**
1. **Lynn Patrick Musil** (CEO)
   - Role: Strategic oversight, competitive positioning
   - Focus: EliseAI, Entrata competitors
   - Segments: Multifamily properties
   - Functions: Strategic planning, executive decisions

2. **Tiffany York** (CPO) 
   - Role: Product strategy, feature prioritization
   - Focus: EliseAI competitive analysis
   - Segments: Multifamily market
   - Functions: Product strategy, roadmap planning

3. **Steve Gabel** (VP Strategic Initiatives)
   - Role: Strategic analysis, market research
   - Focus: Market analysis across segments
   - Functions: Strategic planning, competitive intelligence

**Power User Analytics to Track:**
- System usage patterns
- Feature adoption rates
- Feedback submission frequency
- Strategic decision influence
- Cross-functional collaboration
- Competitive intelligence contributions

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
- **Power user relationship patterns**

### Review Session:
We'll look at the analysis together and:
1. Identify core fields to keep
2. Spot relationship patterns
3. Find correlation fields
4. Design minimal schema
5. **Map power user hierarchies and influence networks**

## 🏗️ Step 3: Build Minimal Schema (Day 3)

Based on real data, we'll create schema with:
- Only fields that have data
- Proper data types from samples
- Correlation IDs for each system
- Simple relationships
- **Power user privilege levels and permissions**

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

-- Power Users with enhanced attributes:
CREATE TABLE POWER_USERS (
    EMPLOYEE_ID VARCHAR(255) PRIMARY KEY,
    ROLE_CODE VARCHAR(50),              -- CEO, CPO, VP_Strategic, etc.
    PRIVILEGE_LEVEL INTEGER,            -- 1=C-Suite, 2=VP, 3=Director
    COMPETITIVE_FOCUS ARRAY,            -- ["EliseAI", "Entrata"]
    STRATEGIC_FUNCTIONS ARRAY,          -- ["Strategic Planning", "Product Strategy"]
    PERFORMANCE_SCORE FLOAT,           -- Quantified performance metric
    INFLUENCE_SCORE FLOAT,             -- Strategic influence measurement
    -- Reference to main employees table
    FOREIGN KEY (EMPLOYEE_ID) REFERENCES EMPLOYEES(EMPLOYEE_ID)
);
```

## 🚀 Step 4: Staging Options

### Option A: Streamlit Staging App (Recommended)
```bash
# Run the staging app with Power Users support
streamlit run scripts/foundational_knowledge_staging.py
```

Benefits:
- Visual data review
- Field mapping UI
- Correlation preview
- Import validation
- **Power user privilege assignment**
- **Influence network visualization**

### Option B: Direct SQL Staging
```sql
-- Create staging tables
CREATE TABLE STAGE_EMPLOYEES_RAW (
    ROW_DATA VARIANT,
    SOURCE_FILE VARCHAR(255),
    LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE STAGE_POWER_USERS_RAW (
    ROW_DATA VARIANT,
    SOURCE_FILE VARCHAR(255), 
    PRIVILEGE_LEVEL INTEGER,
    LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Load JSON/CSV directly
COPY INTO STAGE_POWER_USERS_RAW
FROM @my_stage/power_users_export.csv
FILE_FORMAT = (TYPE = CSV);
```

### Option C: Notion/Google Sheets Parking Lot
Good for:
- Collaborative editing
- Non-technical users
- Initial brainstorming
- **Executive stakeholder review**

Process:
1. Create Notion database with power user fields
2. Manually enter/edit strategic stakeholder data
3. Define privilege levels and influence networks
4. Export as CSV
5. Import to staging

## 📊 Step 5: Correlation & Import (Day 4-5)

### Correlation Strategy:
```python
# 1. Email-based matching (primary)
# 2. Name-based matching (secondary)  
# 3. Role-based verification (power users)
# 4. Manual review for conflicts

def correlate_power_users():
    # Match by email first
    matches = match_by_email()

    # Verify executive roles and titles
    role_verification = verify_executive_roles()

    # Cross-reference with org chart
    hierarchy_check = validate_reporting_structure()

    # Review privilege assignments
    return prepare_power_user_review(matches, role_verification, hierarchy_check)
```

### Import Process:
1. Load to staging tables
2. Run correlation matching
3. **Validate power user privileges and permissions**
4. **Map influence networks and reporting relationships**
5. Review & fix issues
6. Commit to main tables

## 🎯 Immediate Action Items

### For You:
1. **Export sample data** (sanitize if needed):
   - 20-30 employees (CSV)
   - 20-30 customers (CSV)
   - Gong user list (JSON)
   - Slack user directory (JSON)
   - **5-10 power users (CSV) - start with C-Suite and VPs**

2. **Share data structure** (not actual data if sensitive):
   - Column names
   - Sample values (anonymized)
   - File formats
   - **Power user privilege definitions**

3. **Define Power User Categories**:
   - Executive tier (C-Suite)
   - Strategic tier (VPs, Directors)
   - Operational tier (Senior Managers)
   - Champion tier (Beta testers, advocates)

### For Us Together:
1. **Analysis session** (1-2 hours):
   - Review data patterns
   - Design schema
   - Plan correlations
   - **Map power user influence networks**

2. **Build & test** (2-3 hours):
   - Create schema
   - Load sample data
   - Test searches
   - **Validate power user permissions and access patterns**

## 💡 Why This Works Better

1. **No Assumptions**: We see exactly what data you have
2. **Right-Sized Schema**: Only fields that exist
3. **Real Correlations**: Actual ID mappings
4. **Quick Validation**: Test with real searches
5. **Fast Iteration**: Adjust based on findings
6. **Strategic Alignment**: Power users mapped to business influence**

## 🚫 What We're NOT Doing Yet

- Complex JSON structures (wait for patterns)
- AI embeddings (need content first)
- Real-time sync (batch is fine)
- Full automation (manual reveals needs)
- Production scale (sample data first)
- **Complex privilege inheritance (start simple)**

## 📈 Success Timeline

- **Day 1**: You export sample data (including power users)
- **Day 2**: We analyze together (including influence patterns)
- **Day 3**: Schema designed and deployed (with power user tables)
- **Day 4**: Sample data loaded (with privilege validation)
- **Day 5**: Correlations working (including power user hierarchies)
- **Week 2**: Ready for full data (with complete user management)

## 🥇 Power User Success Metrics

- **Coverage**: All C-Suite and VP+ roles identified
- **Accuracy**: Correct privilege levels and reporting structure
- **Completeness**: Strategic functions and competitive focus captured
- **Usability**: Easy search and discovery via chat interface
- **Security**: Appropriate access controls and audit trails

## 🎉 Let's Start!

1. **Export your sample data** (including power users - even 5 records is enough)
2. **Run the analysis script** to see patterns
3. **We'll design the perfect schema** based on YOUR data
4. **Import and validate** with real use cases
5. **Set up power user privileges** and access controls

This approach ensures we build exactly what you need, not what we think you might need!

**Ready to begin? Start with exporting those sample files (including power users)!** 📊
