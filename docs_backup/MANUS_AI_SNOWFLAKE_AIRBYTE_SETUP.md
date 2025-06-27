## **Prompt for Manus AI: Production-Hardening Snowflake & Airbyte for the Sophia AI Living Architecture**

**TO**: Manus AI
**FROM**: Sophia AI Core Development
**SUBJECT**: CRITICAL: Production-Hardening Snowflake & Airbyte for New Dynamic AI Ecosystem

### **Executive Directive**

Manus, we have just completed the implementation of the "Living Architecture" framework within the Sophia AI platform. This is a fundamental shift in how our AI understands and interacts with data. The backend is now capable of dynamically adapting to schema changes, automatically generating its own semantic layer, and evolving its understanding of our business.

To fully realize the benefits of this new architecture, it is **absolutely critical** that our underlying data infrastructure in Snowflake and our ingestion pipelines in Airbyte are perfectly aligned with these new capabilities.

Your mission is to **production-harden our Snowflake and Airbyte environments** to support this dynamic, scalable, and self-healing ecosystem. This is not just a cleanup task; it is a strategic alignment to ensure the long-term health and intelligence of the entire Sophia AI platform.

---

### **Pillar 1: Snowflake Foundation Hardening**

This pillar ensures our Snowflake environment is optimized for performance, security, and the dynamic nature of our new semantic layer.

**1.1. Implement Comprehensive Snowflake Tagging for AI Discovery:**

*   **Objective**: Allow the `SchemaDiscoveryService` to automatically identify and classify data sources.
*   **Action**: Apply a comprehensive set of Snowflake tags to all relevant schemas, tables, and columns.
    *   **Tag:** `SOPHIA_AI_METADATA`
    *   **Tag Values (JSON Object)**:
        *   `entity_type`: (e.g., 'customer', 'employee', 'deal', 'call')
        *   `data_source`: (e.g., 'gong', 'hubspot', 'slack', 'netsuite')
        *   `update_frequency`: (e.g., 'hourly', 'daily', 'streaming')
        *   `pii_level`: (e.g., 'none', 'low', 'high', 'sensitive')
        *   `vector_index`: (e.g., 'true' or 'false', to signal what to vectorize)
*   **Example DDL**:
    ```sql
    -- Tagging a table
    ALTER TABLE GONG_DATA.CALLS SET TAG SOPHIA_AI_METADATA = '{"entity_type": "call", "data_source": "gong", "pii_level": "high", "vector_index": "true"}';

    -- Tagging a column
    ALTER TABLE FOUNDATIONAL_KNOWLEDGE.CUSTOMERS MODIFY COLUMN company_name SET TAG SOPHIA_AI_METADATA = '{"is_primary_identifier": "true"}';
    ```
*   **Success Metric**: Every table and critical column in our managed schemas has a `SOPHIA_AI_METADATA` tag.

**1.2. Create Dedicated Schemas for the Living Architecture:**

*   **Objective**: Isolate generated artifacts and operational data to maintain a clean and organized database.
*   **Action**: Create the following schemas if they do not already exist, with appropriate access controls:
    1.  **`SOPHIA_SEMANTIC`**: To house all dynamically generated `..._360` views.
    2.  **`SOPHIA_INSIGHTS`**: To store the output of the `AutomatedInsightsService`.
    3.  **`SOPHIA_ML`**: To hold all trained machine learning models from the `PredictiveAnalyticsService`.
    4.  **`SOPHIA_OPS`**: For operational metadata, such as data quality logs and workflow performance analytics.

**1.3. Implement Zero-Trust, Role-Based Access Control (RBAC):**

*   **Objective**: Ensure the principle of least privilege is strictly enforced.
*   **Action**: Create and assign the following functional roles:
    *   `SOPHIA_AI_APP_ROLE`: Has read-only access to `SOPHIA_SEMANTIC` views and data schemas. This is the primary role for the main application.
    *   `SOPHIA_AI_ETL_ROLE`: Has write access to the raw and staging data schemas (e.g., `GONG_DATA_RAW`). Used by Airbyte.
    *   `SOPHIA_AI_ADMIN_ROLE`: Has elevated privileges to manage schemas, run ML training, and update the semantic layer. Used by our advanced services and for administrative tasks.

---

### **Pillar 2: Airbyte & OpenFlow Pipeline Optimization**

This pillar ensures our data ingestion is robust, observable, and ready for real-time, event-driven processing.

**2.1. Standardize All Airbyte Connections:**

*   **Objective**: Make all ingestion pipelines consistent, predictable, and easy to manage.
*   **Action**: Review and re-configure every Airbyte connection (Gong, HubSpot, Slack, etc.) to meet the following standards:
    *   **Destination Schema**: All data should land in a standardized `_RAW` schema (e.g., `GONG_DATA_RAW`).
    *   **Sync Mode**: Use **Incremental - Append + Deduped** wherever possible to ensure efficient updates.
    *   **Normalization**: Disable Airbyte's basic normalization. All transformations will be handled by our dbt models or Snowflake tasks post-ingestion.
    *   **Scheduling**: Set a standardized, sensible default schedule (e.g., hourly) for all sources.

**2.2. Implement Comprehensive Data Quality Monitoring:**

*   **Objective**: Ensure "bad memory" never enters the system.
*   **Action**: Integrate a data quality tool (like dbt tests, Great Expectations, or Monte Carlo) into the post-sync workflow for every Airbyte connection.
    *   **Create Tests**: For each critical source, implement at least three data quality tests (e.g., `not_null`, `unique`, `accepted_values`).
    *   **Automate**: These tests should run automatically after every successful Airbyte sync.
    *   **Alerting**: If a data quality test fails, it must trigger an immediate alert (e.g., via Slack or PagerDuty) and **prevent the data from being promoted** from the `_RAW` schema to the staging/production schemas.

**2.3. Prepare for Snowflake OpenFlow:**

*   **Objective**: Position us to immediately leverage real-time, event-driven ingestion when it becomes available.
*   **Action**:
    *   Ensure all Airbyte connectors are updated to the latest versions that will support OpenFlow.
    *   Design our dbt models and Snowflake tasks to be idempotent and capable of handling micro-batches, which is how OpenFlow will deliver data.
    *   In the interim, configure Airbyte webhooks to trigger our transformation jobs on sync completion, simulating an event-driven workflow.

---

### **Final Success Metrics**

Upon completion of this work, our data infrastructure will be:

*   **Dynamically Aware**: Snowflake will be tagged and structured so our AI can automatically discover and classify new data.
*   **Robust & Secure**: With fine-grained RBAC and automated data quality gates.
*   **Future-Proofed**: Ready for real-time streaming with OpenFlow and easily extensible to new data sources.
*   **Perfectly Aligned**: The infrastructure will be an enabling foundation for our new "Living Architecture," not a bottleneck.

Please treat this as a **top-priority directive**. The successful implementation of these enhancements is critical to the long-term success of the Sophia AI platform. 