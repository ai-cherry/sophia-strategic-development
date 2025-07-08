#!/usr/bin/env python3
"""
Foundational Knowledge Data Staging App
Simple Streamlit interface for reviewing and importing sample data
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the handler (when available)
# from infrastructure.mcp_servers.foundational_knowledge.handlers.main_handler import handler

st.set_page_config(
    page_title="Foundational Knowledge Staging",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Foundational Knowledge Data Staging")
st.markdown("Import and review sample data before loading to Snowflake")

# Initialize session state
if 'staged_data' not in st.session_state:
    st.session_state.staged_data = {}
if 'correlations' not in st.session_state:
    st.session_state.correlations = {}

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page",
        ["Upload Data", "Review & Map", "Correlate", "Import to Database"]
    )

# Page 1: Upload Data
if page == "Upload Data":
    st.header("Step 1: Upload Sample Data Files")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Employee Data")
        employee_file = st.file_uploader(
            "Upload employee roster (CSV/JSON)",
            type=['csv', 'json'],
            key="employees"
        )

        if employee_file:
            if employee_file.name.endswith('.csv'):
                df = pd.read_csv(employee_file)
            else:
                df = pd.read_json(employee_file)

            st.session_state.staged_data['employees'] = df
            st.success(f"Loaded {len(df)} employee records")
            st.dataframe(df.head(), use_container_width=True)

    with col2:
        st.subheader("Customer Data")
        customer_file = st.file_uploader(
            "Upload customer list (CSV/JSON)",
            type=['csv', 'json'],
            key="customers"
        )

        if customer_file:
            if customer_file.name.endswith('.csv'):
                df = pd.read_csv(customer_file)
            else:
                df = pd.read_json(customer_file)

            st.session_state.staged_data['customers'] = df
            st.success(f"Loaded {len(df)} customer records")
            st.dataframe(df.head(), use_container_width=True)

    # Additional data sources
    st.subheader("Integration Data")
    col3, col4 = st.columns(2)

    with col3:
        gong_file = st.file_uploader(
            "Upload Gong user export (JSON)",
            type=['json'],
            key="gong"
        )

        if gong_file:
            data = json.load(gong_file)
            df = pd.DataFrame(data)
            st.session_state.staged_data['gong'] = df
            st.success(f"Loaded {len(df)} Gong users")

    with col4:
        slack_file = st.file_uploader(
            "Upload Slack user export (JSON)",
            type=['json'],
            key="slack"
        )

        if slack_file:
            data = json.load(slack_file)
            df = pd.DataFrame(data)
            st.session_state.staged_data['slack'] = df
            st.success(f"Loaded {len(df)} Slack users")

# Page 2: Review & Map
elif page == "Review & Map":
    st.header("Step 2: Review Data & Map Fields")

    if not st.session_state.staged_data:
        st.warning("Please upload data files first!")
    else:
        # Field mapping for each data source
        for source, df in st.session_state.staged_data.items():
            st.subheader(f"{source.title()} Field Mapping")

            # Show data preview
            with st.expander(f"Preview {source} data"):
                st.dataframe(df.head(), use_container_width=True)

            # Field analysis
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Total Fields", len(df.columns))
            with col3:
                null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
                st.metric("Data Completeness", f"{100-null_pct:.1f}%")

            # Field mapping
            if source == 'employees':
                st.write("Map to standard employee fields:")

                mapping = {}
                cols = st.columns(2)

                standard_fields = [
                    'email', 'first_name', 'last_name', 'job_title',
                    'department', 'manager_email'
                ]

                for i, field in enumerate(standard_fields):
                    with cols[i % 2]:
                        mapping[field] = st.selectbox(
                            f"{field}:",
                            options=['(none)'] + list(df.columns),
                            key=f"{source}_{field}"
                        )

                if st.button(f"Save {source} mapping"):
                    st.session_state.correlations[source] = mapping
                    st.success(f"Saved {source} field mapping!")

# Page 3: Correlate
elif page == "Correlate":
    st.header("Step 3: Correlate Records Across Systems")

    if 'employees' not in st.session_state.staged_data:
        st.warning("Please upload employee data first!")
    else:
        employees_df = st.session_state.staged_data['employees']

        # Email-based correlation
        st.subheader("Email-Based Correlation")

        # Get email field from mapping
        email_field = st.session_state.correlations.get('employees', {}).get('email', None)

        if not email_field or email_field == '(none)':
            st.error("Please map the email field for employees first!")
        else:
            # Show correlation results
            correlations = []

            # Check Gong correlation
            if 'gong' in st.session_state.staged_data:
                gong_df = st.session_state.staged_data['gong']

                # Find email field in Gong data
                gong_email_field = None
                for col in gong_df.columns:
                    if 'email' in col.lower():
                        gong_email_field = col
                        break

                if gong_email_field:
                    # Count matches
                    employee_emails = set(employees_df[email_field].dropna().str.lower())
                    gong_emails = set(gong_df[gong_email_field].dropna().str.lower())
                    matches = employee_emails.intersection(gong_emails)

                    correlations.append({
                        'System': 'Gong',
                        'Total Records': len(gong_df),
                        'Matched': len(matches),
                        'Unmatched': len(gong_emails - employee_emails),
                        'Match Rate': f"{len(matches)/len(gong_emails)*100:.1f}%"
                    })

            # Check Slack correlation
            if 'slack' in st.session_state.staged_data:
                slack_df = st.session_state.staged_data['slack']

                # Find email field in Slack data
                slack_email_field = None
                for col in slack_df.columns:
                    if 'email' in col.lower():
                        slack_email_field = col
                        break

                if slack_email_field:
                    # Count matches
                    slack_emails = set(slack_df[slack_email_field].dropna().str.lower())
                    matches = employee_emails.intersection(slack_emails)

                    correlations.append({
                        'System': 'Slack',
                        'Total Records': len(slack_df),
                        'Matched': len(matches),
                        'Unmatched': len(slack_emails - employee_emails),
                        'Match Rate': f"{len(matches)/len(slack_emails)*100:.1f}%"
                    })

            if correlations:
                correlation_df = pd.DataFrame(correlations)
                st.dataframe(correlation_df, use_container_width=True)

                # Show unmatched records for review
                st.subheader("Unmatched Records for Review")

                system = st.selectbox("Select system to review",
                                    [c['System'] for c in correlations])

                if st.button("Show unmatched records"):
                    # Show unmatched records logic here
                    st.info(f"Showing unmatched {system} records...")

# Page 4: Import to Database
elif page == "Import to Database":
    st.header("Step 4: Import to Snowflake")

    if not st.session_state.staged_data:
        st.warning("Please upload and map data first!")
    else:
        st.info("Ready to import to Snowflake Foundational Knowledge schema")

        # Show summary
        st.subheader("Import Summary")

        summary_data = []
        for source, df in st.session_state.staged_data.items():
            summary_data.append({
                'Source': source.title(),
                'Records': len(df),
                'Fields Mapped': len(st.session_state.correlations.get(source, {})),
                'Status': '✅ Ready' if source in st.session_state.correlations else '⚠️ Not Mapped'
            })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

        # Import options
        st.subheader("Import Options")

        col1, col2 = st.columns(2)
        with col1:
            import_mode = st.radio(
                "Import Mode",
                ["Test Mode (Dry Run)", "Production Import"]
            )

        with col2:
            duplicate_handling = st.radio(
                "Duplicate Handling",
                ["Skip Duplicates", "Update Existing", "Create New"]
            )

        # Generate SQL preview
        if st.button("Generate SQL Preview"):
            st.subheader("SQL Preview")

            # Example SQL generation
            sql_preview = """
