# Sophia AI Secret Management Guide

> **Classification**: CONFIDENTIAL  
> **Last Updated**: 2025-07-08  
> **Owner**: Security Team

## Overview

This guide documents the complete secret management lifecycle for Sophia AI, from creation to rotation to emergency access. All team members must follow these procedures to maintain security.

## Architecture

### Secret Flow

```
┌─────────────────────────┐
│   GitHub Organization   │
│       Secrets          │
│   (ai-cherry org)      │
└───────────┬────────────┘
            │ Sync via GitHub Actions
            ▼
┌─────────────────────────┐
│      Pulumi ESC        │
│  (Environment Secrets   │
│    Configuration)       │
└───────────┬────────────┘
            │ Automatic loading
            ▼
┌─────────────────────────┐
│   Application Runtime   │
│  (Environment Variables)│
└─────────────────────────┘
```

### Security Principles

1. **Zero Trust**: No secrets in code, ever
2. **Least Privilege**: Minimal access required
3. **Rotation**: Regular rotation schedule
4. **Audit**: All access logged
5. **Encryption**: At rest and in transit

## Secret Categories

### 1. AI/ML Services

| Secret | Purpose | Rotation | Format |
|--------|---------|----------|---------|
| `OPENAI_API_KEY` | OpenAI GPT access | 90 days | `sk-[48 chars]` |
| `ANTHROPIC_API_KEY` | Claude access | 90 days | `sk-ant-[95 chars]` |
| `PORTKEY_API_KEY` | LLM gateway | 90 days | `portkey-[32 chars]` |
| `OPENROUTER_API_KEY` | Model routing | 90 days | `sk-or-[32 chars]` |

### 2. Infrastructure

| Secret | Purpose | Rotation | Format |
|--------|---------|----------|---------|
| `LAMBDA_API_KEY` | Lambda Labs API | 180 days | `secret_*_[32].[28]` |
| `LAMBDA_SSH_PRIVATE_KEY` | SSH access | Annual | RSA private key |
| `DOCKER_HUB_ACCESS_TOKEN` | Registry push | 90 days | `dckr_pat_[20+]` |
| `PULUMI_ACCESS_TOKEN` | IaC state | Annual | `pul-[40 hex]` |

### 3. Data Services

| Secret | Purpose | Rotation | Format |
|--------|---------|----------|---------|
| `SNOWFLAKE_PASSWORD` | Data warehouse | 60 days | Complex password |
| `POSTGRES_PASSWORD` | Database | 90 days | Complex password |
| `REDIS_PASSWORD` | Cache | 90 days | Complex password |
| `PINECONE_API_KEY` | Vector DB | 180 days | `[36 chars]` |

### 4. Integrations

| Secret | Purpose | Rotation | Format |
|--------|---------|----------|---------|
| `GITHUB_TOKEN` | GitHub API | 90 days | `ghp_[36 chars]` |
| `LINEAR_API_KEY` | Project mgmt | 180 days | `lin_api_[32]` |
| `ASANA_ACCESS_TOKEN` | Task mgmt | 180 days | `[32+ chars]` |
| `SLACK_BOT_TOKEN` | Slack bot | Annual | `xoxb-[varies]` |

## Procedures

### Adding a New Secret

#### Step 1: Add to GitHub Organization

```bash
# Option A: GitHub UI
# 1. Go to https://github.com/organizations/ai-cherry/settings/secrets/actions
# 2. Click "New organization secret"
# 3. Enter name and value
# 4. Select repositories (sophia-main)

# Option B: GitHub CLI
gh secret set MY_NEW_SECRET --org ai-cherry --repos sophia-main
```

#### Step 2: Update Sync Workflow

```yaml
# .github/workflows/secret-sync.yml
env:
  MY_NEW_SECRET: ${{ secrets.MY_NEW_SECRET }}
```

#### Step 3: Update Secret Mapping

```python
# scripts/security/secret_mapping.py
SECRET_MAPPINGS.append(
    SecretMapping(
        github_name="MY_NEW_SECRET",
        esc_path="values.sophia.category.my_new_secret",
        category=SecretCategory.APPROPRIATE_CATEGORY,
        description="What this secret does",
        validation_regex=r"^pattern$",  # Optional
    )
)
```

#### Step 4: Run Synchronization

```bash
# Trigger sync workflow
gh workflow run secret-sync.yml

# Or run manually
python scripts/security/sync_secrets_to_esc.py
```

#### Step 5: Update Application

```python
# backend/core/settings.py
from pydantic import Field
from backend.core.auto_esc_config import get_config_value

class Settings(BaseSettings):
    my_new_secret: str = Field(
        default_factory=lambda: get_config_value("my_new_secret")
    )
```

### Rotating Secrets

#### Automated Rotation

1. **Update in GitHub**
   ```bash
   gh secret set SECRET_NAME --org ai-cherry --repos sophia-main
   ```

2. **Sync to Pulumi ESC**
   ```bash
   gh workflow run secret-sync.yml
   ```

3. **Restart Services**
   ```bash
   python scripts/deployment/rolling_restart.py
   ```

#### Manual Rotation Checklist

