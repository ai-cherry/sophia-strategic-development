# Enhanced Pulumi ESC Implementation Plan

## 🎯 Objective
Transform Sophia AI's Infrastructure as Code to a "fully finished, fully baked" state with:
- ✅ Automated SSH key management for Lambda Labs
- ✅ Consolidated TypeScript-only Pulumi infrastructure
- ✅ Complete IaC coverage for all services
- ✅ Bi-directional GitHub <-> Pulumi ESC synchronization

## 📅 Implementation Timeline

### Phase 1: SSH Key Automation (Day 1)
**Goal**: Eliminate manual SSH key configuration for Lambda Labs

1. **Generate and Store SSH Keys**
   ```bash
   cd infrastructure/esc
   python ssh_key_manager.py
   ```

2. **Update Lambda Labs Pulumi Provider**
   - Implement cloud-init user data injection
   - Base64 decode SSH keys from Pulumi ESC
   - Automatic key provisioning on instance creation

3. **Test SSH Access**
   ```bash
   ssh -i ~/.ssh/pulumi_lambda_key ubuntu@<instance-ip>
   ```

### Phase 2: Language Consolidation (Day 2-3)
**Goal**: Migrate all Pulumi code to TypeScript

1. **Convert Python Infrastructure**
   - Migrate `infrastructure/index.py` to TypeScript
   - Create unified `infrastructure/index.ts`
   - Implement provider pattern for each service

2. **Create Service Providers**
   - `providers/lambda-labs.ts`
   - `providers/snowflake.ts`
   - `providers/estuary.ts`
   - `providers/github.ts`
   - `providers/portkey.ts`

3. **Update Build System**
   ```bash
   cd infrastructure
   npm init -y
   npm install @pulumi/pulumi @pulumi/kubernetes
   npm install typescript ts-node
   ```

### Phase 3: Complete IaC Coverage (Day 4-7)
**Goal**: Implement IaC for all services

1. **Estuary Flow**
   - Connector provisioning
   - Data flow configuration
   - Collection management
   - Schedule automation

2. **Snowflake Enhanced**
   - Database/schema creation
   - User/role management
   - Grants and permissions
   - External stages and pipes

3. **GitHub Resources**
   - Repository management
   - Team configuration
   - Webhook setup
   - Branch protection rules

4. **Portkey Projects**
   - Virtual key management
   - Cost alert configuration
   - Project settings

### Phase 4: Bi-directional Sync (Day 8-9)
**Goal**: Automated secret synchronization

1. **GitHub Actions Workflow**
   ```yaml
   name: Sync Secrets Bi-directional
   on:
     schedule:
       - cron: '0 */6 * * *'  # Every 6 hours
     workflow_dispatch:
   ```

2. **Validation Framework**
   - Secret presence checking
   - Placeholder detection
   - Service readiness validation

3. **Monitoring and Alerts**
   - Secret rotation tracking
   - Sync failure notifications
   - Compliance reporting

## 🚀 Deployment Commands

### Initial Setup
```bash
# 1. Set up SSH key automation
cd infrastructure/esc
python ssh_key_manager.py

# 2. Install TypeScript dependencies
cd ../
npm install

# 3. Deploy infrastructure
pulumi up -s sophia-ai-production

# 4. Run bi-directional sync
cd esc
python github_sync_bidirectional.py
```

### Validation
```bash
# Validate all services
python infrastructure/esc/validate_iac_completeness.py

# Test SSH access
ssh -i ~/.ssh/pulumi_lambda_key ubuntu@$(pulumi stack output platform_ip)

# Check secret sync status
python infrastructure/esc/sync_status_validator.py
```

## 📊 Success Metrics

1. **SSH Automation**
   - ✅ Zero manual SSH key steps
   - ✅ Automatic key injection on instance creation
   - ✅ Successful SSH access without manual configuration

2. **Language Consolidation**
   - ✅ 100% TypeScript Pulumi code
   - ✅ Zero Python Pulumi files
   - ✅ Consistent provider pattern

3. **IaC Coverage**
   - ✅ All 5 services fully managed by Pulumi
   - ✅ No manual infrastructure steps
   - ✅ Complete automation from code to deployment

4. **Secret Management**
   - ✅ 100% secret synchronization
   - ✅ Zero placeholder values in production
   - ✅ Automated rotation capability

## 🛡️ Security Considerations

1. **SSH Key Security**
   - Private keys never stored in Pulumi ESC
   - Public keys base64 encoded for multi-line support
   - Proper file permissions (600 for private, 644 for public)

2. **Secret Rotation**
   - Automated rotation workflows
   - Audit trails for all changes
   - Zero-downtime secret updates

3. **Access Control**
   - GitHub organization admin for secret management
   - Pulumi RBAC for environment access
   - Service-specific IAM policies

## 📚 Documentation Updates

1. Update `infrastructure/README.md` to reflect:
   - TypeScript-only approach
   - Complete service coverage
   - SSH key automation

2. Update `docs/system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md`:
   - New IaC architecture
   - Automated workflows
   - Security enhancements

3. Create new guides:
   - `docs/infrastructure/SSH_KEY_AUTOMATION.md`
   - `docs/infrastructure/TYPESCRIPT_MIGRATION.md`
   - `docs/infrastructure/COMPLETE_IAC_GUIDE.md`

## ✅ Completion Checklist

- [ ] SSH key automation implemented and tested
- [ ] All Pulumi code migrated to TypeScript
- [ ] Estuary Flow IaC implemented
- [ ] Snowflake enhanced IaC implemented
- [ ] GitHub resources IaC implemented
- [ ] Portkey projects IaC implemented
- [ ] Bi-directional sync operational
- [ ] All secrets validated (no placeholders)
- [ ] Documentation fully updated
- [ ] Team trained on new workflows

## 🎉 Expected Outcome

A truly "fully finished, fully baked" Infrastructure as Code implementation where:
- Every infrastructure component is defined in code
- No manual steps required for any deployment
- Complete automation from commit to production
- Enterprise-grade security and compliance
- Zero-friction developer experience
