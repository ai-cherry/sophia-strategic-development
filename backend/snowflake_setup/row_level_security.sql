-- =====================================================================
-- Row-Level Security Policies
-- =====================================================================

-- Customer data access policy
CREATE OR REPLACE ROW ACCESS POLICY CUSTOMER_DATA_POLICY
AS (
    CURRENT_ROLE() IN ('CEO_ROLE', 'EXECUTIVE_ROLE')
    OR (
        CURRENT_ROLE() = 'MANAGER_ROLE' 
        AND CUSTOMER_ID IN (
            SELECT CUSTOMER_ID 
            FROM CONFIG.USER_ACCESS_PERMISSIONS 
            WHERE USER_ID = CURRENT_USER()
        )
    )
);

-- Employee data access policy
CREATE OR REPLACE ROW ACCESS POLICY EMPLOYEE_DATA_POLICY
AS (
    CURRENT_ROLE() IN ('CEO_ROLE', 'EXECUTIVE_ROLE')
    OR EMPLOYEE_ID = CURRENT_USER()
    OR (
        CURRENT_ROLE() = 'MANAGER_ROLE'
        AND EMPLOYEE_ID IN (
            SELECT REPORTS_TO_EMPLOYEE_ID 
            FROM FOUNDATIONAL_KNOWLEDGE.EMPLOYEES 
            WHERE EMPLOYEE_ID = CURRENT_USER()
        )
    )
);

-- Financial data access policy
CREATE OR REPLACE ROW ACCESS POLICY FINANCIAL_DATA_POLICY
AS (
    CURRENT_ROLE() IN ('CEO_ROLE', 'EXECUTIVE_ROLE', 'FINANCE_ROLE')
);
