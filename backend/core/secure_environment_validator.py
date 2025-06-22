"""Validate that required environment variables are present."""

from __future__ import annotations

import os


class SecureEnvironmentValidator:
    """Check runtime environment for required secrets."""

    REQUIRED_VARS = ["PULUMI_ORG", "PULUMI_STACK"]

    def validate(self) -> None:
        """Raise ``RuntimeError`` if mandatory variables are missing."""

        missing = [var for var in self.REQUIRED_VARS if not os.getenv(var)]
        if missing:
            raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
