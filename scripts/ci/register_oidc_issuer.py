"""A script to programmatically register the GitHub OIDC issuer with Pulumi Cloud.

This uses a provided Pulumi Access Token for direct authentication.
"""

import logging
import os

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PULUMI_ORG = "scoobyjava-org"
PULUMI_API_URL = f"https://api.pulumi.com/api/orgs/{PULUMI_ORG}/oidc/issuers"

# --- These are the standard, correct values for GitHub Actions OIDC ---
ISSUER_NAME = "GitHub Actions"
ISSUER_URL = "https://token.actions.githubusercontent.com"
# This is a well-known, public thumbprint for GitHub's OIDC provider.
# It is safe to hardcode this value.
TLS_THUMBPRINT = "6938fd4d98bab03faadb97b34396831e3780aea1"


def register_github_oidc_issuer(api_token: str):
    """Makes a direct API call to Pulumi to register the GitHub OIDC issuer."""
    if not api_token:
        logger.error("Pulumi API token is missing.")
        return

    headers = {
        "Authorization": f"token {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.pulumi+8",
    }

    payload = {
        "name": ISSUER_NAME,
        "url": ISSUER_URL,
        "tlsCertificateThumbprints": [TLS_THUMBPRINT],
        "type": "public",  # For public providers like GitHub
    }

    logger.info(
        f"Registering OIDC issuer '{ISSUER_NAME}' for organization '{PULUMI_ORG}'..."
    )

    try:
        response = requests.post(PULUMI_API_URL, headers=headers, json=payload)

        # Check for success or if it already exists
        if response.status_code == 201:
            logger.info("✅ Successfully registered GitHub OIDC issuer.")
        elif response.status_code == 409:  # Conflict
            logger.warning(
                "⚠️ OIDC issuer with this URL or name already exists. No action needed."
            )
        else:
            response.raise_for_status()

    except requests.RequestException as e:
        logger.error(f"❌ Failed to register OIDC issuer via API: {e}")
        if e.response:
            logger.error(f"Response Body: {e.response.text}")
        raise


if __name__ == "__main__":
    pulumi_token = os.getenv("PULUMI_ACCESS_TOKEN")
    if not pulumi_token:
        raise ValueError("PULUMI_ACCESS_TOKEN environment variable not set.")
    register_github_oidc_issuer(pulumi_token)
