# AGNO Agent Reference

## Overview
This document provides a comprehensive reference for all Agno agents in the Sophia AI platform, including their capabilities, configuration options, and usage patterns. It is intended as a single source of truth for developers and operators.

---

## Agent Registry

| Agent Name                | Class/Module                                      | Capabilities                                      | Pooled? |
|--------------------------|---------------------------------------------------|---------------------------------------------------|---------|
| Sentry Agent             | `SentryAgent` (`backend/agents/specialized/sentry_agent.py`) | Fetch Sentry issue context, trigger Seer AI fix   | Yes     |
| Call Analysis Agent      | `CallAnalysisAgent` (`backend/agents/specialized/call_analysis_agent.py`) | Analyze Gong calls, extract insights              | Yes     |
| Metrics Agent            | `MetricsAgent` (`backend/agents/specialized/metrics_agent.py`) | Metrics reporting, performance summary            | Yes     |
| Executive Agent          | `ExecutiveAgent` (`backend/agents/specialized/executive_agent.py`) | Strategic intelligence, orchestration             | Yes     |
| Sales Coach Agent        | `SalesCoachAgent` (`backend/agents/specialized/sales_coach_agent.py`) | Sales call coaching, performance insights         | Yes     |
| CRM Sync Agent           | `CRMSyncAgent` (`backend/agents/specialized/crm_sync_agent.py`) | CRM data sync and maintenance                     | Yes     |
| Insight Extraction Agent | `InsightExtractionAgent` (`backend/agents/specialized/insight_extraction_agent.py`) | Proactive insight extraction                      | Yes     |
| Project Intelligence Agent | `ProjectIntelligenceAgent` (`backend/agents/specialized/project_intelligence_agent.py`) | Project analytics and reporting                   | Yes     |
| HR Agent                 | `HRAgent` (`backend/agents/specialized/hr_agent.py`) | Team engagement and org health                    | Yes     |

---

## Capabilities

Each agent exposes a set of capabilities, typically as task types. Example (SentryAgent):

- `fetch_sentry_issue_context`: Fetches full context for a Sentry issue (error details, stack trace, project info).
- `trigger_seer_ai_fix`: Triggers Sentry Seer AI to attempt an automated fix for a given issue.

See the agent class docstrings and `get_capabilities()` methods for details.

---

## Configuration Keys & Defaults

All Agno agents use centralized configuration, typically loaded from Pulumi ESC. Common keys:

| Key                  | Description                                 | Default/Example                |
|----------------------|---------------------------------------------|-------------------------------|
| `AGNO_API_KEY`       | API key for Agno platform                   | Pulumi ESC managed            |
| `AGNO_CONFIG`        | JSON config for Agno agent pool/settings    | `{ "default_model": "claude-sonnet-4-20250514", ... }` |
| `max_concurrent_agents` | Max agents in pool                        | 1000                          |
| `agent_pool_size`    | Number of pooled agents                     | 10                            |
| `cache_ttl`          | Agent/tool cache time-to-live (seconds)     | 3600                          |

---

## Usage Patterns

- **Pooling:** All agents should implement a `pooled` classmethod and register with `AgnoPerformanceOptimizer` for ultra-fast instantiation.
- **Task Handling:** Agents process tasks via the `process_task` method, using async/await and robust error handling.
- **Secret Management:** All secrets/configs are loaded from Pulumi ESC using the Agno secret manager.
- **Logging:** Use structured logging with context for all agent actions and errors.

---

## Logging and Error Handling Best Practices

- Use `logger.info`, `logger.warning`, and `logger.error` for all significant actions, warnings, and errors.
- Always include context in log messages (e.g., agent ID, task type, error details).
- When catching exceptions, use `logger.error(..., exc_info=True)` to include stack traces.
- Avoid silent failures; always log exceptions and return a standardized error response.
- Prefer structured logging (e.g., with `structlog` or context dicts) for machine-readability.
- Example:
  ```python
  try:
      ...
  except Exception as e:
      logger.error(f"Agent {self.agent_id} failed to process task {task.task_type}: {e}", exc_info=True)
      return await create_agent_response(False, error=str(e))
  ```

---

## Adding a New Agno Agent

1. Create the agent class in `backend/agents/specialized/`.
2. Implement a `pooled` classmethod using `AgnoPerformanceOptimizer`.
3. Register capabilities in `get_capabilities()`.
4. Use Pulumi ESC for all secrets/config.
5. Add the agent to this reference file.
6. Add/expand tests in `scripts/test_agno_integration.py` or similar.

---

## See Also
- `config/services/agno_integration.yaml` for config schema
- `backend/integrations/agno_integration.py` for integration logic
- `infrastructure/esc/agno_secrets.py` for secret management
- `scripts/test_agno_integration.py` for integration tests 