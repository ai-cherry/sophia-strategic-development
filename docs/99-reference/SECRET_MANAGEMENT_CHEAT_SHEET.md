# 🔐 Secret Management Cheat Sheet

## **Quick Reference for AI Agents**

### **Get Any Secret**
```python
from backend.core.auto_esc_config import get_config_value
secret = get_config_value("secret_name")
```

### **Common Secrets - Copy & Paste**

#### **Docker Hub**
```python
from backend.core.auto_esc_config import get_docker_hub_config
docker = get_docker_hub_config()
# docker["username"] = "scoobyjava15"
# docker["access_token"] = <from Pulumi ESC>
# docker["registry"] = "docker.io"
```

#### **Snowflake**
```python
from backend.core.auto_esc_config import get_snowflake_config
snowflake = get_snowflake_config()
# snowflake["account"] = "UHDECNO-CVB64222"
# snowflake["user"] = "SCOOBYJAVA15"
# snowflake["password"] = <from Pulumi ESC>
```

#### **Lambda Labs**
```python
from backend.core.auto_esc_config import get_lambda_labs_config
lambda_labs = get_lambda_labs_config()
# lambda_labs["api_key"] = <from Pulumi ESC>
# lambda_labs["ssh_private_key"] = <from Pulumi ESC>
```

#### **OpenAI**
```python
openai_key = get_config_value("openai_api_key")
```

#### **Slack**
```python
from backend.core.auto_esc_config import get_integration_config
integrations = get_integration_config()
slack = integrations["slack"]
# slack["bot_token"] = <from Pulumi ESC>
# slack["app_token"] = <from Pulumi ESC>
```

### **GitHub Actions - Already Available**
```yaml
# Docker Hub
username: ${{ secrets.DOCKER_HUB_USERNAME }}
password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}

# Lambda Labs
ssh_key: ${{ secrets.LAMBDA_PRIVATE_SSH_KEY }}

# Pulumi
PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
```

### **Quick Debug Commands**

#### **Check if secret exists in Pulumi ESC**
```bash
pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets | grep -i docker
```

#### **Test secret access from Python**
```bash
python -c "from backend.core.auto_esc_config import get_docker_hub_config; print(get_docker_hub_config())"
```

#### **List all GitHub org secrets**
```bash
gh secret list --org ai-cherry
```

#### **Trigger secret sync**
```bash
gh workflow run sync_secrets.yml
```

### **Common Mistakes to Avoid**

❌ **DON'T**
```python
# Manual login
os.system("docker login -u user -p password")

# Hardcoded secrets
DOCKER_TOKEN = "dckr_pat_xxxxx"

# Creating .env files
with open(".env", "w") as f:
    f.write("DOCKER_TOKEN=xxx")
```

✅ **DO**
```python
# Use the permanent solution
from backend.core.auto_esc_config import get_docker_hub_config
docker = get_docker_hub_config()
```

### **Secret Not Working?**

1. **Is it in GitHub?** → `gh secret list --org ai-cherry`
2. **Is it synced?** → Check last sync in GitHub Actions
3. **Is it mapped?** → Check `esc_key_mappings` in `auto_esc_config.py`
4. **Still broken?** → Run sync manually: `gh workflow run sync_secrets.yml`

### **Adding a New Secret**

1. **GitHub**: https://github.com/ai-cherry → Settings → Secrets → New
2. **Sync Script**: Add to `scripts/unified_secret_sync.py`
3. **Mapping**: Add to `backend/core/auto_esc_config.py`
4. **Push**: Changes trigger automatic sync

### **Remember**
- 🔐 Secrets are **ALREADY** in the system
- 🚀 GitHub Actions has **AUTOMATIC** access
- 🛠️ Use `get_config_value()` for **EVERYTHING**
- ❌ **NEVER** create manual solutions 