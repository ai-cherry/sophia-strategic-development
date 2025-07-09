# Secret Rotation Guide

## Overview

This guide provides comprehensive instructions for rotating secrets in the Sophia AI platform, with special emphasis on Programmatic Access Tokens (PAT) used by MCP servers.

## Secret Types and Rotation Schedule

| Secret Type | Rotation Frequency | Priority | Impact |
|-------------|-------------------|----------|---------|
| PAT Tokens | 90 days | HIGH | Service disruption |
| API Keys | 180 days | MEDIUM | Feature degradation |
| Database Passwords | 365 days | LOW | Maintenance window |
| JWT Secrets | 90 days | HIGH | Session invalidation |

## PAT Token Rotation

### 1. Snowflake PAT Rotation

#### Generate New PAT

**Via Snowflake UI**:
1. Log into Snowflake Console
2. Navigate to Account → Security → Programmatic Access
3. Click "Generate Token"
4. Set expiration to 90 days
5. Copy token immediately (shown only once)

**Via SQL**:
```sql
-- Generate new PAT
CALL SYSTEM$GENERATE_SCIM_ACCESS_TOKEN('SOPHIA_AI_MCP_SERVICE');

-- View token (save immediately)
SELECT * FROM TABLE(INFORMATION_SCHEMA.SCIM_ACCESS_TOKENS())
WHERE CREATED_ON > DATEADD('minute', -5, CURRENT_TIMESTAMP());
```

#### Update Secrets

1. **GitHub Organization Secret**:
```bash
# Update production PAT
gh secret set SNOWFLAKE_MCP_PAT_PROD --org ai-cherry

# Update staging PAT
gh secret set SNOWFLAKE_MCP_PAT_STAGING --org ai-cherry
```

2. **Trigger Sync Workflow**:
```bash
# Sync to Pulumi ESC
gh workflow run sync_secrets.yml
```

3. **Verify in Pulumi ESC**:
```bash
pulumi env get default/sophia-ai-production --show-secrets | grep snowflake_mcp_pat
```

### 2. Pulumi PAT Rotation

```bash
# Generate new token
pulumi access-token create sophia-mcp-rotation --description "MCP Server Access"

# Update GitHub secret
gh secret set PULUMI_MCP_PAT_PROD --org ai-cherry

# Trigger sync
gh workflow run sync_secrets.yml
```

### 3. Estuary PAT Rotation

1. Log into Estuary Dashboard
2. Navigate to Settings → API Tokens
3. Create new token with appropriate scopes
4. Update GitHub secret: `ESTUARY_MCP_PAT_PROD`
5. Trigger sync workflow

## Automated Rotation Script

### Installation

```bash
# Make script executable
chmod +x scripts/rotate_pat.py
```

### Usage

```bash
# Rotate specific PAT
python scripts/rotate_pat.py --service snowflake --env prod

# Rotate all PATs
python scripts/rotate_pat.py --all --env prod

# Dry run
python scripts/rotate_pat.py --service snowflake --env prod --dry-run
```

### Script Implementation

```python
#!/usr/bin/env python3
"""PAT rotation script for Sophia AI."""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List

class PATRotator:
    """Handles PAT rotation for various services."""

    SERVICES = {
        "snowflake": {
            "secret_name": "SNOWFLAKE_MCP_PAT",
            "rotation_days": 90,
            "generator": "generate_snowflake_pat"
        },
        "pulumi": {
            "secret_name": "PULUMI_MCP_PAT",
            "rotation_days": 90,
            "generator": "generate_pulumi_pat"
        },
        "estuary": {
            "secret_name": "ESTUARY_MCP_PAT",
            "rotation_days": 90,
            "generator": "generate_estuary_pat"
        }
    }

    def rotate_pat(self, service: str, env: str, dry_run: bool = False):
        """Rotate PAT for a specific service."""
        if service not in self.SERVICES:
            raise ValueError(f"Unknown service: {service}")

        config = self.SERVICES[service]
        secret_name = f"{config['secret_name']}_{env.upper()}"

        print(f"🔄 Rotating PAT for {service} ({env})")

        if not dry_run:
            # Generate new PAT
            new_pat = getattr(self, config['generator'])(env)

            # Update GitHub secret
            self._update_github_secret(secret_name, new_pat)

            # Trigger sync
            self._trigger_sync_workflow()

            # Log rotation
            self._log_rotation(service, env)

        print(f"✅ PAT rotation complete for {service}")
```

## API Key Rotation

### 1. OpenAI API Key

```bash
# Generate new key at platform.openai.com
# Update GitHub secret
gh secret set OPENAI_API_KEY --org ai-cherry

# Trigger sync
gh workflow run sync_secrets.yml
```

