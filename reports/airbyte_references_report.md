# Airbyte References Report

Total files with Airbyte references: 13


## /Users/lynnmusil/sophia-main/ESTUARY_FLOW_INTEGRATION_PLAN.md

- Line 5: `Airbyte`
  ```
  Estuary Flow will replace Airbyte as our primary data ingestion layer, providing real-time CDC capabilities, better scalability, and unified data pipeline management. This integration enhances our V2 MCP server architecture with enterprise-grade data streaming.
  ```
- Line 64: `Airbyte`
  ```
  - Replace complex Airbyte configurations
  ```
- Line 255: `Airbyte`
  ```
  - Keep Airbyte running
  ```
- Line 264: `Airbyte`
  ```
  ### 3. **Airbyte Decommission (Week 3)**
  ```
- Line 265: `Airbyte`
  ```
  - Remove Airbyte configurations
  ```
- Line 277: `Airbyte`
  ```
  | Cost Reduction | 30% vs Airbyte | AWS billing |
  ```
- Line 300: `Airbyte`
  ```
  - [ ] Decommission Airbyte
  ```
- Line 5: `Airbyte`
  ```
  Estuary Flow will replace Airbyte as our primary data ingestion layer, providing real-time CDC capabilities, better scalability, and unified data pipeline management. This integration enhances our V2 MCP server architecture with enterprise-grade data streaming.
  ```
- Line 64: `Airbyte`
  ```
  - Replace complex Airbyte configurations
  ```
- Line 255: `Airbyte`
  ```
  - Keep Airbyte running
  ```
- Line 264: `Airbyte`
  ```
  ### 3. **Airbyte Decommission (Week 3)**
  ```
- Line 265: `Airbyte`
  ```
  - Remove Airbyte configurations
  ```
- Line 277: `Airbyte`
  ```
  | Cost Reduction | 30% vs Airbyte | AWS billing |
  ```
- Line 300: `Airbyte`
  ```
  - [ ] Decommission Airbyte
  ```
- Line 5: `Airbyte`
  ```
  Estuary Flow will replace Airbyte as our primary data ingestion layer, providing real-time CDC capabilities, better scalability, and unified data pipeline management. This integration enhances our V2 MCP server architecture with enterprise-grade data streaming.
  ```
- Line 64: `Airbyte`
  ```
  - Replace complex Airbyte configurations
  ```
- Line 255: `Airbyte`
  ```
  - Keep Airbyte running
  ```
- Line 264: `Airbyte`
  ```
  ### 3. **Airbyte Decommission (Week 3)**
  ```
- Line 265: `Airbyte`
  ```
  - Remove Airbyte configurations
  ```
- Line 277: `Airbyte`
  ```
  | Cost Reduction | 30% vs Airbyte | AWS billing |
  ```
- Line 300: `Airbyte`
  ```
  - [ ] Decommission Airbyte
  ```

## /Users/lynnmusil/sophia-main/ESTUARY_FLOW_V2_SUMMARY.md

- Line 7: `Airbyte`
  ```
  - Designed to replace Airbyte with superior real-time capabilities
  ```
- Line 130: `Airbyte`
  ```
  - 30% reduction vs Airbyte
  ```
- Line 7: `Airbyte`
  ```
  - Designed to replace Airbyte with superior real-time capabilities
  ```
- Line 130: `Airbyte`
  ```
  - 30% reduction vs Airbyte
  ```
- Line 7: `Airbyte`
  ```
  - Designed to replace Airbyte with superior real-time capabilities
  ```
- Line 130: `Airbyte`
  ```
  - 30% reduction vs Airbyte
  ```

## /Users/lynnmusil/sophia-main/SOPHIA_SNOWFLAKE_NATURAL_LANGUAGE_FLOW.md

- Line 209: `STG_TRANSFORMED`
  ```
  SELECT * FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```

## /Users/lynnmusil/sophia-main/codebase_audit_report.json