- [ ] Generate new secret value
- [ ] Update in GitHub organization secrets
- [ ] Run sync workflow
- [ ] Verify in Pulumi ESC
- [ ] Deploy/restart affected services
- [ ] Test functionality
- [ ] Update rotation date in tracking

### Accessing Secrets

#### For Development

```bash
# Never store secrets locally!
# Use Pulumi ESC for development

# 1. Login to Pulumi
pulumi login

# 2. Access development environment
pulumi env open scoobyjava-org/default/sophia-ai-development

# 3. Secrets are now in environment
python -c "from backend.core.auto_esc_config import get_config_value; print(get_config_value('openai_api_key')[:10] + '...')"
```

#### For Debugging

```bash
# Check if secret exists in GitHub
gh secret list --org ai-cherry

# Check if synced to Pulumi ESC
pulumi env get scoobyjava-org/default/sophia-ai-production | grep my_secret

# Check if loaded in application
docker exec sophia-backend python -c "import os; print('MY_SECRET' in os.environ)"
```

## Security Best Practices

### DO's

✅ **DO** use strong, unique secrets
✅ **DO** rotate secrets on schedule
✅ **DO** use secret scanning tools
✅ **DO** audit access regularly
✅ **DO** use least privilege principle
✅ **DO** document secret purpose

### DON'Ts

❌ **DON'T** commit secrets to git
❌ **DON'T** share secrets via email/slack
❌ **DON'T** use default passwords
❌ **DON'T** reuse secrets across environments
❌ **DON'T** log secret values
❌ **DON'T** hardcode secrets anywhere

## Rotation Schedule

### Monthly Tasks (First Monday)

```bash
# Run rotation check
python scripts/security/check_rotation_schedule.py

# Rotate any secrets due this month
python scripts/security/rotate_secrets.py --due-this-month
```

### Rotation Calendar

| Frequency | Secret Types | Next Rotation |
|-----------|--------------|---------------|
| 60 days | Database passwords | Check monthly |
| 90 days | API keys, tokens | Check monthly |
| 180 days | Integration tokens | Check monthly |
| Annual | SSH keys, certs | January |

## Emergency Procedures

### Compromised Secret

1. **Immediate Actions**
   ```bash
   # 1. Revoke/disable the compromised secret
   # 2. Generate new secret
   # 3. Update in GitHub
   gh secret set COMPROMISED_SECRET --org ai-cherry
   
   # 4. Deploy immediately
   gh workflow run emergency-secret-rotation.yml
   ```

2. **Investigation**
   - Check access logs
   - Audit git history
   - Review deployment logs
   - Identify exposure window

3. **Remediation**
   - Rotate related secrets
   - Update security policies
   - Document incident
   - Implement additional controls

### Lost Access

1. **GitHub Organization Admin**
   - Contact organization owner
   - Use backup admin account
   - Follow GitHub recovery

2. **Pulumi Access**
   - Use backup Pulumi admin
   - Contact Pulumi support
   - Restore from backup token

3. **Lambda Labs Access**
   - Use backup SSH key
   - Contact Lambda Labs support
   - Launch new instance if needed

## Monitoring & Alerts

### Secret Usage Monitoring

```python
# Metrics to track
- Secret access frequency
- Failed authentication attempts
- Unusual access patterns
- Rotation compliance
```

### Alert Conditions

| Alert | Condition | Action |
|-------|-----------|--------|
| Rotation Due | Age > threshold - 7 days | Email reminder |
| Access Spike | Access > 10x normal | Investigate |
| Auth Failure | Failures > 5 in 5 min | Check immediately |
| Missing Secret | Secret not found | Fix deployment |

## Compliance

### Audit Requirements

1. **Monthly Review**
   - Check all secret ages
   - Review access logs
   - Verify rotation compliance

2. **Quarterly Audit**
   - Full secret inventory
   - Access permission review
   - Update documentation

3. **Annual Security Review**
   - Complete security assessment
   - Update policies
   - Training refresh

### Documentation

All secrets must be documented with:
- Purpose and usage
- Owner/team responsible
- Rotation schedule
- Format/validation rules
- Dependencies

## Tools and Scripts

### Secret Management Tools

```bash
# Scan for exposed secrets
python scripts/security/scan_for_secrets.py

# Check rotation schedule
python scripts/security/check_rotation_schedule.py

# Validate all secrets
python scripts/security/validate_secrets.py

# Sync secrets
python scripts/security/sync_secrets_to_esc.py
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## Appendix

### Secret Naming Convention

```
{SERVICE}_{TYPE}_{ENVIRONMENT}

Examples:
OPENAI_API_KEY_PROD
SNOWFLAKE_PASSWORD_STAGING
LAMBDA_SSH_KEY_DEV
```

### Useful Commands

```bash
# List all GitHub secrets
gh secret list --org ai-cherry

# View Pulumi ESC environment
pulumi env get scoobyjava-org/default/sophia-ai-production

# Test secret loading
python -c "from backend.core.auto_esc_config import config; print(config.get_all_secrets())"

# Validate secret format
python scripts/security/validate_secret_format.py SECRET_NAME "secret_value"
```

### Emergency Contacts

- **Security Team**: security@ai-cherry.com
- **On-Call**: See GitHub organization
- **Escalation**: Via #security Slack channel

---

**Remember**: Security is everyone's responsibility. When in doubt, ask the security team! 