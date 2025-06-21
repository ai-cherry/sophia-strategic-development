# Sophia AI - Infrastructure Operations Guide

This document is the single source of truth for deploying, managing, and troubleshooting the Sophia AI infrastructure.

## 1. Onboarding a New Engineer

To get a new engineer set up to manage the Sophia infrastructure, follow these steps:

1.  **Install Core Dependencies:**
    *   Python 3.11+
    *   Pulumi CLI
    *   Node.js (for some Pulumi providers)

2.  **Grant Access:**
    *   Add the engineer's email to the `admin-access` policy in `infrastructure/esc/__main__.py`.
    *   Invite the engineer to your Pulumi organization.
    *   Grant them access to the Lambda Labs account.
    *   Grant them access to the company GitHub organization.

3.  **Initial Setup:**
    *   Clone the `sophia-main` repository.
    *   Run `pip install -r infrastructure/requirements.txt` to install Python dependencies.
    *   Run `pulumi login` to authenticate with the Pulumi service.

## 2. Deploying Infrastructure

All infrastructure is managed via Pulumi.

### Deploying to an Environment

To deploy or update an environment (e.g., `staging`), run the following commands from the root of the repository:

```bash
pulumi stack select staging
pulumi up
```

### End-to-End Deployment Test

To test a full deployment from scratch, use the `iac-audit-test` stack:

```bash
pulumi stack init iac-audit-test --copy-config-from production
pulumi up -s iac-audit-test --yes
python infrastructure/test_deployment.py
pulumi destroy -s iac-audit-test --yes
pulumi stack rm iac-audit-test
```

## 3. Managing Secrets

All secrets are managed via Pulumi ESC and the scripts in `infrastructure/esc/`.

### Adding a New Secret

1.  Add the secret definition to the appropriate service file (e.g., `gong_secrets.py`).
2.  Add the secret mapping to `infrastructure/esc/__main__.py`.
3.  Run `pulumi up` on the target environment to apply the change.
4.  Use the `inject_secrets.sh` script to securely provide the secret's value.

### Rotating a Secret

1.  Follow the procedure defined in `infrastructure/esc/secret_rotation_framework.py`.
2.  Update the secret value in Pulumi ESC.
3.  Run `pulumi up` to propagate the change.

## 4. Troubleshooting

**Common Error: Pulumi deployment fails on a resource.**
*   **Solution:** Check the detailed error message in the Pulumi console. It often points to a misconfigured secret or an invalid API key. Use `pulumi preview` to see the planned changes before running `pulumi up`.

**Common Error: `test_deployment.py` fails.**
*   **Solution:** Check the output of the script to see which component failed. This usually indicates a problem with network connectivity (firewalls, security groups) or incorrect credentials.
