#!/usr/bin/env python3
"""
Ephemeral Credentials Test Script for Sophia AI Platform.

This script tests the ephemeral credentials system by creating, validating,
and revoking credentials.
"""

import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infrastructure.security.ephemeral_credentials.models import (
    CredentialRequest,
    CredentialRevocationRequest,
    CredentialScope,
    CredentialType,
    CredentialValidationRequest,
    TokenMetadata,
)
from infrastructure.security.ephemeral_credentials.service import (
    EphemeralCredentialsService,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def test_ephemeral_credentials():
    """Test the ephemeral credentials system."""
    logger.info("Starting ephemeral credentials test")

    # Create ephemeral credentials service
    storage_path = os.path.join(os.getcwd(), "data", "test_ephemeral_credentials.json")
    service = EphemeralCredentialsService(
        storage_path=storage_path,
        auto_save=True,
    )

    # Initialize service
    await service.initialize()
    logger.info("Ephemeral credentials service initialized")

    # Test credential creation
    logger.info("Testing credential creation")

    # Create API key
    api_key_request = CredentialRequest(
        name="Test API Key",
        credential_type=CredentialType.API_KEY,
        scopes=[
            CredentialScope.API_READ,
            CredentialScope.API_WRITE,
        ],
        ttl_seconds=3600,  # 1 hour
        metadata=TokenMetadata(
            user_id="test-user",
            client_id="test-client",
        ),
    )

    api_key_response = await service.create_credential(
        request=api_key_request,
        created_by="test-script",
    )

    logger.info(f"Created API key: {api_key_response.token_value}")

    # Create access token
    access_token_request = CredentialRequest(
        name="Test Access Token",
        credential_type=CredentialType.ACCESS_TOKEN,
        scopes=[
            CredentialScope.LLM_ACCESS,
            CredentialScope.AGENT_ACCESS,
        ],
        ttl_seconds=1800,  # 30 minutes
        metadata=TokenMetadata(
            user_id="test-user",
            client_id="test-client",
        ),
    )

    access_token_response = await service.create_credential(
        request=access_token_request,
        created_by="test-script",
    )

    logger.info(f"Created access token: {access_token_response.token_value}")

    # Create service token
    service_token_request = CredentialRequest(
        name="Test Service Token",
        credential_type=CredentialType.SERVICE_TOKEN,
        scopes=[
            CredentialScope.SERVICE_READ,
            CredentialScope.SERVICE_WRITE,
        ],
        ttl_seconds=86400,  # 24 hours
        metadata=TokenMetadata(
            service_id="test-service",
        ),
    )

    service_token_response = await service.create_credential(
        request=service_token_request,
        created_by="test-script",
    )

    logger.info(f"Created service token: {service_token_response.token_value}")

    # Test credential validation
    logger.info("Testing credential validation")

    # Validate API key
    api_key_validation = await service.validate_credential(
        request=CredentialValidationRequest(
            token_value=api_key_response.token_value,
            required_scopes=[CredentialScope.API_READ],
        )
    )

    logger.info(f"API key validation: {api_key_validation.valid}")
    assert api_key_validation.valid, "API key validation failed"

    # Validate access token
    access_token_validation = await service.validate_credential(
        request=CredentialValidationRequest(
            token_value=access_token_response.token_value,
            required_scopes=[CredentialScope.LLM_ACCESS],
        )
    )

    logger.info(f"Access token validation: {access_token_validation.valid}")
    assert access_token_validation.valid, "Access token validation failed"

    # Validate service token
    service_token_validation = await service.validate_credential(
        request=CredentialValidationRequest(
            token_value=service_token_response.token_value,
            required_scopes=[CredentialScope.SERVICE_READ],
        )
    )

    logger.info(f"Service token validation: {service_token_validation.valid}")
    assert service_token_validation.valid, "Service token validation failed"

    # Test credential validation with insufficient scopes
    logger.info("Testing credential validation with insufficient scopes")

    # Validate API key with insufficient scopes
    api_key_invalid_validation = await service.validate_credential(
        request=CredentialValidationRequest(
            token_value=api_key_response.token_value,
            required_scopes=[CredentialScope.SYSTEM_ADMIN],
        )
    )

    logger.info(f"API key invalid validation: {api_key_invalid_validation.valid}")
    assert (
        not api_key_invalid_validation.valid
    ), "API key invalid validation should fail"

    # Test credential revocation
    logger.info("Testing credential revocation")

    # Revoke API key
    api_key_revocation = await service.revoke_credential(
        request=CredentialRevocationRequest(
            credential_id=api_key_response.id,
            reason="Test revocation",
        ),
        revoked_by="test-script",
    )

    logger.info(f"API key revocation: {api_key_revocation}")
    assert api_key_revocation, "API key revocation failed"

    # Validate revoked API key
    api_key_revoked_validation = await service.validate_credential(
        request=CredentialValidationRequest(
            token_value=api_key_response.token_value,
        )
    )

    logger.info(f"Revoked API key validation: {api_key_revoked_validation.valid}")
    assert (
        not api_key_revoked_validation.valid
    ), "Revoked API key validation should fail"

    # Test credential listing
    logger.info("Testing credential listing")

    # List active credentials
    active_credentials = await service.list_credentials(
        include_expired=False,
        include_revoked=False,
    )

    logger.info(f"Active credentials: {len(active_credentials)}")
    assert len(active_credentials) == 2, "Should have 2 active credentials"

    # List all credentials
    all_credentials = await service.list_credentials(
        include_expired=True,
        include_revoked=True,
    )

    logger.info(f"All credentials: {len(all_credentials)}")
    assert len(all_credentials) == 3, "Should have 3 total credentials"

    # Test credential cleanup
    logger.info("Testing credential cleanup")

    # Create expired credential
    expired_token_request = CredentialRequest(
        name="Expired Token",
        credential_type=CredentialType.SESSION_TOKEN,
        scopes=[CredentialScope.API_READ],
        ttl_seconds=1,  # 1 second
        metadata=TokenMetadata(
            user_id="test-user",
        ),
    )

    expired_token_response = await service.create_credential(
        request=expired_token_request,
        created_by="test-script",
    )

    logger.info(f"Created expired token: {expired_token_response.token_value}")

    # Wait for token to expire
    logger.info("Waiting for token to expire...")
    await asyncio.sleep(2)

    # Clean up expired credentials
    removed_count = await service.cleanup_expired_credentials()

    logger.info(f"Removed {removed_count} expired credentials")
    assert removed_count == 1, "Should have removed 1 expired credential"

    # Shutdown service
    await service.shutdown()
    logger.info("Ephemeral credentials service shut down")

    logger.info("All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_ephemeral_credentials())