- Line 6619: `STG_TRANSFORMED`
  ```
  "STG_TRANSFORMED",
  ```

## /Users/lynnmusil/sophia-main/core/sql_security_validator.py

- Line 42: `STG_TRANSFORMED`
  ```
  "STG_TRANSFORMED",
  ```

## /Users/lynnmusil/sophia-main/core/use_cases/asana_project_intelligence_agent.py

- Line 144: `STG_TRANSFORMED`
  ```
  query = f"\n            WITH project_task_summary AS (\n                SELECT\n                    p.PROJECT_GID,\n                    COUNT(t.TASK_GID) as total_tasks,\n                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,\n                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    AVG(CASE WHEN t.AI_URGENCY_SCORE IS NOT NULL THEN t.AI_URGENCY_SCORE ELSE 0.5 END) as avg_urgency\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                GROUP BY p.PROJECT_GID\n            )\n            SELECT\n                p.PROJECT_GID,\n                p.PROJECT_NAME,\n                p.COMPLETION_PERCENTAGE,\n                p.TEAM_NAME,\n                p.OWNER_NAME,\n                p.DUE_DATE,\n                p.CREATED_AT,\n                p.MODIFIED_AT,\n                p.AI_HEALTH_SCORE,\n                p.AI_RISK_ASSESSMENT,\n                pts.total_tasks,\n                pts.completed_tasks,\n                pts.overdue_tasks,\n                pts.avg_urgency,\n                p.AI_MEMORY_METADATA\n            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n            LEFT JOIN project_task_summary pts ON p.PROJECT_GID = pts.PROJECT_GID\n            {where_clause}\n            ORDER BY p.MODIFIED_AT DESC\n            "
  ```
- Line 144: `STG_TRANSFORMED`
  ```
  query = f"\n            WITH project_task_summary AS (\n                SELECT\n                    p.PROJECT_GID,\n                    COUNT(t.TASK_GID) as total_tasks,\n                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,\n                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    AVG(CASE WHEN t.AI_URGENCY_SCORE IS NOT NULL THEN t.AI_URGENCY_SCORE ELSE 0.5 END) as avg_urgency\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                GROUP BY p.PROJECT_GID\n            )\n            SELECT\n                p.PROJECT_GID,\n                p.PROJECT_NAME,\n                p.COMPLETION_PERCENTAGE,\n                p.TEAM_NAME,\n                p.OWNER_NAME,\n                p.DUE_DATE,\n                p.CREATED_AT,\n                p.MODIFIED_AT,\n                p.AI_HEALTH_SCORE,\n                p.AI_RISK_ASSESSMENT,\n                pts.total_tasks,\n                pts.completed_tasks,\n                pts.overdue_tasks,\n                pts.avg_urgency,\n                p.AI_MEMORY_METADATA\n            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n            LEFT JOIN project_task_summary pts ON p.PROJECT_GID = pts.PROJECT_GID\n            {where_clause}\n            ORDER BY p.MODIFIED_AT DESC\n            "
  ```
- Line 144: `STG_TRANSFORMED`
  ```
  query = f"\n            WITH project_task_summary AS (\n                SELECT\n                    p.PROJECT_GID,\n                    COUNT(t.TASK_GID) as total_tasks,\n                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,\n                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    AVG(CASE WHEN t.AI_URGENCY_SCORE IS NOT NULL THEN t.AI_URGENCY_SCORE ELSE 0.5 END) as avg_urgency\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                GROUP BY p.PROJECT_GID\n            )\n            SELECT\n                p.PROJECT_GID,\n                p.PROJECT_NAME,\n                p.COMPLETION_PERCENTAGE,\n                p.TEAM_NAME,\n                p.OWNER_NAME,\n                p.DUE_DATE,\n                p.CREATED_AT,\n                p.MODIFIED_AT,\n                p.AI_HEALTH_SCORE,\n                p.AI_RISK_ASSESSMENT,\n                pts.total_tasks,\n                pts.completed_tasks,\n                pts.overdue_tasks,\n                pts.avg_urgency,\n                p.AI_MEMORY_METADATA\n            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n            LEFT JOIN project_task_summary pts ON p.PROJECT_GID = pts.PROJECT_GID\n            {where_clause}\n            ORDER BY p.MODIFIED_AT DESC\n            "
  ```
