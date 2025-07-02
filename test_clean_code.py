#!/usr/bin/env python3
"""
Clean, secure code example for testing Codacy analysis
Demonstrates best practices and security-conscious programming
"""

import logging
import secrets
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureUserManager:
    """Secure user management with proper error handling and validation"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Ensure database exists and has proper schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Safely retrieve user data using parameterized queries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # Using parameterized query to prevent SQL injection
                cursor.execute(
                    "SELECT id, username, email, created_at FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve user {user_id}: {e}")
            return None
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create new user with secure password hashing"""
        try:
            # Validate inputs
            if not self._validate_user_input(username, email, password):
                return False
            
            password_hash = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash)
                )
                conn.commit()
            
            logger.info(f"User {username} created successfully")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"User creation failed: username or email already exists")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error during user creation: {e}")
            return False
    
    def _validate_user_input(self, username: str, email: str, password: str) -> bool:
        """Validate user input data"""
        if not username or len(username) < 3:
            logger.warning("Username too short")
            return False
        
        if not email or '@' not in email:
            logger.warning("Invalid email format")
            return False
        
        if not password or len(password) < 8:
            logger.warning("Password too short")
            return False
        
        return True
    
    def _hash_password(self, password: str) -> str:
        """Securely hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

class SecureTokenGenerator:
    """Cryptographically secure token generation"""
    
    @staticmethod
    def generate_api_token(length: int = 32) -> str:
        """Generate cryptographically secure API token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate secure session identifier"""
        return secrets.token_hex(16)

class ConfigManager:
    """Secure configuration file handling"""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def read_config(self, config_name: str) -> Optional[str]:
        """Safely read configuration file with path validation"""
        try:
            # Validate config name to prevent path traversal
            if not self._is_valid_config_name(config_name):
                logger.warning(f"Invalid config name: {config_name}")
                return None
            
            config_path = self.config_dir / config_name
            
            # Ensure the resolved path is within config directory
            if not str(config_path.resolve()).startswith(str(self.config_dir.resolve())):
                logger.warning(f"Path traversal attempt detected: {config_name}")
                return None
            
            if config_path.exists() and config_path.is_file():
                return config_path.read_text(encoding='utf-8')
            else:
                logger.info(f"Config file not found: {config_name}")
                return None
                
        except (OSError, IOError) as e:
            logger.error(f"Failed to read config {config_name}: {e}")
            return None
    
    def _is_valid_config_name(self, name: str) -> bool:
        """Validate configuration file name"""
        # Only allow alphanumeric, dots, and hyphens
        return name.replace('.', '').replace('-', '').replace('_', '').isalnum()

def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """Safely divide two numbers with proper error handling"""
    try:
        if denominator == 0:
            logger.warning("Division by zero attempted")
            return None
        return numerator / denominator
    except (TypeError, ValueError) as e:
        logger.error(f"Invalid input for division: {e}")
        return None

def process_user_list(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean, focused function for processing user data"""
    processed_users = []
    
    for user in users:
        if not isinstance(user, dict):
            logger.warning("Invalid user data format")
            continue
        
        # Simple, clear processing logic
        processed_user = {
            'id': user.get('id'),
            'username': user.get('username', '').strip(),
            'email': user.get('email', '').lower().strip(),
            'is_active': user.get('status') == 'active'
        }
        
        # Validate required fields
        if processed_user['id'] and processed_user['username'] and processed_user['email']:
            processed_users.append(processed_user)
        else:
            logger.warning(f"Incomplete user data: {user.get('id', 'unknown')}")
    
    return processed_users

if __name__ == "__main__":
    # Demonstrate secure code usage
    logger.info("Testing secure code patterns...")
    
    # Secure user management
    user_manager = SecureUserManager("test_users.db")
    user_data = user_manager.get_user_by_id(1)
    
    # Secure token generation
    token_generator = SecureTokenGenerator()
    api_token = token_generator.generate_api_token()
    
    # Secure configuration handling
    config_manager = ConfigManager("./config")
    config_data = config_manager.read_config("app.conf")
    
    # Safe mathematical operations
    result = safe_divide(10, 2)
    
    logger.info("Secure code testing completed successfully") 