# Sophia AI Quick Reference Card

## 🚀 Essential Commands

### Snowflake Connection
```bash
# Test connection (run from /tmp to avoid Python path issues)
cd /tmp && PYTHONPATH="" python -c "
import snowflake.connector
conn = snowflake.connector.connect(
    account='UHDECNO-CVB64222',
    user='SCOOBYJAVA15',
    password='<PAT_TOKEN>',
    role='ACCOUNTADMIN'
)
print('✅ Connected!')
"
```

### GitHub Actions
```bash
# Trigger secrets sync
gh workflow run sync_secrets.yml

# Check workflow status
gh workflow list

# View runs
gh run list
```

### Lambda Labs
```bash
# Check instances via API
curl -H "Authorization: Bearer $LAMBDA_API_KEY" \
  https://cloud.lambdalabs.com/api/v1/instances
```

### Docker Hub
```bash
# Login
docker login -u scoobyjava15

# Push image
docker push scoobyjava15/sophia-ai:latest
```

### K3s Deployment
```bash
# Deploy to Lambda Labs (via SSH)
ssh ubuntu@<INSTANCE_IP> < deploy_k3s_lambda_labs.sh

# Check cluster
kubectl get nodes
kubectl get all -A
```

## 🔑 Key Endpoints

- **Snowflake**: UHDECNO-CVB64222.snowflakecomputing.com
- **Lambda Labs**: 192.222.58.232 (primary cluster)
- **Docker Registry**: docker.io/scoobyjava15
- **GitHub Org**: https://github.com/ai-cherry
- **Pulumi Org**: scoobyjava-org

## 📊 Service Status Check

```bash
# Run comprehensive infrastructure check
python scripts/setup_infrastructure_comprehensive.py

# Generate fresh report
python scripts/setup_infrastructure_comprehensive.py report
```

## 🚨 Important Notes

1. **Snowflake PAT**: Valid until June 24, 2026
2. **Master Token**: Valid until June 24, 2026
3. **Environment**: Always defaults to "prod"
4. **Deployment**: Always via GitHub Actions

## 🧹 Cleanup After Use

```bash
# One-time scripts to delete after use:
rm deploy_k3s_lambda_labs.sh
rm deploy_mcp_lambda_labs.sh
```

## 💡 Troubleshooting

### Snowflake Connection Issues
- Use PAT token as password
- Run from outside project directory
- Check account format includes organization

### Lambda Labs No IP
- Access via Lambda Labs dashboard
- Use SSH keys from secrets

### GitHub Actions Failures
- Check organization secrets
- Verify PAT permissions
- Review workflow logs

## 📞 Quick Support

- **Documentation**: `docs/system_handbook/`
- **Infrastructure Guide**: `INFRASTRUCTURE_SETUP_GUIDE.md`
- **Setup Script**: `scripts/setup_infrastructure_comprehensive.py` 