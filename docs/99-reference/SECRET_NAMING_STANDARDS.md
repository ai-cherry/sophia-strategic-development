# Secret Naming Standards

## **Naming Convention Rules**

### **GitHub Organization Secrets**
- **Format**: `UPPER_CASE_WITH_UNDERSCORES`
- **Prefix**: None (organization-wide)
- **Examples**:
  - `DOCKER_HUB_ACCESS_TOKEN`
  - `LAMBDA_PRIVATE_SSH_KEY`
  - `PULUMI_ACCESS_TOKEN`

### **Pulumi ESC**
- **Format**: `lower_case_with_underscores`
- **Path**: Nested under service categories
- **Examples**:
  - `values.sophia.infrastructure.docker.access_token`
  - `values.sophia.ai.openai.api_key`
  - `values.sophia.business.gong.access_key`

### **Backend Access**
- **Format**: `lower_case_with_underscores`
- **Access**: Via `get_config_value()`
- **Examples**:
  - `get_config_value("docker_hub_access_token")`
  - `get_config_value("lambda_api_key")`
  - `get_config_value("openai_api_key")`

## **Mapping Pattern**

```python
# In backend/core/auto_esc_config.py
esc_key_mappings = {
    "backend_name": "pulumi_esc_path",
    # Examples:
    "docker_hub_access_token": "docker_hub_access_token",
    "lambda_api_key": "lambda_api_key",
}
```

## **Service-Specific Standards**

### **Docker Hub**
- **GitHub**: `DOCKER_HUB_ACCESS_TOKEN`, `DOCKER_HUB_USERNAME`
- **Pulumi**: `docker_hub_access_token`, `docker_hub_username`
- **Backend**: `get_docker_hub_config()`

### **Lambda Labs**
- **GitHub**: `LAMBDA_API_KEY`, `LAMBDA_PRIVATE_SSH_KEY`
- **Pulumi**: `lambda_api_key`, `lambda_ssh_private_key`
- **Backend**: `get_lambda_labs_config()`

### **Snowflake**
- **GitHub**: `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ACCOUNT`
- **Pulumi**: `snowflake_password`, `snowflake_account`
- **Backend**: `get_snowflake_config()`

### **AI Services**
- **GitHub**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Pulumi**: `openai_api_key`, `anthropic_api_key`
- **Backend**: `get_config_value("openai_api_key")`

## **Migration Rules**

When renaming secrets:

1. **Keep both names temporarily**
   ```python
   "docker_token": "docker_token",  # Legacy
   "docker_hub_access_token": "docker_hub_access_token",  # New
   ```

2. **Update all references**
   - GitHub workflows
   - Python scripts
   - Documentation

3. **Remove legacy after verification**

## **Validation Script**

```python
# Validate secret naming
from backend.core.auto_esc_config import get_config_value

required_secrets = [
    "docker_hub_access_token",
    "lambda_api_key",
    "openai_api_key",
    "snowflake_password",
]

for secret in required_secrets:
    value = get_config_value(secret)
    if not value or value.startswith("PLACEHOLDER"):
        print(f"❌ {secret}: Missing or placeholder")
    else:
        print(f"✅ {secret}: Configured")
```

## **Common Naming Mistakes**

❌ **Incorrect**:
- `DockerHubToken` (wrong case)
- `DOCKERHUB_TOKEN` (missing underscore)
- `docker-hub-token` (hyphens instead of underscores)
- `DOCKER_TOKEN` (ambiguous name)

✅ **Correct**:
- `DOCKER_HUB_ACCESS_TOKEN` (GitHub)
- `docker_hub_access_token` (Pulumi/Backend)

## **Future-Proofing**

1. **Be specific**: `DOCKER_HUB_ACCESS_TOKEN` not `DOCKER_TOKEN`
2. **Include service**: `GITHUB_API_TOKEN` not just `API_TOKEN`
3. **Indicate type**: `LAMBDA_PRIVATE_SSH_KEY` not `LAMBDA_KEY`
4. **Version if needed**: `OPENAI_API_KEY_V2` for migrations 