- Line 248: `STG_TRANSFORMED`
  ```
  query = f"\n            WITH team_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(DISTINCT p.PROJECT_GID) as total_projects,\n                    COUNT(DISTINCT CASE WHEN p.IS_ARCHIVED = FALSE THEN p.PROJECT_GID END) as active_projects,\n                    COUNT(DISTINCT CASE WHEN p.COMPLETION_PERCENTAGE = 100 THEN p.PROJECT_GID END) as completed_projects,\n                    AVG(p.COMPLETION_PERCENTAGE) as avg_completion_rate,\n                    COUNT(DISTINCT u.USER_GID) as member_count\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_USERS u ON p.TEAM_NAME = u.DEPARTMENT\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            ),\n            task_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(t.TASK_GID) as total_tasks,\n                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,\n                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    COUNT(CASE WHEN t.COMPLETED_AT >= CURRENT_DATE - 30 THEN 1 END) as tasks_completed_last_30d\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            )\n            SELECT\n                tm.TEAM_NAME,\n                tm.total_projects,\n                tm.active_projects,\n                tm.completed_projects,\n                tm.avg_completion_rate,\n                tm.member_count,\n                COALESCE(tkm.total_tasks, 0) as total_tasks,\n                COALESCE(tkm.overdue_tasks, 0) as overdue_tasks,\n                COALESCE(tkm.tasks_completed_last_30d, 0) as recent_completions\n            FROM team_metrics tm\n            LEFT JOIN task_metrics tkm ON tm.TEAM_NAME = tkm.TEAM_NAME\n            WHERE tm.TEAM_NAME IS NOT NULL\n            ORDER BY tm.avg_completion_rate DESC\n            "
  ```
- Line 248: `STG_TRANSFORMED`
  ```
  query = f"\n            WITH team_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(DISTINCT p.PROJECT_GID) as total_projects,\n                    COUNT(DISTINCT CASE WHEN p.IS_ARCHIVED = FALSE THEN p.PROJECT_GID END) as active_projects,\n                    COUNT(DISTINCT CASE WHEN p.COMPLETION_PERCENTAGE = 100 THEN p.PROJECT_GID END) as completed_projects,\n                    AVG(p.COMPLETION_PERCENTAGE) as avg_completion_rate,\n                    COUNT(DISTINCT u.USER_GID) as member_count\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_USERS u ON p.TEAM_NAME = u.DEPARTMENT\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            ),\n            task_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(t.TASK_GID) as total_tasks,\n                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,\n                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    COUNT(CASE WHEN t.COMPLETED_AT >= CURRENT_DATE - 30 THEN 1 END) as tasks_completed_last_30d\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            )\n            SELECT\n                tm.TEAM_NAME,\n                tm.total_projects,\n                tm.active_projects,\n                tm.completed_projects,\n                tm.avg_completion_rate,\n                tm.member_count,\n                COALESCE(tkm.total_tasks, 0) as total_tasks,\n                COALESCE(tkm.overdue_tasks, 0) as overdue_tasks,\n                COALESCE(tkm.tasks_completed_last_30d, 0) as recent_completions\n            FROM team_metrics tm\n            LEFT JOIN task_metrics tkm ON tm.TEAM_NAME = tkm.TEAM_NAME\n            WHERE tm.TEAM_NAME IS NOT NULL\n            ORDER BY tm.avg_completion_rate DESC\n            "
  ```