### 2. Anthropic API Key

```bash
# Generate new key at console.anthropic.com
# Update GitHub secret
gh secret set ANTHROPIC_API_KEY --org ai-cherry

# Trigger sync
gh workflow run sync_secrets.yml
```

## Database Password Rotation

### Snowflake User Password

```sql
-- Change password
ALTER USER SOPHIA_AI_USER SET PASSWORD = 'new_secure_password';

-- Update GitHub secret
-- gh secret set SNOWFLAKE_PASSWORD_PROD --org ai-cherry
```

### PostgreSQL Password

```sql
-- Change password
ALTER USER sophia_user WITH PASSWORD 'new_secure_password';

-- Update connection strings
```

## JWT Secret Rotation

### 1. Generate New Secret

```python
import secrets
new_secret = secrets.token_urlsafe(64)
print(f"New JWT secret: {new_secret}")
```

### 2. Dual-Key Period

To avoid invalidating existing sessions:

1. Add new secret as secondary
2. Validate tokens with both secrets
3. Issue new tokens with new secret
4. After grace period, remove old secret

```python
# Configuration during rotation
JWT_SECRETS = {
    "primary": "new_secret_key",
    "secondary": "old_secret_key",  # Remove after grace period
}
```

## Rotation Checklist

### Pre-Rotation

- [ ] Identify all services using the secret
- [ ] Schedule maintenance window if needed
- [ ] Backup current configuration
- [ ] Prepare rollback plan

### During Rotation

- [ ] Generate new secret
- [ ] Update GitHub Organization Secret
- [ ] Trigger sync workflow
- [ ] Verify Pulumi ESC update
- [ ] Test service connectivity

### Post-Rotation

- [ ] Monitor service health
- [ ] Check error logs
- [ ] Update documentation
- [ ] Schedule next rotation

## Emergency Procedures

### Service Disruption

If a service fails after rotation:

1. **Immediate Rollback**:
```bash
# Revert to previous secret
gh secret set SECRET_NAME --org ai-cherry < backup_secret.txt

# Trigger sync
gh workflow run sync_secrets.yml
```

2. **Debug Connection**:
```bash
# Test MCP server health
curl -H "Authorization: Bearer $PAT" http://server:port/health
```

3. **Check Logs**:
```bash
# View MCP server logs
kubectl logs deployment/mcp-server-name
```

### Lost Secret Recovery

If a secret is lost:

1. **Check Pulumi ESC History**:
```bash
pulumi env version-history default/sophia-ai-production
```

2. **Restore from Backup**:
```bash
# Pulumi stores encrypted backups
pulumi env restore default/sophia-ai-production --version <version>
```

## Monitoring and Alerts

### Secret Expiration Monitoring

```python
# Prometheus alert rule
- alert: SecretExpiringSoon
  expr: secret_expiry_days < 14
  for: 1h
  annotations:
    summary: "Secret {{ $labels.secret_name }} expires in {{ $value }} days"
```

### Rotation Tracking

```sql
-- Audit table for rotations
CREATE TABLE secret_rotation_log (
    id SERIAL PRIMARY KEY,
    secret_name VARCHAR(255),
    rotated_at TIMESTAMP,
    rotated_by VARCHAR(255),
    next_rotation DATE,
    status VARCHAR(50)
);
```

## Best Practices

1. **Automate Rotation**: Use scripts and workflows
2. **Test in Staging**: Always test rotation in staging first
3. **Document Everything**: Keep detailed rotation logs
4. **Monitor Continuously**: Set up expiration alerts
5. **Practice Recovery**: Test rollback procedures regularly

## Compliance

### SOC 2 Requirements

- Secrets rotated at least annually
- Rotation events logged and auditable
- Access to rotation tools restricted
- Encryption in transit and at rest

### Industry Standards

- Follow NIST guidelines for key management
- Implement principle of least privilege
- Use hardware security modules (HSM) where applicable
- Regular security audits

## Tools and Resources

### CLI Tools

```bash
# GitHub CLI for secret management
gh secret list --org ai-cherry

# Pulumi CLI for ESC
pulumi env get default/sophia-ai-production

# Snowflake CLI for PAT management
snow sql -q "SHOW PARAMETERS LIKE 'SCIM%'"
```

### Monitoring Dashboards

- Grafana: Secret Expiration Dashboard
- Prometheus: Secret Rotation Metrics
- Datadog: Security Compliance Tracking

### Documentation

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Pulumi ESC Documentation](https://www.pulumi.com/docs/esc/)
- [Snowflake PAT Documentation](https://docs.snowflake.com/en/user-guide/scim-intro)
