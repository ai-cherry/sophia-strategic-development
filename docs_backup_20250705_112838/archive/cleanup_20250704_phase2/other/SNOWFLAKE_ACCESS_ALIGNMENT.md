# Snowflake Access & IaC Alignment Review

## Overview

This document reviews all code paths invoking Snowflake connections and verifies alignment with Pulumi ESC configuration. It identifies hardcoded credentials or misaligned implementations and prescribes remediation steps.

---

## 1. Configuration Source

**Expected pattern**:
All Snowflake connections must use the centralized `get_snowflake_config()` from `backend/core/auto_esc_config.py`, which reads secrets from Pulumi ESC (GitHub Organization Secrets → Pulumi ESC).

---

## 2. Identified Access Points

| File                                                                           | Issue                                                                                   | Location                                                                               |
|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| `backend/services/unified_ai_orchestration_service.py`                         | Hardcoded `account` and `user` values; bypasses ESC config                              | `snowflake.connector.connect(account="ZNB04675.us-east-1", user="SCOOBYJAVA15", …)`    |
| `backend/services/snowflake_cortex_aisql.py`                                    | Uses `get_snowflake_config()` correctly                                                   | **OK**                                                                                 |
| `backend/utils/snowflake_cortex_service.py`                                     | Uses `get_snowflake_config()`                                                             | **OK**                                                                                 |
| `backend/services/real_time_streaming_service.py`                               | Passes `snowflake_config` but may originate from legacy patterns                          | Verify callers supply ESC-backed config                                                |
| `backend/services/snowflake/pooled_connection.py`                               | Retrieves connection params via `secure_snowflake_config`                                  | Validate `secure_snowflake_config` uses ESC under the hood                              |
| `backend/infrastructure/adapters/snowflake_adapter.py`                          | Uses `SnowflakeConfigManager` from scripts; ensure manager sources ESC                   | Confirm `SnowflakeConfigManager` delegates to ESC config                                |
| `backend/services/schema_discovery_service.py`                                  | Loads templates under `backend/snowflake_setup`; separate from runtime config             | Ensure SQL scripts use ESC-based pattern for credentials                                |
| Other miscellaneous services instantiating `snowflake.connector.connect` directly | Various services (e.g., `kb_management_service.py`, `enhanced_snowflake_cortex_service.py`, etc.) | Replace with `get_snowflake_config()`                                                   |

---

## 3. Pulumi ESC & GitHub Actions

- **Secrets in GitHub Actions** (`.github/workflows/uv-ci-cd.yml`):
  ```yaml
  env:
    PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
    PULUMI_CONFIG_PASSPHRASE: ${{ secrets.PULUMI_CONFIG_PASSPHRASE }}
  ```
- **Snowflake ESC keys** expected:
  - `snowflake_account`
  - `snowflake_user`
  - `snowflake_password`
  - `snowflake_role`
  - `snowflake_warehouse`
  - `snowflake_database`
  - `snowflake_schema`

Ensure these are defined in GitHub Org Secrets and syncing into Pulumi stack.

---

## 4. Remediation Steps

1. **Refactor hardcoded connectors**
   - In `unified_ai_orchestration_service.py`, replace direct `snowflake.connector.connect(...)` calls with:
     ```python
     from backend.core.auto_esc_config import get_snowflake_config
     config = get_snowflake_config()
     conn = snowflake.connector.connect(**config)
     ```
2. **Validate pooled & adapter modules**
   - Confirm `secure_snowflake_config` and `SnowflakeConfigManager` internally call `get_snowflake_config()`.
3. **Audit all direct imports**
   - Search for `snowflake.connector.connect(` and replace with unified ESC-based pattern.
4. **Add CI lint rule**
   - Introduce a Ruff or custom linter rule preventing direct hardcoded Snowflake credentials.
5. **Update documentation**
   - Add a section in `00_SOPHIA_AI_SYSTEM_HANDBOOK.md` under “Security Framework” describing Snowflake config ingestion via Pulumi ESC.
6. **Secret sync verification**
   - Write a Pulumi health-check script asserting all Snowflake keys are present in ESC.
7. **GitHub Actions smoke test**
   - Add a workflow step post-deploy that runs `pulumi config get snowflake_account` and fails if empty.

---

## 5. Future Prevention

- Enforce **no direct** `connector.connect` parameters except via `get_snowflake_config()`.
- Maintain ADRs for any new Snowflake access patterns.
- Include configuration audit in nightly health checks.
- Train developers on ESC-based config pattern and add pre-commit hook verifying no literal strings matching Snowflake account formats.

---
*End of Snowflake Access & IaC Alignment Review*
