"""View resource definitions for Sophia AI"""

from pulumi_snowflake import View


def create_foundational_knowledge_views(database_name: str, schema_name: str):
    """Create analytical views for foundational knowledge"""
    views = {}

    # Employee expertise view
    views["employee_expertise"] = View(
        "employee-expertise-view",
        database=database_name,
        schema=schema_name,
        name="V_EMPLOYEE_EXPERTISE",
        statement=f"""
        SELECT
            e.EMPLOYEE_ID,
            e.FIRST_NAME || ' ' || e.LAST_NAME as FULL_NAME,
            e.TITLE,
            e.DEPARTMENT,
            ea.value::string as EXPERTISE_AREA,
            COUNT(*) OVER (PARTITION BY ea.value::string) as EXPERTS_IN_AREA
        FROM {database_name}.{schema_name}.EMPLOYEES e,
        LATERAL FLATTEN(input => e.EXPERTISE_AREAS) ea
        """,
        comment="View of employee expertise areas for skill matching",
    )

    # Customer product usage view
    views["customer_products"] = View(
        "customer-products-view",
        database=database_name,
        schema=schema_name,
        name="V_CUSTOMER_PRODUCT_USAGE",
        statement=f"""
        SELECT
            c.CUSTOMER_ID,
            c.COMPANY_NAME,
            c.INDUSTRY,
            p.value::string as PRODUCT_ID,
            prod.PRODUCT_NAME,
            prod.CATEGORY
        FROM {database_name}.{schema_name}.CUSTOMERS c,
        LATERAL FLATTEN(input => c.PRODUCTS_USED) p
        LEFT JOIN {database_name}.{schema_name}.PRODUCTS prod
            ON p.value::string = prod.PRODUCT_ID
        """,
        comment="Customer product usage analysis view",
    )

    # Competitive analysis view
    views["competitive_analysis"] = View(
        "competitive-analysis-view",
        database=database_name,
        schema=schema_name,
        name="V_COMPETITIVE_ANALYSIS",
        statement=f"""
        SELECT
            p.PRODUCT_ID,
            p.PRODUCT_NAME,
            p.CATEGORY,
            c.value::string as COMPETITOR_ID,
            comp.COMPANY_NAME as COMPETITOR_NAME,
            comp.STRENGTHS,
            comp.WEAKNESSES,
            comp.PRICING_MODEL
        FROM {database_name}.{schema_name}.PRODUCTS p,
        LATERAL FLATTEN(input => p.COMPETITORS) c
        LEFT JOIN {database_name}.{schema_name}.COMPETITORS comp
            ON c.value::string = comp.COMPETITOR_ID
        """,
        comment="Product competitive analysis view",
    )

    # Entity search view (for unified search)
    views["entity_search"] = View(
        "entity-search-view",
        database=database_name,
        schema=schema_name,
        name="V_ENTITY_SEARCH",
        statement=f"""
        SELECT
            'EMPLOYEE' as ENTITY_TYPE,
            EMPLOYEE_ID as ENTITY_ID,
            FIRST_NAME || ' ' || LAST_NAME as NAME,
            TITLE as DESCRIPTION,
            EMBEDDING
        FROM {database_name}.{schema_name}.EMPLOYEES
        UNION ALL
        SELECT
            'CUSTOMER' as ENTITY_TYPE,
            CUSTOMER_ID as ENTITY_ID,
            COMPANY_NAME as NAME,
            INDUSTRY as DESCRIPTION,
            EMBEDDING
        FROM {database_name}.{schema_name}.CUSTOMERS
        UNION ALL
        SELECT
            'PRODUCT' as ENTITY_TYPE,
            PRODUCT_ID as ENTITY_ID,
            PRODUCT_NAME as NAME,
            CATEGORY as DESCRIPTION,
            EMBEDDING
        FROM {database_name}.{schema_name}.PRODUCTS
        UNION ALL
        SELECT
            'COMPETITOR' as ENTITY_TYPE,
            COMPETITOR_ID as ENTITY_ID,
            COMPANY_NAME as NAME,
            MARKET_POSITION as DESCRIPTION,
            EMBEDDING
        FROM {database_name}.{schema_name}.COMPETITORS
        """,
        comment="Unified entity search view for vector similarity searches",
    )

    return views
