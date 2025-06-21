# Security & Secrets Management Guide

This guide explains how to securely manage secrets, credentials, and sensitive data in Sophia AI. It is designed for both AI coding agents and human developers.

---

## 🔐 Centralized Secret Management
- **All secrets are managed via Pulumi ESC and GitHub Organization Secrets.**
- **No `.env` files or hardcoded secrets are used anywhere in the codebase.**
- **Secrets are automatically loaded into the backend via Pulumi ESC integration.**

---

## 🏗️ How It Works
1. **Secrets are defined at the GitHub Organization level.**
2. **GitHub Actions sync secrets to Pulumi ESC.**
3. **Backend loads secrets from Pulumi ESC at runtime.**
4. **No manual secret management or local `.env` files required.**

---

## 🧑‍💻 Secure Secret Loading Pattern
- **Always use the auto ESC config loader:**
  ```python
  from backend.core.auto_esc_config import config
  openai_key = config.openai_api_key
  gong_key = config.gong_access_key
  ```
- **Never hardcode secrets or credentials in code or config files.**
- **Never share secrets in chat, email, or documentation.**

---

## 🔄 Secret Rotation & Audit Logging
- **To rotate a secret:**
  1. Update the secret in the GitHub Organization settings.
  2. GitHub Actions will sync the new secret to Pulumi ESC.
  3. The backend will pick up the new secret automatically on restart or reload.
- **All secret access and changes are logged for auditability.**
- **Use the CEO dashboard and logs to monitor secret usage and rotation events.**

---

## 🛡️ Best Practices
- **Never commit secrets to the repository.**
- **Use role-based access control for secret management.**
- **Enable audit logging for all secret access and changes.**
- **Rotate secrets regularly and after any suspected compromise.**
- **Document all secret usage in code with clear, AI-parseable comments.**

---

## 📝 Example: Secure API Client
```python
from backend.core.auto_esc_config import config
import openai
openai.api_key = config.openai_api_key
```

---

## AI-Parseable Section
- All secret names, access patterns, and rotation steps are documented in a consistent, parseable format for AI coding agents.
- Example queries and responses are included in this guide and in code comments.

---

For more details, see the onboarding guide, performance playbook, and CEO dashboard for live security and secret management status. 