- Line 248: `STG_TRANSFORMED`
  ```
  query = f"\n            WITH team_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(DISTINCT p.PROJECT_GID) as total_projects,\n                    COUNT(DISTINCT CASE WHEN p.IS_ARCHIVED = FALSE THEN p.PROJECT_GID END) as active_projects,\n                    COUNT(DISTINCT CASE WHEN p.COMPLETION_PERCENTAGE = 100 THEN p.PROJECT_GID END) as completed_projects,\n                    AVG(p.COMPLETION_PERCENTAGE) as avg_completion_rate,\n                    COUNT(DISTINCT u.USER_GID) as member_count\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_USERS u ON p.TEAM_NAME = u.DEPARTMENT\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            ),\n            task_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(t.TASK_GID) as total_tasks,\n                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,\n                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    COUNT(CASE WHEN t.COMPLETED_AT >= CURRENT_DATE - 30 THEN 1 END) as tasks_completed_last_30d\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            )\n            SELECT\n                tm.TEAM_NAME,\n                tm.total_projects,\n                tm.active_projects,\n                tm.completed_projects,\n                tm.avg_completion_rate,\n                tm.member_count,\n                COALESCE(tkm.total_tasks, 0) as total_tasks,\n                COALESCE(tkm.overdue_tasks, 0) as overdue_tasks,\n                COALESCE(tkm.tasks_completed_last_30d, 0) as recent_completions\n            FROM team_metrics tm\n            LEFT JOIN task_metrics tkm ON tm.TEAM_NAME = tkm.TEAM_NAME\n            WHERE tm.TEAM_NAME IS NOT NULL\n            ORDER BY tm.avg_completion_rate DESC\n            "
  ```
- Line 248: `STG_TRANSFORMED`
  ```
  query = f"\n            WITH team_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(DISTINCT p.PROJECT_GID) as total_projects,\n                    COUNT(DISTINCT CASE WHEN p.IS_ARCHIVED = FALSE THEN p.PROJECT_GID END) as active_projects,\n                    COUNT(DISTINCT CASE WHEN p.COMPLETION_PERCENTAGE = 100 THEN p.PROJECT_GID END) as completed_projects,\n                    AVG(p.COMPLETION_PERCENTAGE) as avg_completion_rate,\n                    COUNT(DISTINCT u.USER_GID) as member_count\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_USERS u ON p.TEAM_NAME = u.DEPARTMENT\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            ),\n            task_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(t.TASK_GID) as total_tasks,\n                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,\n                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    COUNT(CASE WHEN t.COMPLETED_AT >= CURRENT_DATE - 30 THEN 1 END) as tasks_completed_last_30d\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            )\n            SELECT\n                tm.TEAM_NAME,\n                tm.total_projects,\n                tm.active_projects,\n                tm.completed_projects,\n                tm.avg_completion_rate,\n                tm.member_count,\n                COALESCE(tkm.total_tasks, 0) as total_tasks,\n                COALESCE(tkm.overdue_tasks, 0) as overdue_tasks,\n                COALESCE(tkm.tasks_completed_last_30d, 0) as recent_completions\n            FROM team_metrics tm\n            LEFT JOIN task_metrics tkm ON tm.TEAM_NAME = tkm.TEAM_NAME\n            WHERE tm.TEAM_NAME IS NOT NULL\n            ORDER BY tm.avg_completion_rate DESC\n            "
  ```
