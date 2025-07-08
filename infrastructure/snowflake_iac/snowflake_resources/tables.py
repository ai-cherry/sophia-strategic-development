"""Table resource definitions for Sophia AI"""

from pulumi_snowflake import Table, TableColumn


def create_foundational_knowledge_tables(database_name: str, schema_name: str):
    """Create all foundational knowledge tables"""
    tables = {}

    # EMPLOYEES table
    tables["employees"] = Table(
        "employees-table",
        database=database_name,
        schema=schema_name,
        name="EMPLOYEES",
        columns=[
            TableColumn(name="EMPLOYEE_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="FIRST_NAME", type="VARCHAR(255)"),
            TableColumn(name="LAST_NAME", type="VARCHAR(255)"),
            TableColumn(name="EMAIL", type="VARCHAR(255)", nullable=False),
            TableColumn(name="TITLE", type="VARCHAR(255)"),
            TableColumn(name="DEPARTMENT", type="VARCHAR(255)"),
            TableColumn(name="MANAGER_ID", type="VARCHAR(36)"),
            TableColumn(name="EXPERTISE_AREAS", type="ARRAY"),
            TableColumn(name="SLACK_ID", type="VARCHAR(255)"),
            TableColumn(name="GONG_ID", type="VARCHAR(255)"),
            TableColumn(name="HUBSPOT_ID", type="VARCHAR(255)"),
            TableColumn(name="NOTION_PAGE_ID", type="VARCHAR(255)"),
            TableColumn(name="EMBEDDING", type="VECTOR(FLOAT, 768)"),
            TableColumn(
                name="CREATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
            TableColumn(
                name="UPDATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
        ],
        comment="Pay Ready employees with cross-system IDs and expertise",
    )

    # CUSTOMERS table
    tables["customers"] = Table(
        "customers-table",
        database=database_name,
        schema=schema_name,
        name="CUSTOMERS",
        columns=[
            TableColumn(name="CUSTOMER_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="COMPANY_NAME", type="VARCHAR(255)", nullable=False),
            TableColumn(name="INDUSTRY", type="VARCHAR(255)"),
            TableColumn(name="SIZE", type="VARCHAR(50)"),
            TableColumn(name="REVENUE_RANGE", type="VARCHAR(50)"),
            TableColumn(name="KEY_CONTACTS", type="ARRAY"),
            TableColumn(name="PRODUCTS_USED", type="ARRAY"),
            TableColumn(name="ACCOUNT_OWNER_ID", type="VARCHAR(36)"),
            TableColumn(name="HUBSPOT_COMPANY_ID", type="VARCHAR(255)"),
            TableColumn(name="GONG_ACCOUNT_ID", type="VARCHAR(255)"),
            TableColumn(name="NOTION_PAGE_ID", type="VARCHAR(255)"),
            TableColumn(name="EMBEDDING", type="VECTOR(FLOAT, 768)"),
            TableColumn(
                name="CREATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
            TableColumn(
                name="UPDATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
        ],
        comment="Customer companies with product usage and cross-system IDs",
    )

    # COMPETITORS table
    tables["competitors"] = Table(
        "competitors-table",
        database=database_name,
        schema=schema_name,
        name="COMPETITORS",
        columns=[
            TableColumn(name="COMPETITOR_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="COMPANY_NAME", type="VARCHAR(255)", nullable=False),
            TableColumn(name="PRODUCTS", type="ARRAY"),
            TableColumn(name="STRENGTHS", type="ARRAY"),
            TableColumn(name="WEAKNESSES", type="ARRAY"),
            TableColumn(name="MARKET_POSITION", type="VARCHAR(255)"),
            TableColumn(name="PRICING_MODEL", type="VARCHAR(500)"),
            TableColumn(name="TARGET_MARKET", type="VARCHAR(500)"),
            TableColumn(name="NOTION_PAGE_ID", type="VARCHAR(255)"),
            TableColumn(name="EMBEDDING", type="VECTOR(FLOAT, 768)"),
            TableColumn(
                name="CREATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
            TableColumn(
                name="UPDATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
        ],
        comment="Competitor analysis and market intelligence",
    )

    # PRODUCTS table
    tables["products"] = Table(
        "products-table",
        database=database_name,
        schema=schema_name,
        name="PRODUCTS",
        columns=[
            TableColumn(name="PRODUCT_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="PRODUCT_NAME", type="VARCHAR(255)", nullable=False),
            TableColumn(name="CATEGORY", type="VARCHAR(255)"),
            TableColumn(name="FEATURES", type="ARRAY"),
            TableColumn(name="BENEFITS", type="ARRAY"),
            TableColumn(name="TARGET_CUSTOMER", type="VARCHAR(500)"),
            TableColumn(name="PRICING_TIERS", type="VARIANT"),
            TableColumn(name="COMPETITORS", type="ARRAY"),
            TableColumn(name="NOTION_PAGE_ID", type="VARCHAR(255)"),
            TableColumn(name="EMBEDDING", type="VECTOR(FLOAT, 768)"),
            TableColumn(
                name="CREATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
            TableColumn(
                name="UPDATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
        ],
        comment="Pay Ready products and services catalog",
    )

    # COMPANY_DOCUMENTS table
    tables["company_documents"] = Table(
        "company-documents-table",
        database=database_name,
        schema=schema_name,
        name="COMPANY_DOCUMENTS",
        columns=[
            TableColumn(name="DOCUMENT_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="TITLE", type="VARCHAR(500)", nullable=False),
            TableColumn(name="TYPE", type="VARCHAR(100)"),
            TableColumn(name="CATEGORY", type="VARCHAR(255)"),
            TableColumn(name="CONTENT", type="VARCHAR(16777216)"),  # 16MB max
            TableColumn(name="SUMMARY", type="VARCHAR(4000)"),
            TableColumn(name="TAGS", type="ARRAY"),
            TableColumn(name="AUTHOR_ID", type="VARCHAR(36)"),
            TableColumn(name="NOTION_PAGE_ID", type="VARCHAR(255)"),
            TableColumn(name="FILE_URL", type="VARCHAR(1000)"),
            TableColumn(name="EMBEDDING", type="VECTOR(FLOAT, 768)"),
            TableColumn(
                name="CREATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
            TableColumn(
                name="UPDATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
        ],
        comment="Company policies, procedures, and documentation",
    )

    # SALES_MATERIALS table
    tables["sales_materials"] = Table(
        "sales-materials-table",
        database=database_name,
        schema=schema_name,
        name="SALES_MATERIALS",
        columns=[
            TableColumn(name="MATERIAL_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="TITLE", type="VARCHAR(500)", nullable=False),
            TableColumn(name="TYPE", type="VARCHAR(100)"),
            TableColumn(name="PRODUCT_IDS", type="ARRAY"),
            TableColumn(name="TARGET_AUDIENCE", type="VARCHAR(255)"),
            TableColumn(name="KEY_MESSAGES", type="ARRAY"),
            TableColumn(name="CONTENT_URL", type="VARCHAR(1000)"),
            TableColumn(name="NOTION_PAGE_ID", type="VARCHAR(255)"),
            TableColumn(name="EFFECTIVENESS_SCORE", type="NUMBER(3,2)"),
            TableColumn(name="EMBEDDING", type="VECTOR(FLOAT, 768)"),
            TableColumn(
                name="CREATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
            TableColumn(
                name="UPDATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
        ],
        comment="Sales collateral, presentations, and marketing materials",
    )

    # PRICING_MODELS table
    tables["pricing_models"] = Table(
        "pricing-models-table",
        database=database_name,
        schema=schema_name,
        name="PRICING_MODELS",
        columns=[
            TableColumn(name="PRICING_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="PRODUCT_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="TIER_NAME", type="VARCHAR(100)"),
            TableColumn(name="PRICE", type="NUMBER(10,2)"),
            TableColumn(name="BILLING_PERIOD", type="VARCHAR(50)"),
            TableColumn(name="FEATURES", type="ARRAY"),
            TableColumn(name="LIMITS", type="VARIANT"),
            TableColumn(name="DISCOUNT_RULES", type="VARIANT"),
            TableColumn(name="EFFECTIVE_DATE", type="DATE"),
            TableColumn(name="END_DATE", type="DATE"),
            TableColumn(
                name="CREATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
            TableColumn(
                name="UPDATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
        ],
        comment="Product pricing tiers and discount structures",
    )

    # RELATIONSHIPS table (for entity connections)
    tables["relationships"] = Table(
        "relationships-table",
        database=database_name,
        schema=schema_name,
        name="RELATIONSHIPS",
        columns=[
            TableColumn(name="RELATIONSHIP_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="SOURCE_TYPE", type="VARCHAR(50)", nullable=False),
            TableColumn(name="SOURCE_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="TARGET_TYPE", type="VARCHAR(50)", nullable=False),
            TableColumn(name="TARGET_ID", type="VARCHAR(36)", nullable=False),
            TableColumn(name="RELATIONSHIP_TYPE", type="VARCHAR(100)"),
            TableColumn(name="STRENGTH", type="NUMBER(3,2)"),
            TableColumn(name="METADATA", type="VARIANT"),
            TableColumn(
                name="CREATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
            TableColumn(
                name="UPDATED_AT",
                type="TIMESTAMP_LTZ",
                default={"value": "CURRENT_TIMESTAMP()"},
            ),
        ],
        comment="Relationships between entities (employees, customers, products)",
    )

    return tables


def create_existing_tables(database_name: str, schemas: dict):
    """Create tables for existing schemas (Gong, HubSpot, Slack)"""
    tables = {}

    # Example: Gong calls table
    tables["gong_calls"] = Table(
        "gong-calls-table",
        database=database_name,
        schema=schemas["gong"].name,
        name="CALLS",
        columns=[
            TableColumn(name="CALL_ID", type="VARCHAR(255)", nullable=False),
            TableColumn(name="TITLE", type="VARCHAR(1000)"),
            TableColumn(name="PARTICIPANTS", type="ARRAY"),
            TableColumn(name="DURATION_MINUTES", type="NUMBER"),
            TableColumn(name="TRANSCRIPT", type="VARCHAR(16777216)"),
            TableColumn(name="SUMMARY", type="VARCHAR(4000)"),
            TableColumn(name="ACTION_ITEMS", type="ARRAY"),
            TableColumn(name="SENTIMENT_SCORE", type="NUMBER(3,2)"),
            TableColumn(name="CREATED_AT", type="TIMESTAMP_LTZ"),
        ],
        comment="Gong call recordings and analytics",
    )

    return tables
