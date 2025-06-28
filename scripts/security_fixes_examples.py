#!/usr/bin/env python3
"""
Sophia AI - Security Fixes Examples
This file demonstrates practical implementations of security fixes for identified issues.
"""

import hashlib
import subprocess
import os
import re
from typing import List, Dict, Any, Optional


# -----------------------------------------------------------------------------
# 1. MD5 Hash Security Fixes
# -----------------------------------------------------------------------------

# INSECURE - Using MD5 hash without usedforsecurity=False
def insecure_generate_cache_key(url: str) -> str:
    """Insecure way to generate a cache key using MD5."""
    return hashlib.md5(url.encode()).hexdigest()


# SECURE - Using MD5 with usedforsecurity=False for non-security purposes
def secure_generate_cache_key(url: str) -> str:
    """Secure way to generate a cache key using MD5 with usedforsecurity=False."""
    return hashlib.md5(url.encode(), usedforsecurity=False).hexdigest()


# SECURE - Using a more secure hash algorithm for security purposes
def secure_generate_hash_for_security(data: str) -> str:
    """Secure way to generate a hash for security purposes using SHA-256."""
    return hashlib.sha256(data.encode()).hexdigest()


# -----------------------------------------------------------------------------
# 2. Command Injection Fixes
# -----------------------------------------------------------------------------

# INSECURE - Using shell=True with subprocess
def insecure_run_command(command: str) -> subprocess.CompletedProcess:
    """Insecure way to run a command with shell=True."""
    return subprocess.run(command, shell=True, capture_output=True, text=True)