- Line 248: `STG_TRANSFORMED`
  ```
  query = f"\n            WITH team_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(DISTINCT p.PROJECT_GID) as total_projects,\n                    COUNT(DISTINCT CASE WHEN p.IS_ARCHIVED = FALSE THEN p.PROJECT_GID END) as active_projects,\n                    COUNT(DISTINCT CASE WHEN p.COMPLETION_PERCENTAGE = 100 THEN p.PROJECT_GID END) as completed_projects,\n                    AVG(p.COMPLETION_PERCENTAGE) as avg_completion_rate,\n                    COUNT(DISTINCT u.USER_GID) as member_count\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_USERS u ON p.TEAM_NAME = u.DEPARTMENT\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            ),\n            task_metrics AS (\n                SELECT\n                    p.TEAM_NAME,\n                    COUNT(t.TASK_GID) as total_tasks,\n                    COUNT(CASE WHEN t.IS_COMPLETED = TRUE THEN 1 END) as completed_tasks,\n                    COUNT(CASE WHEN t.TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    COUNT(CASE WHEN t.COMPLETED_AT >= CURRENT_DATE - 30 THEN 1 END) as tasks_completed_last_30d\n                FROM STG_TRANSFORMED.STG_ASANA_PROJECTS p\n                LEFT JOIN STG_TRANSFORMED.STG_ASANA_TASKS t ON p.PROJECT_GID = t.PROJECT_GID\n                {where_clause}\n                GROUP BY p.TEAM_NAME\n            )\n            SELECT\n                tm.TEAM_NAME,\n                tm.total_projects,\n                tm.active_projects,\n                tm.completed_projects,\n                tm.avg_completion_rate,\n                tm.member_count,\n                COALESCE(tkm.total_tasks, 0) as total_tasks,\n                COALESCE(tkm.overdue_tasks, 0) as overdue_tasks,\n                COALESCE(tkm.tasks_completed_last_30d, 0) as recent_completions\n            FROM team_metrics tm\n            LEFT JOIN task_metrics tkm ON tm.TEAM_NAME = tkm.TEAM_NAME\n            WHERE tm.TEAM_NAME IS NOT NULL\n            ORDER BY tm.avg_completion_rate DESC\n            "
  ```
- Line 310: `STG_TRANSFORMED`
  ```
  task_query = f"\n                SELECT\n                    COUNT(*) as total_tasks,\n                    COUNT(CASE WHEN TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks,\n                    COUNT(CASE WHEN ASSIGNEE_GID IS NULL THEN 1 END) as unassigned_tasks,\n                    COUNT(CASE WHEN DEPENDENCY_COUNT > 0 THEN 1 END) as dependent_tasks,\n                    AVG(AI_URGENCY_SCORE) as avg_urgency,\n                    COUNT(CASE WHEN ESTIMATED_HOURS IS NULL THEN 1 END) as unestimated_tasks\n                FROM STG_TRANSFORMED.STG_ASANA_TASKS\n                WHERE PROJECT_GID = '{project.project_gid}'\n                "
  ```

## /Users/lynnmusil/sophia-main/docs/implementation/MCP_V2_MIGRATION_STATUS.md

- Line 40: `airbyte`
  ```
  - `airbyte` → `airbyte_v2` (port 9035)
  ```
- Line 40: `airbyte`
  ```
  - `airbyte` → `airbyte_v2` (port 9035)
  ```
- Line 40: `airbyte`
  ```
  - `airbyte` → `airbyte_v2` (port 9035)
  ```

## /Users/lynnmusil/sophia-main/estuary_migration_complete_report.json

- Line 19: `airbyte`
  ```
  ".venv/lib/python3.12/site-packages/langchain_community/document_loaders/airbyte.py",
  ```
- Line 19: `airbyte`
  ```
  ".venv/lib/python3.12/site-packages/langchain_community/document_loaders/airbyte.py",
  ```
- Line 19: `airbyte`
  ```
  ".venv/lib/python3.12/site-packages/langchain_community/document_loaders/airbyte.py",
  ```

## /Users/lynnmusil/sophia-main/infrastructure/services/enhanced_cortex_agent_service.py

- Line 503: `STG_TRANSFORMED`
  ```
  FROM SOPHIA_AI_ADVANCED.STG_TRANSFORMED.CUSTOMER_INTELLIGENCE_ADVANCED
  ```
- Line 576: `STG_TRANSFORMED`
  ```
  FROM SOPHIA_AI_ADVANCED.STG_TRANSFORMED.SALES_OPPORTUNITY_INTELLIGENCE
  ```
- Line 689: `STG_TRANSFORMED`
  ```
  FROM SOPHIA_AI_ADVANCED.STG_TRANSFORMED.COMMUNICATION_INTELLIGENCE_REALTIME
  ```

