"""Tasks and streams resource definitions for Sophia AI"""

from pulumi_snowflake import Stream, Task


def create_embedding_tasks(database_name: str, schema_name: str, warehouse_name: str):
    """Create tasks for automatic embedding generation"""
    tasks = {}

    # Create streams first
    employee_stream = Stream(
        "employee-stream",
        database=database_name,
        schema=schema_name,
        name="EMPLOYEES_STREAM",
        on_table=f"{database_name}.{schema_name}.EMPLOYEES",
        comment="Stream to track changes in EMPLOYEES table",
    )

    customer_stream = Stream(
        "customer-stream",
        database=database_name,
        schema=schema_name,
        name="CUSTOMERS_STREAM",
        on_table=f"{database_name}.{schema_name}.CUSTOMERS",
        comment="Stream to track changes in CUSTOMERS table",
    )

    product_stream = Stream(
        "product-stream",
        database=database_name,
        schema=schema_name,
        name="PRODUCTS_STREAM",
        on_table=f"{database_name}.{schema_name}.PRODUCTS",
        comment="Stream to track changes in PRODUCTS table",
    )

    # Employee embedding task
    tasks["employee_embeddings"] = Task(
        "employee-embedding-task",
        database=database_name,
        schema=schema_name,
        name="GENERATE_EMPLOYEE_EMBEDDINGS",
        warehouse=warehouse_name,
        schedule="USING CRON 0 */6 * * * UTC",  # Every 6 hours
        comment="Generate embeddings for new/updated employees",
        sql_statement=f"""
        MERGE INTO {database_name}.{schema_name}.EMPLOYEES target
        USING (
            SELECT
                EMPLOYEE_ID,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                    'e5-base-v2',
                    CONCAT_WS(' ',
                        FIRST_NAME,
                        LAST_NAME,
                        TITLE,
                        DEPARTMENT,
                        ARRAY_TO_STRING(EXPERTISE_AREAS, ', ')
                    )
                ) as NEW_EMBEDDING
            FROM {database_name}.{schema_name}.EMPLOYEES_STREAM
            WHERE METADATA$ACTION IN ('INSERT', 'UPDATE')
        ) source
        ON target.EMPLOYEE_ID = source.EMPLOYEE_ID
        WHEN MATCHED THEN
            UPDATE SET
                target.EMBEDDING = source.NEW_EMBEDDING,
                target.UPDATED_AT = CURRENT_TIMESTAMP();
        """,
        enabled=True,
    )

    # Customer embedding task
    tasks["customer_embeddings"] = Task(
        "customer-embedding-task",
        database=database_name,
        schema=schema_name,
        name="GENERATE_CUSTOMER_EMBEDDINGS",
        warehouse=warehouse_name,
        schedule="USING CRON 0 */6 * * * UTC",  # Every 6 hours
        comment="Generate embeddings for new/updated customers",
        sql_statement=f"""
        MERGE INTO {database_name}.{schema_name}.CUSTOMERS target
        USING (
            SELECT
                CUSTOMER_ID,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                    'e5-base-v2',
                    CONCAT_WS(' ',
                        COMPANY_NAME,
                        INDUSTRY,
                        SIZE,
                        ARRAY_TO_STRING(PRODUCTS_USED, ', ')
                    )
                ) as NEW_EMBEDDING
            FROM {database_name}.{schema_name}.CUSTOMERS_STREAM
            WHERE METADATA$ACTION IN ('INSERT', 'UPDATE')
        ) source
        ON target.CUSTOMER_ID = source.CUSTOMER_ID
        WHEN MATCHED THEN
            UPDATE SET
                target.EMBEDDING = source.NEW_EMBEDDING,
                target.UPDATED_AT = CURRENT_TIMESTAMP();
        """,
        enabled=True,
    )

    # Product embedding task
    tasks["product_embeddings"] = Task(
        "product-embedding-task",
        database=database_name,
        schema=schema_name,
        name="GENERATE_PRODUCT_EMBEDDINGS",
        warehouse=warehouse_name,
        schedule="USING CRON 0 */12 * * * UTC",  # Every 12 hours
        comment="Generate embeddings for new/updated products",
        sql_statement=f"""
        MERGE INTO {database_name}.{schema_name}.PRODUCTS target
        USING (
            SELECT
                PRODUCT_ID,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                    'e5-base-v2',
                    CONCAT_WS(' ',
                        PRODUCT_NAME,
                        CATEGORY,
                        ARRAY_TO_STRING(FEATURES, ', '),
                        ARRAY_TO_STRING(BENEFITS, ', '),
                        TARGET_CUSTOMER
                    )
                ) as NEW_EMBEDDING
            FROM {database_name}.{schema_name}.PRODUCTS_STREAM
            WHERE METADATA$ACTION IN ('INSERT', 'UPDATE')
        ) source
        ON target.PRODUCT_ID = source.PRODUCT_ID
        WHEN MATCHED THEN
            UPDATE SET
                target.EMBEDDING = source.NEW_EMBEDDING,
                target.UPDATED_AT = CURRENT_TIMESTAMP();
        """,
        enabled=True,
    )

    # Document embedding task
    tasks["document_embeddings"] = Task(
        "document-embedding-task",
        database=database_name,
        schema=schema_name,
        name="GENERATE_DOCUMENT_EMBEDDINGS",
        warehouse=warehouse_name,
        schedule="USING CRON 0 */4 * * * UTC",  # Every 4 hours
        comment="Generate embeddings for company documents",
        sql_statement=f"""
        UPDATE {database_name}.{schema_name}.COMPANY_DOCUMENTS
        SET
            EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                'e5-base-v2',
                CONCAT_WS(' ', TITLE, SUMMARY, ARRAY_TO_STRING(TAGS, ', '))
            ),
            UPDATED_AT = CURRENT_TIMESTAMP()
        WHERE EMBEDDING IS NULL
           OR UPDATED_AT < DATEADD(day, -7, CURRENT_TIMESTAMP());
        """,
        enabled=True,
    )

    return tasks
