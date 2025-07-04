# Sophia AI Vercel Infrastructure

Comprehensive Pulumi TypeScript infrastructure for automating Sophia AI's Vercel deployment and DNS configuration.

## 🎯 Overview

This Pulumi program automates:
- ✅ **Vercel Project Cleanup**: Removes legacy projects and domains
- ✅ **New Project Creation**: Creates production and development Vercel projects
- ✅ **Environment Configuration**: Sets up environment variables with proper scoping
- ✅ **Custom Domain Setup**: Configures `app.sophia-intel.ai` and `dev.app.sophia-intel.ai`
- ✅ **DNS Automation**: Automatically creates Namecheap DNS records (optional)
- ✅ **Domain Verification**: Handles TXT record verification for custom domains

## 📋 Prerequisites

### Required Tools
```bash
# Install Pulumi
curl -fsSL https://get.pulumi.com | sh

# Install Node.js 18+
# Install Vercel CLI
npm install -g vercel

# Install jq for JSON processing
# macOS: brew install jq
# Ubuntu: sudo apt install jq

# Install Python 3 and requests library
pip3 install requests
```

### Required Credentials
- **Vercel API Token**: From https://vercel.com/account/tokens
- **Vercel Team ID**: From your Vercel organization settings (optional)
- **Namecheap API Key**: From Namecheap account (optional for DNS automation)
- **Namecheap API User**: Your Namecheap username

## 🚀 Quick Start

### 1. Initialize Pulumi Stack
```bash
cd infrastructure/vercel
npm install

# Initialize stack
pulumi stack init scoobyjava-org/sophia-vercel-prod

# Or select existing stack
pulumi stack select scoobyjava-org/sophia-vercel-prod
```

### 2. Configure Secrets and Settings
```bash
# Required: Vercel configuration
pulumi config set --secret vercel:token <your-vercel-token>
pulumi config set vercel:teamId <your-team-id>  # Optional

# Optional: Namecheap DNS automation
pulumi config set --secret namecheap:apiKey <your-namecheap-api-key>
pulumi config set namecheap:apiUser <your-namecheap-username>

# Optional: Legacy project cleanup
pulumi config set deleteLegacyOrchestraProjects true  # Default: false
```

### 3. Deploy Infrastructure
```bash
# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up

# Check outputs
pulumi stack output
```

## ⚙️ Configuration Options

### Core Settings
| Setting | Description | Required | Default |
|---------|-------------|----------|---------|
| `vercel:token` | Vercel API access token | ✅ Yes | - |
| `vercel:teamId` | Vercel team/organization ID | ❌ No | - |
| `deleteLegacyOrchestraProjects` | Delete legacy projects | ❌ No | `false` |

### DNS Automation (Optional)
| Setting | Description | Required | Default |
|---------|-------------|----------|---------|
| `namecheap:apiKey` | Namecheap API key | ❌ No | - |
| `namecheap:apiUser` | Namecheap username | ❌ No | - |
| `namecheap:clientIp` | Client IP for API | ❌ No | `127.0.0.1` |

## 🏗️ Infrastructure Components

### Vercel Projects Created
1. **Production Project**
   - Name: `sophia-ai-frontend-prod`
   - Repository: `ai-cherry/sophia-main`
   - Root Directory: `frontend/`
   - Branch: `main`
   - Domain: `app.sophia-intel.ai`

2. **Development Project**
   - Name: `sophia-ai-frontend-dev`
   - Repository: `ai-cherry/sophia-main`
   - Root Directory: `frontend/`
   - Branch: `develop`
   - Domain: `dev.app.sophia-intel.ai`

### Environment Variables
#### Production Project
- `NEXT_PUBLIC_API_URL`: `https://api.sophia-intel.ai`
- `NEXT_PUBLIC_ENVIRONMENT`: `production`

#### Development Project
- `NEXT_PUBLIC_API_URL`: `https://dev.api.sophia-intel.ai`
- `NEXT_PUBLIC_ENVIRONMENT`: `development`

### DNS Records (Automated)
```
# CNAME Records
app.sophia-intel.ai → cname.vercel-dns.com
dev.app.sophia-intel.ai → cname.vercel-dns.com

# TXT Verification Records (Dynamic)
_vercel.app.sophia-intel.ai → <verification-value>
_vercel.dev.app.sophia-intel.ai → <verification-value>
```