## /Users/lynnmusil/sophia-main/infrastructure/snowflake_setup/sample_developer_queries.md

- Line 37: `STG_TRANSFORMED`
  ```
  SHOW TABLES IN SCHEMA STG_TRANSFORMED;
  ```
- Line 43: `STG_TRANSFORMED`
  ```
  DESCRIBE TABLE STG_TRANSFORMED.STG_GONG_CALLS;
  ```
- Line 44: `STG_TRANSFORMED`
  ```
  DESCRIBE TABLE STG_TRANSFORMED.STG_HUBSPOT_DEALS;
  ```
- Line 56: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```
- Line 65: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
  ```
- Line 74: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS;
  ```
- Line 93: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
  ```
- Line 110: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
  ```
- Line 134: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS hd
  ```
- Line 163: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```
- Line 187: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```
- Line 215: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS t
  ```
- Line 216: `STG_TRANSFORMED`
  ```
  JOIN STG_TRANSFORMED.STG_GONG_CALLS c ON t.CALL_ID = c.CALL_ID
  ```
- Line 230: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
  ```
- Line 241: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS hd
  ```
- Line 265: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS t
  ```
- Line 266: `STG_TRANSFORMED`
  ```
  JOIN STG_TRANSFORMED.STG_GONG_CALLS c ON t.CALL_ID = c.CALL_ID
  ```
- Line 303: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
  ```
- Line 326: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```
- Line 352: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
  ```
- Line 482: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS hd
  ```
- Line 483: `STG_TRANSFORMED`
  ```
  LEFT JOIN STG_TRANSFORMED.STG_GONG_CALLS gc ON hd.DEAL_ID = gc.HUBSPOT_DEAL_ID
  ```
- Line 591: `STG_TRANSFORMED`
  ```
  WHERE TABLE_SCHEMA = 'STG_TRANSFORMED'
  ```
- Line 606: `STG_TRANSFORMED`
  ```
  WHERE TABLE_SCHEMA IN ('STG_TRANSFORMED', 'AI_MEMORY')
  ```
- Line 629: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_HUBSPOT_DEALS
  ```
- Line 638: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS
  ```
- Line 679: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS gc
  ```
- Line 703: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS gt
  ```
- Line 705: `STG_TRANSFORMED`
  ```
  JOIN STG_TRANSFORMED.STG_GONG_CALLS gc ON gt.CALL_ID = gc.CALL_ID
  ```
- Line 742: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS gc
  ```
- Line 761: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS gc,
  ```
- Line 833: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS gc
  ```
- Line 913: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS gc
  ```
- Line 998: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS gc
  ```
- Line 1065: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```
- Line 1085: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```
- Line 1095: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```
- Line 1134: `STG_TRANSFORMED`
  ```
  'STG_TRANSFORMED.STG_GONG_CALLS' as table_name,
  ```
- Line 1141: `STG_TRANSFORMED`
  ```
  FROM STG_TRANSFORMED.STG_GONG_CALLS
  ```

## /Users/lynnmusil/sophia-main/scripts/backend/sophia_data_pipeline_ultimate.py

- Line 11: `STG_TRANSFORMED`
  ```
  - Comprehensive transformation to STG_TRANSFORMED tables
  ```
- Line 319: `STG_TRANSFORMED`
  ```
  "STG_TRANSFORMED",  # Structured staging tables
  ```
- Line 467: `STG_TRANSFORMED`
  ```
  """Execute transformation procedures to populate STG_TRANSFORMED tables"""
  ```
- Line 478: `STG_TRANSFORMED`
  ```
  cursor.execute("CALL STG_TRANSFORMED.TRANSFORM_RAW_GONG_CALLS()")
  ```
- Line 484: `STG_TRANSFORMED`
  ```
  cursor.execute("CALL STG_TRANSFORMED.TRANSFORM_RAW_GONG_TRANSCRIPTS()")
  ```
