#!/usr/bin/env python3
"""
Simplified Ephemeral Credentials Test Script for Sophia AI Platform.

This script tests the ephemeral credentials system using a simplified implementation
that doesn't depend on the secret_management module.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Simplified models
class CredentialScope(str, Enum):
    """Scope of the ephemeral credential."""
    API_READ = "api:read"
    API_WRITE = "api:write"
    LLM_ACCESS = "llm:access"
    AGENT_ACCESS = "agent:access"
    SERVICE_READ = "service:read"
    SERVICE_WRITE = "service:write"
    SYSTEM_ADMIN = "system:admin"


class CredentialType(str, Enum):
    """Type of ephemeral credential."""
    API_KEY = "api_key"
    ACCESS_TOKEN = "access_token"
    SERVICE_TOKEN = "service_token"
    SESSION_TOKEN = "session_token"


class CredentialStatus(str, Enum):
    """Status of ephemeral credential."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


# Simplified ephemeral credentials service
class SimpleEphemeralCredentialsService:
    """Simplified ephemeral credentials service for testing."""
    
    def __init__(self, storage_path: str):
        """Initialize the service."""
        self.storage_path = storage_path
        self.credentials = {}
        self._load_from_storage()
    
    def _load_from_storage(self):
        """Load credentials from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                self.credentials = data.get("credentials", {})
            except Exception as e:
                logger.error(f"Failed to load credentials: {e}")
                self.credentials = {}
    
    def _save_to_storage(self):
        """Save credentials to storage."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump({"credentials": self.credentials}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
    
    async def create_credential(self, name: str, credential_type: str, scopes: List[str], ttl_seconds: int, user_id: Optional[str] = None):
        """Create a new credential."""
        # Generate ID
        cred_id = str(uuid.uuid4())
        
        # Generate token
        if credential_type == "api_key":
            token = f"sk-sophia-{uuid.uuid4().hex}"
        else:
            token = f"{uuid.uuid4().hex}.{uuid.uuid4().hex}"
        
        # Calculate expiration
        expires_at = (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat()
        
        # Create credential
        credential = {
            "id": cred_id,
            "name": name,
            "credential_type": credential_type,
            "token_value": token,
            "scopes": scopes,
            "status": "active",
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": expires_at,
            "user_id": user_id,
        }
        
        # Store credential
        self.credentials[cred_id] = credential
        self._save_to_storage()
        
        return credential
    
    async def validate_credential(self, token_value: str, required_scopes: Optional[List[str]] = None):
        """Validate a credential."""
        # Find credential by token
        credential = None
        for cred in self.credentials.values():
            if cred.get("token_value") == token_value:
                credential = cred
                break
        
        # If credential not found
        if not credential:
            return {"valid": False, "error": "Invalid credential"}
        
        # Check if expired
        if datetime.fromisoformat(credential["expires_at"]) <= datetime.now(UTC):
            return {"valid": False, "error": "Credential expired"}
        
        # Check if revoked
        if credential["status"] == "revoked":
            return {"valid": False, "error": "Credential revoked"}
        
        # Check scopes
        if required_scopes:
            for scope in required_scopes:
                if scope not in credential["scopes"]:
                    return {"valid": False, "error": "Insufficient scopes"}
        
        # Update last used
        credential["last_used_at"] = datetime.now(UTC).isoformat()
        self._save_to_storage()
        
        return {
            "valid": True,
            "credential_id": credential["id"],
            "scopes": credential["scopes"],
            "expires_at": credential["expires_at"],
        }
    
    async def revoke_credential(self, credential_id: str):
        """Revoke a credential."""
        if credential_id not in self.credentials:
            return False
        
        self.credentials[credential_id]["status"] = "revoked"
        self.credentials[credential_id]["revoked_at"] = datetime.now(UTC).isoformat()
        self._save_to_storage()
        
        return True
    
    async def list_credentials(self, include_expired: bool = False, include_revoked: bool = False):
        """List credentials."""
        result = []
        now = datetime.now(UTC)
        
        for cred in self.credentials.values():
            # Skip expired credentials
            if not include_expired and datetime.fromisoformat(cred["expires_at"]) <= now:
                continue
            
            # Skip revoked credentials
            if not include_revoked and cred["status"] == "revoked":
                continue
            
            result.append(cred)
        
        return result
    
    async def cleanup_expired_credentials(self):
        """Clean up expired credentials."""
        now = datetime.now(UTC)
        expired_ids = []
        
        for cred_id, cred in self.credentials.items():
            if datetime.fromisoformat(cred["expires_at"]) <= now:
                expired_ids.append(cred_id)
        
        for cred_id in expired_ids:
            del self.credentials[cred_id]
        
        if expired_ids:
            self._save_to_storage()
        
        return len(expired_ids)


async def test_ephemeral_credentials():
    """Test the ephemeral credentials system."""
    logger.info("Starting ephemeral credentials test")
    
    # Create service
    storage_path = os.path.join(os.getcwd(), "data", "test_ephemeral_credentials.json")
    service = SimpleEphemeralCredentialsService(storage_path)
    
    # Test credential creation
    logger.info("Testing credential creation")
    
    # Create API key
    api_key = await service.create_credential(
        name="Test API Key",
        credential_type="api_key",
        scopes=["api:read", "api:write"],
        ttl_seconds=3600,
        user_id="test-user",
    )
    
    logger.info(f"Created API key: {api_key['token_value']}")
    
    # Create access token
    access_token = await service.create_credential(
        name="Test Access Token",
        credential_type="access_token",
        scopes=["llm:access", "agent:access"],
        ttl_seconds=1800,
        user_id="test-user",
    )
    
    logger.info(f"Created access token: {access_token['token_value']}")
    
    # Create service token
    service_token = await service.create_credential(
        name="Test Service Token",
        credential_type="service_token",
        scopes=["service:read", "service:write"],
        ttl_seconds=86400,
        user_id="test-service",
    )
    
    logger.info(f"Created service token: {service_token['token_value']}")
    
    # Test credential validation
    logger.info("Testing credential validation")
    
    # Validate API key
    api_key_validation = await service.validate_credential(
        token_value=api_key["token_value"],
        required_scopes=["api:read"],
    )
    
    logger.info(f"API key validation: {api_key_validation['valid']}")
    assert api_key_validation["valid"], "API key validation failed"
    
    # Validate access token
    access_token_validation = await service.validate_credential(
        token_value=access_token["token_value"],
        required_scopes=["llm:access"],
    )
    
    logger.info(f"Access token validation: {access_token_validation['valid']}")
    assert access_token_validation["valid"], "Access token validation failed"
    
    # Validate service token
    service_token_validation = await service.validate_credential(
        token_value=service_token["token_value"],
        required_scopes=["service:read"],
    )
    
    logger.info(f"Service token validation: {service_token_validation['valid']}")
    assert service_token_validation["valid"], "Service token validation failed"
    
    # Test credential validation with insufficient scopes
    logger.info("Testing credential validation with insufficient scopes")
    
    # Validate API key with insufficient scopes
    api_key_invalid_validation = await service.validate_credential(
        token_value=api_key["token_value"],
        required_scopes=["system:admin"],
    )
    
    logger.info(f"API key invalid validation: {api_key_invalid_validation['valid']}")
    assert not api_key_invalid_validation["valid"], "API key invalid validation should fail"
    
    # Test credential revocation
    logger.info("Testing credential revocation")
    
    # Revoke API key
    api_key_revocation = await service.revoke_credential(
        credential_id=api_key["id"],
    )
    
    logger.info(f"API key revocation: {api_key_revocation}")
    assert api_key_revocation, "API key revocation failed"
    
    # Validate revoked API key
    api_key_revoked_validation = await service.validate_credential(
        token_value=api_key["token_value"],
    )
    
    logger.info(f"Revoked API key validation: {api_key_revoked_validation['valid']}")
    assert not api_key_revoked_validation["valid"], "Revoked API key validation should fail"
    
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
    expired_token = await service.create_credential(
        name="Expired Token",
        credential_type="session_token",
        scopes=["api:read"],
        ttl_seconds=1,
        user_id="test-user",
    )
    
    logger.info(f"Created expired token: {expired_token['token_value']}")
    
    # Wait for token to expire
    logger.info("Waiting for token to expire...")
    await asyncio.sleep(2)
    
    # Clean up expired credentials
    removed_count = await service.cleanup_expired_credentials()
    
    logger.info(f"Removed {removed_count} expired credentials")
    assert removed_count == 1, "Should have removed 1 expired credential"
    
    logger.info("All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_ephemeral_credentials())