# SECURE - Avoid shell=True by passing command as list
def secure_run_command(command_args: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    """Secure way to run a command by passing arguments as a list."""
    return subprocess.run(command_args, capture_output=True, text=True, cwd=cwd)


# SECURE - Example of converting a shell command string to argument list
def convert_shell_command_to_args(command: str) -> List[str]:
    """Convert a shell command string to a list of arguments.
    Note: This is a simplified version and may not handle all shell syntax."""
    # For complex commands, consider using shlex.split()
    import shlex
    return shlex.split(command)


# EXAMPLE - How to use the secure approach for different scenarios
def example_secure_command_usage():
    """Example of how to use secure command execution in different scenarios."""
    # Simple command
    result = secure_run_command(["ls", "-la"])
    
    # Command with cd (change directory)
    # Instead of: subprocess.run("cd /tmp && ls", shell=True)
    # Use multiple steps:
    original_dir = os.getcwd()
    try:
        os.chdir("/tmp")
        result = secure_run_command(["ls"])
    finally:
        os.chdir(original_dir)
    
    # Or use cwd parameter:
    result = secure_run_command(["ls"], cwd="/tmp")
    
    # For pip/npm installs:
    # Instead of: subprocess.run("uv add requests", shell=True)
    result = secure_run_command(["pip", "install", "requests"])


# -----------------------------------------------------------------------------
# 3. Hardcoded Secrets Fixes
# -----------------------------------------------------------------------------

# INSECURE - Hardcoded secrets
class InsecureSecretManager:
    """Insecure secret management with hardcoded values."""
    
    def __init__(self):
        self.api_key = "api_key_12345"
        self.webhook_secret = "webhook_secret_67890"
        self.database_password = "database_password_abcde"


# SECURE - Environment variables and secure storage
class SecureSecretManager:
    """Secure secret management using environment variables and config service."""
    
    def __init__(self):
        self.config_service = None  # This would be your actual config service
        self.secrets = {}
        self._load_secrets()
    
    def _load_secrets(self):
        """Load secrets from environment or secure storage."""
        try:
            # First try to load from a secure config service
            if self.config_service:
                self.secrets["api_key"] = self.config_service.get_secret("api_key")
                self.secrets["webhook_secret"] = self.config_service.get_secret("webhook_secret")
                self.secrets["database_password"] = self.config_service.get_secret("database_password")
            else:
                # Fall back to environment variables if config service is not available
                self.secrets["api_key"] = os.environ.get("API_KEY")
                self.secrets["webhook_secret"] = os.environ.get("WEBHOOK_SECRET")
                self.secrets["database_password"] = os.environ.get("DATABASE_PASSWORD")
        except Exception as e:
            # Log the error but don't expose secret loading failures in detail
            print(f"Error loading secrets: {type(e).__name__}")
            raise
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get a secret by name."""
        return self.secrets.get(secret_name)


# -----------------------------------------------------------------------------
# 4. File Permissions Fixes
# -----------------------------------------------------------------------------

# INSECURE - Overly permissive file permissions
def insecure_make_executable(script_path: str):
    """Insecure way to make a script executable with overly permissive permissions."""
    os.chmod(script_path, 0o755)  # rwxr-xr-x (readable and executable by anyone)


# SECURE - Use least privilege permissions
def secure_make_executable(script_path: str):
    """Secure way to make a script executable with minimal necessary permissions."""
    os.chmod(script_path, 0o700)  # rwx------ (readable and executable only by owner)


# -----------------------------------------------------------------------------
# 5. SQL Injection Fixes
# -----------------------------------------------------------------------------

# INSECURE - SQL string concatenation
def insecure_query_database(conn, user_id: str, status: str):
    """Insecure database query using string concatenation."""
    query = f"SELECT * FROM users WHERE user_id = '{user_id}' AND status = '{status}'"
    return conn.execute(query)


# SECURE - Parameterized queries
def secure_query_database(conn, user_id: str, status: str):
    """Secure database query using parameterized queries."""
    query = "SELECT * FROM users WHERE user_id = ? AND status = ?"
    return conn.execute(query, (user_id, status))


# SECURE - For special cases where parameters aren't supported
def secure_schema_operations(conn, schema_name: str):
    """Secure schema operations with validation."""
    # Validate schema name (only allow alphanumeric and underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', schema_name):
        raise ValueError("Invalid schema name")
    
    # Now it's safe to use in a query that doesn't support parameters
    query = f"USE SCHEMA {schema_name}"
    return conn.execute(query)


# -----------------------------------------------------------------------------
# 6. XSS Prevention in Jinja2
# -----------------------------------------------------------------------------

# INSECURE - Jinja2 without autoescape
def insecure_jinja_setup():
    """Insecure Jinja2 setup without autoescape."""
    from jinja2 import Environment
    
    env = Environment(
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env


# SECURE - Jinja2 with autoescape
def secure_jinja_setup():
    """Secure Jinja2 setup with autoescape enabled."""
    from jinja2 import Environment
    
    env = Environment(
        autoescape=True,  # Enable autoescaping
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env


# SECURE - Jinja2 with selective autoescaping
def secure_jinja_setup_selective():
    """Secure Jinja2 setup with selective autoescaping."""
    from jinja2 import Environment, select_autoescape
    
    env = Environment(
        autoescape=select_autoescape(
            enabled_extensions=('html', 'xml', 'j2'),
            default_for_string=True
        ),
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env


# -----------------------------------------------------------------------------
# 7. Unsafe Deserialization Fixes
# -----------------------------------------------------------------------------

# INSECURE - Using pickle for deserialization
def insecure_deserialize(serialized_data):
    """Insecure deserialization using pickle."""
    import pickle
    return pickle.loads(serialized_data)


# SECURE - Using JSON for deserialization
def secure_deserialize_json(serialized_data):
    """Secure deserialization using JSON."""
    import json
    return json.loads(serialized_data)


# SECURE - Using MessagePack for binary data
def secure_deserialize_msgpack(serialized_data):
    """Secure deserialization using MessagePack.
    Note: Requires the 'msgpack' package to be installed (pip install msgpack)."""
    try:
        import msgpack
        return msgpack.unpackb(serialized_data)
    except ImportError:
        print("MessagePack not installed. Install with: pip install msgpack")
        # Fallback to JSON if msgpack is not available
        import json
        import base64
        # Assume serialized_data might be binary, convert to base64 string first
        return json.loads(base64.b64encode(serialized_data).decode('utf-8'))


# SECURE - Validated pickle deserialization with schema enforcement
def secure_deserialize_with_validation(serialized_data, allowed_classes=None):
    """More secure deserialization with validation and schema enforcement."""
    import pickle
    import io
    
    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            # Only allow safe classes from known modules
            if allowed_classes and (module, name) in allowed_classes:
                return super().find_class(module, name)
            raise pickle.UnpicklingError(f"Global '{module}.{name}' is forbidden")
    
    return RestrictedUnpickler(io.BytesIO(serialized_data)).load()


# Example of allowed classes for secure unpickling
ALLOWED_PICKLE_CLASSES = {
    ('builtins', 'list'),
    ('builtins', 'dict'),
    ('builtins', 'set'),
    ('collections', 'OrderedDict'),
    ('datetime', 'datetime'),
}


if __name__ == "__main__":
    # Example usage of secure functions
    url = "https://example.com/page?param=value"
    
    # MD5 Hash
    secure_key = secure_generate_cache_key(url)
    print(f"Secure cache key: {secure_key}")
    
    # Command execution
    result = secure_run_command(["echo", "Hello, secure world!"])
    print(f"Command output: {result.stdout}")
    
    # Message to developers
    print("\nREMEMBER: Always follow secure coding practices!")
    print("- Never use MD5 for security purposes")
    print("- Never use shell=True with subprocess")
    print("- Never hardcode secrets")
    print("- Use least privilege file permissions")
    print("- Always use parameterized queries")
    print("- Enable autoescaping in templates")
    print("- Use safe deserialization methods")