# Sophia AI - Secure Credential Management Guide

## 🔐 Security Notice

This repository uses **Pulumi ESC (Environment, Secrets, and Configuration)** for secure credential management. **No secrets are stored in source code.**

## 🚀 Quick Setup

### 1. Environment Variables Required

Copy `.env.example` to `.env` and fill in your actual values:

```bash
cp .env.example .env
```

### 2. Required Credentials

You'll need to obtain and configure these credentials:

#### Pulumi Configuration
- `PULUMI_ORG`: Your Pulumi organization name
- `PULUMI_ACCESS_TOKEN`: Your Pulumi access token from https://app.pulumi.com/account/tokens

#### AI Services
- `OPENAI_API_KEY`: OpenAI API key from https://platform.openai.com/api-keys

#### Business Integrations
- `GONG_ACCESS_KEY`: Gong API access key
- `GONG_CLIENT_SECRET`: Gong client secret
- `GONG_URL`: Your Gong instance URL

#### Development Tools
- `RETOOL_API_TOKEN`: Retool API token for dashboard integration

### 3. Pulumi ESC Setup

Once you have your credentials:

```bash
# Set up Pulumi ESC environments
./scripts/setup_pulumi_esc.sh

# Configure environment variables
./scripts/setup_environment.sh
```

### 4. Start the Application

```bash
# Start backend API
python3 simple_server.py

# Start frontend dashboard (in another terminal)
cd sophia-dashboard
npm run dev --host
```

## 🛡️ Security Best Practices

### ✅ What We Do
- Use Pulumi ESC for centralized secret management
- Environment-based configuration
- No secrets in source code
- Automated secret rotation capabilities
- Role-based access control

### ❌ What We Don't Do
- Store API keys in `.env` files committed to Git
- Hardcode secrets in application code
- Share credentials via insecure channels
- Use the same secrets across environments

## 🔄 Secret Rotation

Pulumi ESC supports automated secret rotation:

```bash
# Rotate all secrets
pulumi env set your-org/sophia-ai-production secrets.rotation_enabled true

# Rotate specific secret
pulumi env set your-org/sophia-ai-production secrets.openai_key "new-api-key" --secret
```

## 📋 Environment Structure

```
sophia-ai-base/          # Shared configuration
├── organization
├── project
└── common settings

sophia-ai-production/    # Production secrets
├── imports: [sophia-ai-base]
├── openai_key (secret)
├── gong_credentials (secret)
└── database_url (secret)

sophia-ai-development/   # Development secrets
├── imports: [sophia-ai-base]
├── openai_key (secret)
└── test_credentials
```

## 🚨 Emergency Procedures

### If Secrets Are Compromised
1. **Immediately rotate** all affected credentials
2. **Update Pulumi ESC** with new values
3. **Redeploy applications** to use new secrets
4. **Audit access logs** for unauthorized usage

### If Pulumi Access Is Lost
1. **Contact Pulumi support** for account recovery
2. **Use backup access tokens** if available
3. **Regenerate all secrets** as a precaution

## 📞 Support

For credential management issues:
- **Pulumi ESC**: https://www.pulumi.com/docs/esc/
- **Security Questions**: Contact your security team
- **Technical Issues**: Check the troubleshooting guide

## 🔍 Audit Trail

All secret access is logged via Pulumi ESC:
- Who accessed which secrets
- When secrets were retrieved
- Which applications used credentials
- Any unauthorized access attempts

This ensures complete visibility and compliance with security policies.

