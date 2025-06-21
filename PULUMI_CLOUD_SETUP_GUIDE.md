# Pulumi Cloud Setup Guide for Sophia AI

## 🎯 Overview
This guide walks you through setting up Pulumi Cloud access for the Sophia AI system to enable Infrastructure as Code (IaC) and Environment, Secrets, and Configuration (ESC) management.

## 📋 Prerequisites
- Pulumi CLI installed (✅ v3.177.0 detected)
- GitHub account for integration
- Access to create Pulumi organizations

## 🚀 Step-by-Step Setup

### 1. Create Pulumi Cloud Account

#### Option A: Sign up with GitHub (Recommended)
```bash
# Visit https://app.pulumi.com/signup
# Click "Sign up with GitHub"
# Authorize Pulumi to access your GitHub account
```

#### Option B: Sign up with Email
```bash
# Visit https://app.pulumi.com/signup
# Enter your email and create password
# Verify your email address
```

### 2. Create Pulumi Access Token

1. **Login to Pulumi Cloud**: https://app.pulumi.com
2. **Navigate to Settings**: Click your profile → Settings
3. **Access Tokens**: Go to "Access Tokens" tab
4. **Create New Token**:
   - Name: `sophia-ai-development`
   - Description: `Sophia AI Infrastructure Management`
   - Expiration: 90 days (or longer)
5. **Copy Token**: Save it securely - you won't see it again!

### 3. Configure Local Pulumi CLI

```bash
# Login to Pulumi Cloud
pulumi login

# When prompted, paste your access token
# Or set it as environment variable:
export PULUMI_ACCESS_TOKEN="pul-your-access-token-here"
pulumi login
```

### 4. Create or Join Organization

#### Option A: Create New Organization
```bash
# Visit https://app.pulumi.com/account/organizations/add
# Organization Name: "ai-cherry" (or your preferred name)
# Organization URL: "ai-cherry"
```

#### Option B: Use Existing Organization
```bash
# If you already have an organization, note its name
# Update PULUMI_ORG in your environment
```

### 5. Update Environment Configuration

```bash
# Update .env file with your actual values
cat > .env << 'EOF'
# Pulumi Configuration
PULUMI_ORG=ai-cherry
PULUMI_ACCESS_TOKEN=pul-your-actual-access-token

# Core Application
SECRET_KEY=sophia-secret-key-$(openssl rand -hex 16)
JWT_SECRET=sophia-jwt-secret-$(openssl rand -hex 16)

# AI Services
OPENAI_API_KEY=sk-your-openai-key

# Business Integrations
GONG_ACCESS_KEY=your-gong-access-key
GONG_CLIENT_SECRET=your-gong-client-secret
GONG_URL=https://your-instance.app.gong.io

# Development Tools
RETOOL_API_TOKEN=your-retool-api-token

# Database (default development settings)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sophia_enhanced

# Configuration
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
```

### 6. Initialize Pulumi ESC Environments

```bash
# Load environment variables
source .env

# Run the ESC setup script
bash scripts/setup_pulumi_esc.sh
```

### 7. Verify Setup

```bash
# Check Pulumi login status
pulumi whoami

# List available environments
pulumi env ls

# Test environment access
pulumi env open ai-cherry/sophia-ai-production
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "file://~ does not support Pulumi ESC"
**Problem**: Logged into local backend instead of Pulumi Cloud
**Solution**:
```bash
pulumi logout
pulumi login  # Make sure to use cloud login
```

#### 2. "invalid character '<' looking for beginning of value"
**Problem**: Invalid access token or network issue
**Solution**:
```bash
# Generate new access token from Pulumi Cloud
# Ensure token starts with "pul-"
export PULUMI_ACCESS_TOKEN="pul-your-new-token"
pulumi login
```

#### 3. "organization not found"
**Problem**: Organization doesn't exist or no access
**Solution**:
```bash
# Create organization in Pulumi Cloud
# Or get invited to existing organization
# Update PULUMI_ORG environment variable
```

### 4. Environment Variables Not Loading
**Problem**: ESC environments not properly configured
**Solution**:
```bash
# Check environment configuration
pulumi env get ai-cherry/sophia-ai-production

# Update environment files
pulumi env set ai-cherry/sophia-ai-production --file infrastructure/esc/sophia-ai-production.yaml
```

## 🎯 Next Steps After Setup

### 1. Configure Secrets in ESC
```bash
# Set actual API keys in Pulumi ESC
pulumi env set ai-cherry/sophia-ai-production values.sophia.ai.openai.api_key "sk-your-actual-key" --secret

# Set Gong credentials
pulumi env set ai-cherry/sophia-ai-production values.sophia.business.gong.access_key "your-gong-key" --secret
```

### 2. Test Integration
```bash
# Test backend with ESC integration
export PULUMI_ORG=ai-cherry
python backend/main.py
```

### 3. Set up GitHub Integration
```bash
# Configure GitHub OIDC for secure CI/CD
# Add Pulumi access token to GitHub secrets
# Update GitHub Actions workflows
```

## 📊 Verification Checklist

- [ ] Pulumi Cloud account created
- [ ] Access token generated and saved
- [ ] Local CLI authenticated (`pulumi whoami` works)
- [ ] Organization created/joined
- [ ] ESC environments initialized
- [ ] Environment variables configured
- [ ] Backend starts without secret errors
- [ ] GitHub integration configured

## 🔐 Security Best Practices

1. **Token Management**:
   - Use short-lived tokens (90 days max)
   - Rotate tokens regularly
   - Store tokens securely (never commit to git)

2. **Environment Separation**:
   - Use separate environments for dev/staging/production
   - Implement least-privilege access
   - Audit environment access regularly

3. **Secret Management**:
   - Use ESC for all sensitive configuration
   - Enable secret encryption at rest
   - Implement secret rotation policies

## 📞 Support Resources

- **Pulumi Documentation**: https://www.pulumi.com/docs/
- **ESC Documentation**: https://www.pulumi.com/docs/esc/
- **Community Slack**: https://slack.pulumi.com/
- **GitHub Issues**: https://github.com/pulumi/pulumi/issues

## 🎉 Success Indicators

When setup is complete, you should be able to:
- Run `pulumi whoami` and see your cloud username
- List ESC environments with `pulumi env ls`
- Start the Sophia AI backend without credential errors
- Deploy infrastructure using `pulumi up`
- Access secrets through ESC integration

---

**Next**: Once Pulumi Cloud access is working, run the complete system deployment:
```bash
python scripts/deploy_complete_system.py
``` 