# Foundational Knowledge Data Strategy - Working with Real Sample Data

## 🎯 Executive Summary

Working with real sample data from the start is the **best approach**. It prevents over-engineering and ensures we build exactly what's needed. Here's a practical strategy combining sample data exploration with a staging approach.

## 📊 Option Analysis

### Option 1: Direct Sample Data Approach ✅ RECOMMENDED
**Process**: Download sample exports → Analyze together → Design schema → Build incrementally

**Pros:**
- See real data patterns immediately
- Avoid assumptions about field needs
- Build exactly what's required
- Fast iteration based on actual data

**Cons:**
- Need to handle sensitive data carefully
- Requires some data prep work

### Option 2: Notion/Google Drive Staging
**Process**: Manual entry in Notion → Export to CSV → Import to Snowflake

**Pros:**
- Easy collaborative editing
- Non-technical users can contribute
- Good for initial brainstorming

**Cons:**
- Extra step in the process
- Data format limitations
- Manual export/import cycle

### Option 3: Foundational Knowledge MCP Server as Staging
**Process**: Build simple UI → Manual entry → Direct to Snowflake

**Pros:**
- Direct database entry
- No export/import needed
- Can validate in real-time

**Cons:**
- Need to build UI first
- More complex than needed initially

## 🚀 Recommended Approach: Smart Sample Data Strategy

### Phase 1: Data Collection & Analysis (Day 1-2)

#### Step 1: Gather Sample Data Exports

**Employee Roster (from HR system)**
```csv
# Get 20-30 employees including:
- Leadership team (5-10)
- Department heads (5-10)
- Key individual contributors (10)
- Mix of departments
```

**Gong Data (via API or Export)**
```json
# Get 10-20 sample records:
- User list with emails
- Recent call metadata (not transcripts)
- Call participants
- Basic call outcomes
```

**Slack Data (via API)**
```json
# Get basic data:
- User directory
- Channel list
- User-channel membership
- NO message content
```

**Customer Data (from CRM)**
```csv
# Get 20-30 customers:
- Top 10 by revenue
- Mix of tiers
- Include churned customers
- Basic fields only
```

#### Step 2: Data Analysis Session

Let's work together to:
1. **Review each export file**
2. **Identify patterns**:
   - Which fields are always populated?
   - Which fields are always empty?
   - What data types are used?
   - What relationships exist?

3. **Document findings**:
```markdown
## Employee Data Analysis
- Always have: email, first_name, last_name
- Sometimes have: manager_email, department, title
- Never have: employee_id (need to generate)
- Surprise finding: Multiple title formats
- Relationship: Manager by email reference
```

### Phase 2: Schema Design (Day 3)

Based on real data, we'll design minimal schema:

```sql
-- Example based on actual data patterns
CREATE TABLE EMPLOYEES (
    -- Core fields (always present)
    EMPLOYEE_ID VARCHAR(255) PRIMARY KEY DEFAULT UUID_STRING(),
    EMAIL VARCHAR(255) UNIQUE NOT NULL,
    FIRST_NAME VARCHAR(255) NOT NULL,
    LAST_NAME VARCHAR(255) NOT NULL,

    -- Common fields (usually present)
    DISPLAY_NAME VARCHAR(255), -- Found in Slack
    JOB_TITLE VARCHAR(255),    -- Varies by system
    DEPARTMENT VARCHAR(255),    -- Sometimes missing

    -- Integration IDs (for correlation)
    GONG_USER_ID VARCHAR(255),      -- From Gong export
    SLACK_USER_ID VARCHAR(255),     -- From Slack export
    SLACK_EMAIL VARCHAR(255),       -- Sometimes different!

    -- Derived fields
    IS_MANAGER BOOLEAN DEFAULT FALSE,
    REPORTS_TO_EMAIL VARCHAR(255),

    -- Metadata
    DATA_SOURCE VARCHAR(50),  -- 'hr', 'gong', 'slack', 'manual'
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Phase 3: Iterative Loading (Day 4-5)

#### Step 1: Create Staging Tables
```sql
-- Raw data staging
CREATE TABLE STAGE_EMPLOYEE_UPLOADS (
    UPLOAD_ID VARCHAR(255) DEFAULT UUID_STRING(),
    SOURCE_SYSTEM VARCHAR(50),
    RAW_DATA VARIANT,  -- JSON blob of original data
    PROCESSED BOOLEAN DEFAULT FALSE,
    UPLOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Step 2: Load Sample Data
```python
# Simple loader script
import pandas as pd
import json

def load_employee_sample(file_path, source_system):
    """Load sample data with source tracking"""

    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        records = df.to_dict('records')
    else:
        with open(file_path) as f:
            records = json.load(f)

    for record in records:
        # Store raw data
        store_staging_record(source_system, record)

        # Transform to our schema
        employee = transform_to_employee(record, source_system)

        # Load to main table
        create_or_update_employee(employee)
```

#### Step 3: Correlation & Deduplication
```python
def correlate_employees():
    """Match employees across systems"""

    # Strategy 1: Email matching
    matches = match_by_email()

    # Strategy 2: Name matching for different emails
    fuzzy_matches = match_by_name()

    # Manual review for ambiguous cases
    return prepare_review_list(matches, fuzzy_matches)
```

### Phase 4: Knowledge Base Integration (Day 6-7)

#### Option A: Simple Staging UI
```python
# Minimal Streamlit app for data review
import streamlit as st

st.title("Foundational Knowledge Staging")

# Show uploaded data
tab1, tab2, tab3 = st.tabs(["Employees", "Customers", "Review Matches"])

with tab1:
    employees = load_staged_employees()
    edited_df = st.data_editor(employees)

    if st.button("Commit to Database"):
        commit_employees(edited_df)
```

#### Option B: Direct SQL Worksheets
```sql
-- Review staging data
SELECT
    SOURCE_SYSTEM,
    RAW_DATA:email::STRING as EMAIL,
    RAW_DATA:name::STRING as NAME,
    RAW_DATA:title::STRING as TITLE
FROM STAGE_EMPLOYEE_UPLOADS
WHERE PROCESSED = FALSE
ORDER BY UPLOADED_AT DESC;

-- Manual correlation
UPDATE EMPLOYEES e1
SET GONG_USER_ID = (
    SELECT RAW_DATA:userId::STRING
    FROM STAGE_EMPLOYEE_UPLOADS
    WHERE SOURCE_SYSTEM = 'gong'
    AND LOWER(RAW_DATA:email::STRING) = LOWER(e1.EMAIL)
    LIMIT 1
)
WHERE GONG_USER_ID IS NULL;
```

## 📋 Recommended Next Steps

### Week 1: Data Collection & Schema Design

**Day 1-2: Collect Sample Data**
1. Export employee roster (CSV)
2. Get Gong user list (API/Export)
3. Pull Slack directory (API)
4. Export top 30 customers (CRM)

**Day 3: Analysis Session**
- Review exports together
- Document patterns
- Identify correlations
- Design minimal schema

**Day 4-5: Initial Load**
- Create staging tables
- Load sample data
- Build correlation logic
- Handle duplicates

### Week 2: Refinement & Integration

**Day 6-7: Data Quality**
- Review loaded data
- Fix correlation issues
- Add missing fields
- Document decisions

**Day 8-9: Integration Setup**
- Map external IDs
- Test basic lookups
- Create unified views
- Build search

**Day 10: Validation**
- User testing
- Search accuracy
- Performance check
- Plan next phase

## 🛠️ Practical Tools & Scripts

### 1. Data Analysis Script
```python
import pandas as pd
import json
from pathlib import Path

def analyze_data_files(directory):
    """Analyze all data files in directory"""

    results = {}

    for file in Path(directory).glob('*'):
        if file.suffix == '.csv':
            df = pd.read_csv(file)
            results[file.name] = {
                'rows': len(df),
                'columns': list(df.columns),
                'null_counts': df.isnull().sum().to_dict(),
                'sample': df.head(3).to_dict()
            }
        elif file.suffix == '.json':
            with open(file) as f:
                data = json.load(f)
            results[file.name] = analyze_json_structure(data)

    return results
```

### 2. Correlation Helper
```sql
-- Find potential matches across systems
CREATE OR REPLACE VIEW VW_EMPLOYEE_CORRELATION AS
SELECT
    e.EMAIL as MASTER_EMAIL,
    e.FIRST_NAME || ' ' || e.LAST_NAME as FULL_NAME,

    -- Gong correlation
    g.RAW_DATA:email::STRING as GONG_EMAIL,
    g.RAW_DATA:userId::STRING as GONG_ID,

    -- Slack correlation
    s.RAW_DATA:email::STRING as SLACK_EMAIL,
    s.RAW_DATA:id::STRING as SLACK_ID,

    -- Match confidence
    CASE
        WHEN LOWER(e.EMAIL) = LOWER(g.RAW_DATA:email::STRING) THEN 'exact'
        WHEN LOWER(e.EMAIL) = LOWER(s.RAW_DATA:email::STRING) THEN 'exact'
        ELSE 'review'
    END as MATCH_CONFIDENCE

FROM EMPLOYEES e
LEFT JOIN STAGE_EMPLOYEE_UPLOADS g
    ON g.SOURCE_SYSTEM = 'gong'
    AND LOWER(e.EMAIL) = LOWER(g.RAW_DATA:email::STRING)
LEFT JOIN STAGE_EMPLOYEE_UPLOADS s
    ON s.SOURCE_SYSTEM = 'slack'
    AND LOWER(e.EMAIL) = LOWER(s.RAW_DATA:email::STRING);
```

### 3. Simple Staging UI
```python
# streamlit_staging.py
import streamlit as st
import pandas as pd
from foundational_knowledge_handler import handler

st.set_page_config(page_title="FK Data Staging", layout="wide")

# File upload
uploaded_file = st.file_uploader("Upload Employee Data", type=['csv', 'json'])

if uploaded_file:
    # Parse file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_json(uploaded_file)

    # Show data
    st.write(f"Loaded {len(df)} records")

    # Edit data
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True
    )

    # Map columns
    st.subheader("Column Mapping")
    col_mapping = {}
    our_fields = ['email', 'first_name', 'last_name', 'job_title', 'department']

    cols = st.columns(2)
    for i, field in enumerate(our_fields):
        with cols[i % 2]:
            col_mapping[field] = st.selectbox(
                f"Map to {field}",
                options=[''] + list(df.columns),
                key=field
            )

    # Import button
    if st.button("Import to Database", type="primary"):
        # Transform and import
        success_count = 0
        for _, row in edited_df.iterrows():
            employee_data = {}
            for our_field, their_field in col_mapping.items():
                if their_field:
                    employee_data[our_field] = row[their_field]

            if employee_data.get('email'):
                result = handler.create_employee(employee_data)
                if result['success']:
                    success_count += 1

        st.success(f"Imported {success_count} employees!")
```

## 🎯 Why This Approach Works

1. **Real Data First**: No assumptions, just facts
2. **Iterative Design**: Schema evolves with understanding
3. **Correlation Built-In**: Handle multiple systems from start
4. **Simple Tools**: CSV, JSON, basic SQL - no complexity
5. **Quick Validation**: See results in days, not weeks

## 📈 Success Metrics

- **Day 3**: Schema designed from real data
- **Day 5**: 50+ employees loaded and correlated
- **Day 7**: Search working across all entities
- **Day 10**: Ready for production data

## 🚀 Let's Start!

1. **You provide**: Sample data exports (sanitized if needed)
2. **We analyze**: Together in a working session
3. **We build**: Minimal schema that fits perfectly
4. **You validate**: With real searches and use cases
5. **We iterate**: Based on what we learn

This approach gets us from zero to useful in 1 week instead of 1 month!