- Line 517: `STG_TRANSFORMED`
  ```
  cursor.execute("CALL STG_TRANSFORMED.ENRICH_GONG_CALLS_WITH_AI()")
  ```

## /Users/lynnmusil/sophia-main/scripts/cleanup_outdated_models.py

- Line 158: `Airbyte`
  ```
  """Check for Airbyte references that should be Estuary"""
  ```
- Line 206: `Airbyte`
  ```
  print("🔍 Scanning for Airbyte references...")
  ```
- Line 218: `Airbyte`
  ```
  # Generate Airbyte report
  ```
- Line 220: `Airbyte`
  ```
  airbyte_report = ["# Airbyte References Report\n"]
  ```
- Line 221: `Airbyte`
  ```
  airbyte_report.append(f"Total files with Airbyte references: {len(airbyte_findings)}\n")
  ```
- Line 231: `Airbyte`
  ```
  print(f"✅ Airbyte report saved to: {airbyte_report_path}")
  ```
- Line 236: `Airbyte`
  ```
  print(f"- Files with Airbyte references: {len(airbyte_findings)}")
  ```
- Line 242: `Airbyte`
  ```
  print(f"- Total Airbyte references: {total_airbyte}")
  ```
- Line 158: `Airbyte`
  ```
  """Check for Airbyte references that should be Estuary"""
  ```
- Line 206: `Airbyte`
  ```
  print("🔍 Scanning for Airbyte references...")
  ```
- Line 218: `Airbyte`
  ```
  # Generate Airbyte report
  ```
- Line 220: `Airbyte`
  ```
  airbyte_report = ["# Airbyte References Report\n"]
  ```
- Line 221: `Airbyte`
  ```
  airbyte_report.append(f"Total files with Airbyte references: {len(airbyte_findings)}\n")
  ```
- Line 231: `Airbyte`
  ```
  print(f"✅ Airbyte report saved to: {airbyte_report_path}")
  ```
- Line 236: `Airbyte`
  ```
  print(f"- Files with Airbyte references: {len(airbyte_findings)}")
  ```
- Line 242: `Airbyte`
  ```
  print(f"- Total Airbyte references: {total_airbyte}")
  ```
- Line 158: `Airbyte`
  ```
  """Check for Airbyte references that should be Estuary"""
  ```
- Line 206: `Airbyte`
  ```
  print("🔍 Scanning for Airbyte references...")
  ```
- Line 218: `Airbyte`
  ```
  # Generate Airbyte report
  ```
- Line 220: `Airbyte`
  ```
  airbyte_report = ["# Airbyte References Report\n"]
  ```
- Line 221: `Airbyte`
  ```
  airbyte_report.append(f"Total files with Airbyte references: {len(airbyte_findings)}\n")
  ```
- Line 231: `Airbyte`
  ```
  print(f"✅ Airbyte report saved to: {airbyte_report_path}")
  ```
- Line 236: `Airbyte`
  ```
  print(f"- Files with Airbyte references: {len(airbyte_findings)}")
  ```
- Line 242: `Airbyte`
  ```
  print(f"- Total Airbyte references: {total_airbyte}")
  ```
- Line 165: `RAW_ESTUARY`
  ```
  r'RAW_ESTUARY',
  ```
- Line 166: `STG_TRANSFORMED`
  ```
  r'STG_TRANSFORMED',
  ```

## /Users/lynnmusil/sophia-main/scripts/migration/mcp_v2_migration_orchestrator.py

- Line 237: `airbyte`
  ```
  "airbyte",
  ```
- Line 238: `airbyte`
  ```
  "mcp-servers/airbyte",
  ```
- Line 237: `airbyte`
  ```
  "airbyte",
  ```
- Line 238: `airbyte`
  ```
  "mcp-servers/airbyte",
  ```
- Line 237: `airbyte`
  ```
  "airbyte",
  ```
- Line 238: `airbyte`
  ```
  "mcp-servers/airbyte",
  ```