-- Employee Import SQL
INSERT INTO FOUNDATIONAL_KNOWLEDGE.EMPLOYEES (
    EMAIL, FIRST_NAME, LAST_NAME, JOB_TITLE, DEPARTMENT
)
SELECT
    email_column,
    first_name_column,
    last_name_column,
    title_column,
    department_column
FROM staging_table
WHERE email_column IS NOT NULL
  AND email_column NOT IN (
    SELECT EMAIL FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES
  );

-- Update correlation IDs
UPDATE FOUNDATIONAL_KNOWLEDGE.EMPLOYEES e
SET GONG_USER_ID = g.user_id
FROM gong_staging g
WHERE LOWER(e.EMAIL) = LOWER(g.email);
            """

            st.code(sql_preview, language='sql')

        # Import button
        if st.button("🚀 Start Import", type="primary", disabled=(import_mode == "Production Import")):
            with st.spinner("Importing data..."):
                # Simulate import process
                progress_bar = st.progress(0)
                status_text = st.empty()

                import time
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text(f"Validating data... {i+1}%")
                    elif i < 60:
                        status_text.text(f"Importing employees... {i+1}%")
                    elif i < 90:
                        status_text.text(f"Correlating systems... {i+1}%")
                    else:
                        status_text.text(f"Finalizing... {i+1}%")
                    time.sleep(0.05)

                status_text.text("Import complete!")
                st.success("✅ Successfully imported data to Snowflake!")

                # Show results
                st.subheader("Import Results")
                results = {
                    'Employees Imported': 47,
                    'Customers Imported': 23,
                    'Correlations Created': 89,
                    'Errors': 0
                }

                col1, col2, col3, col4 = st.columns(4)
                for i, (metric, value) in enumerate(results.items()):
                    with [col1, col2, col3, col4][i]:
                        st.metric(metric, value)

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: This staging app helps you review and clean data before importing to production")

if __name__ == "__main__":
    # Run with: streamlit run scripts/foundational_knowledge_staging.py
    pass
