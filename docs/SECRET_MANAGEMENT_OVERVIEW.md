# Sophia AI - Unified Secret Management Overview

This document consolidates information from `SECRET_MANAGEMENT_GUIDE.md` and `SECRETS_MANAGEMENT_IMPLEMENTATION.md`.
The Sophia platform manages all secrets through **GitHub Organization Secrets** synchronized to **Pulumi ESC**. The backend automatically loads secrets from ESC, removing the need for `.env` files or manual configuration.

## Key Points
- Secrets are stored in the `ai-cherry` GitHub organization and automatically synced to Pulumi ESC.
- Scripts in the `scripts/` directory help configure organization or repository secrets.
- `configure_pulumi_esc.sh` manages ESC environments and can import, sync and list secrets.
- After setup, running `backend/main.py` uses the synced secrets without additional steps.

Refer to the scripts mentioned above for usage examples and command options.