## 🧹 Project Cleanup

### Always Deleted
These projects are always removed (not Git-connected):
- `frontend`
- `modern-admin`
- `dist`

### Conditionally Deleted
When `deleteLegacyOrchestraProjects: true`:
- `orchestra-main`
- `dashboard` (removes `dashboard.cherry-ai.me` domain first)
- `admin-interface` (removes `admin.cherry-ai.me` domain first)

## 📊 Outputs

After successful deployment:
```bash
pulumi stack output
```

### Available Outputs
- `productionProjectId`: Vercel project ID for production
- `developmentProjectId`: Vercel project ID for development
- `productionUrl`: Default Vercel URL for production
- `developmentUrl`: Default Vercel URL for development
- `productionCustomDomain`: Custom domain URL for production
- `developmentCustomDomain`: Custom domain URL for development
- `configurationSummary`: Summary of configuration settings
- `cleanupStatus`: Status of project cleanup operation
- `dnsSetupStatus`: Status of DNS configuration
- `verificationStatus`: Domain verification status

## 🔧 Manual DNS Setup (If Automation Disabled)

If Namecheap API credentials are not provided, add these records manually:

### Namecheap Advanced DNS Settings
```
Type: CNAME
Host: app
Value: cname.vercel-dns.com
TTL: 300

Type: CNAME
Host: dev.app
Value: cname.vercel-dns.com
TTL: 300
```

### Verification Records
After deployment, check the output for TXT verification records:
```bash
pulumi stack output dnsSetupStatus
```

Add the displayed TXT records to Namecheap DNS.

## 🚨 Troubleshooting

### Common Issues

#### 1. Project Already Exists
```bash
# Check existing projects
vercel projects ls

# Manual cleanup if needed
vercel projects rm <project-name> --yes
```

#### 2. Domain Verification Failed
```bash
# Check domain status
vercel domains inspect app.sophia-intel.ai

# Re-run verification
pulumi refresh
pulumi up
```

#### 3. DNS Propagation Issues
```bash
# Check DNS propagation
dig app.sophia-intel.ai
nslookup app.sophia-intel.ai

# Wait 5-60 minutes for propagation
```

#### 4. Namecheap API Issues
```bash
# Verify API credentials
curl "https://api.namecheap.com/xml.response?ApiUser=<user>&ApiKey=<key>&UserName=<user>&Command=namecheap.domains.getList&ClientIp=127.0.0.1"

# Check IP whitelist in Namecheap account
```

### Debug Commands
```bash
# View detailed logs
pulumi logs

# Check resource status
pulumi stack

# Force refresh
pulumi refresh --yes

# Destroy and recreate
pulumi destroy --yes
pulumi up --yes
```

## 🔄 Updates and Maintenance

### Updating Configuration
```bash
# Update Vercel token
pulumi config set --secret vercel:token <new-token>

# Update team ID
pulumi config set vercel:teamId <new-team-id>

# Apply changes
pulumi up
```

### Adding New Environment Variables
```typescript
// Add to index.ts
const newEnvVar = new vercel.ProjectEnvironmentVariable("new-env", {
    projectId: prodProject.id,
    target: ["production"],
    key: "NEW_VARIABLE",
    value: "new-value",
    teamId: vercelTeamId,
});
```

### Scaling to Additional Environments
```typescript
// Add staging project
const stagingProject = new vercel.Project("sophia-ai-staging", {
    name: "sophia-ai-frontend-staging",
    framework: "nextjs",
    gitRepository: {
        type: "github",
        repo: githubRepo,
        productionBranch: "staging",
    },
    // ... other configuration
});
```

## 📚 Additional Resources

- [Pulumi Vercel Provider Documentation](https://www.pulumi.com/registry/packages/vercel/)
- [Vercel API Documentation](https://vercel.com/docs/rest-api)
- [Namecheap API Documentation](https://www.namecheap.com/support/api/)
- [Sophia AI Infrastructure Documentation](../../README.md)

## 🤝 Contributing

1. Make changes to `index.ts`
2. Test with `pulumi preview`
3. Deploy with `pulumi up`
4. Update documentation as needed
5. Commit changes to repository

## 📄 License

This infrastructure code is part of the Sophia AI project and follows the same licensing terms.
