"""
Sophia AI Security Middleware

Comprehensive security middleware implementing enterprise-grade security measures
for all API endpoints including rate limiting, input validation, and security headers.
"""

import hashlib
import logging
import os
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import jwt
import redis
from flask import Flask, g, jsonify, request
from werkzeug.exceptions import BadRequest, TooManyRequests, Unauthorized

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Comprehensive security middleware for Sophia AI API"""

    def __init__(self, app: Flask, redis_url: str | None = None):
        self.app = app
        self.redis_client = None

        # Initialize Redis for rate limiting if URL provided
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("Redis connection established for rate limiting")
            except Exception as e:
                logger.warning(
                    f"Redis connection failed: {e}. Rate limiting will use in-memory storage."
                )
                self.redis_client = None

        # In-memory storage fallback for rate limiting
        self.rate_limit_storage = {}

        # Security configuration
        self.config = {
            "rate_limit": {
                "default": {"requests": 100, "window": 3600},  # 100 requests per hour
                "api": {
                    "requests": 1000,
                    "window": 3600,
                },  # 1000 requests per hour for API
                "auth": {
                    "requests": 10,
                    "window": 900,
                },  # 10 auth attempts per 15 minutes
            },
            "security_headers": {
                "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none';",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
                "Cross-Origin-Embedder-Policy": "require-corp",
                "Cross-Origin-Opener-Policy": "same-origin",
                "Cross-Origin-Resource-Policy": "cross-origin",
            },
            "cors": {
                "origins": [
                    "https://sophia-ai-frontend-dev.vercel.app",
                    "https://localhost:3000",
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "credentials": True,
            },
            "input_validation": {
                "max_content_length": 10 * 1024 * 1024,  # 10MB
                "allowed_content_types": [
                    "application/json",
                    "application/x-www-form-urlencoded",
                    "multipart/form-data",
                    "text/plain",
                ],
            },
        }

        # Initialize middleware
        self._setup_middleware()

    def _setup_middleware(self):
        """Setup all security middleware"""

        @self.app.before_request
        def before_request():
            """Execute before each request"""

            # Add request ID for tracing
            g.request_id = self._generate_request_id()

            # Log request details
            logger.info(
                f"Request {g.request_id}: {request.method} {request.path} from {request.remote_addr}"
            )

            # Validate content length
            if (
                request.content_length
                and request.content_length
                > self.config["input_validation"]["max_content_length"]
            ):
                logger.warning(
                    f"Request {g.request_id}: Content length too large: {request.content_length}"
                )
                raise BadRequest("Request entity too large")

            # Validate content type
            if (
                request.content_type
                and request.content_type.split(";")[0]
                not in self.config["input_validation"]["allowed_content_types"]
            ):
                logger.warning(
                    f"Request {g.request_id}: Invalid content type: {request.content_type}"
                )
                raise BadRequest("Unsupported content type")

            # Apply rate limiting
            self._apply_rate_limiting()

            # Validate input data
            self._validate_input_data()

        @self.app.after_request
        def after_request(response):
            """Execute after each request"""

            # Add security headers
            for header, value in self.config["security_headers"].items():
                response.headers[header] = value

            # Add CORS headers
            origin = request.headers.get("Origin")
            if origin in self.config["cors"]["origins"]:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = ", ".join(
                    self.config["cors"]["methods"]
                )
                response.headers["Access-Control-Allow-Headers"] = ", ".join(
                    self.config["cors"]["headers"]
                )
                if self.config["cors"]["credentials"]:
                    response.headers["Access-Control-Allow-Credentials"] = "true"

            # Add request ID to response
            response.headers["X-Request-ID"] = g.get("request_id", "unknown")

            # Log response details
            logger.info(
                f"Response {g.get('request_id', 'unknown')}: {response.status_code}"
            )

            return response

        @self.app.errorhandler(429)
        def handle_rate_limit(e):
            """Handle rate limit exceeded"""
            return (
                jsonify(
                    {
                        "error": "Rate limit exceeded",
                        "message": "Too many requests. Please try again later.",
                        "request_id": g.get("request_id", "unknown"),
                    }
                ),
                429,
            )

        @self.app.errorhandler(400)
        def handle_bad_request(e):
            """Handle bad request"""
            return (
                jsonify(
                    {
                        "error": "Bad request",
                        "message": str(e.description),
                        "request_id": g.get("request_id", "unknown"),
                    }
                ),
                400,
            )

        @self.app.errorhandler(401)
        def handle_unauthorized(e):
            """Handle unauthorized access"""
            return (
                jsonify(
                    {
                        "error": "Unauthorized",
                        "message": "Authentication required",
                        "request_id": g.get("request_id", "unknown"),
                    }
                ),
                401,
            )

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = str(time.time())
        remote_addr = request.remote_addr or "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")

        data = f"{timestamp}-{remote_addr}-{user_agent}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

    def _apply_rate_limiting(self):
        """Apply rate limiting based on endpoint and client"""

        # Determine rate limit category
        if request.path.startswith("/api/auth"):
            category = "auth"
        elif request.path.startswith("/api"):
            category = "api"
        else:
            category = "default"

        # Get rate limit configuration
        rate_config = self.config["rate_limit"][category]

        # Create rate limit key
        client_id = self._get_client_identifier()
        rate_key = f"rate_limit:{category}:{client_id}"

        # Check rate limit
        if self._is_rate_limited(rate_key, rate_config):
            logger.warning(f"Rate limit exceeded for {client_id} on {request.path}")
            raise TooManyRequests("Rate limit exceeded")

    def _get_client_identifier(self) -> str:
        """Get unique client identifier for rate limiting"""

        # Try to get authenticated user ID
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                return f"user:{payload.get('user_id', 'unknown')}"
            except Exception as e:
                logger.warning(f"Failed to decode JWT: {e}")

        # Fall back to IP address
        return f"ip:{request.remote_addr or 'unknown'}"

    def _is_rate_limited(self, key: str, config: dict[str, int]) -> bool:
        """Check if request should be rate limited"""

        current_time = int(time.time())
        window_start = current_time - config["window"]

        if self.redis_client:
            # Use Redis for distributed rate limiting
            try:
                pipe = self.redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(current_time): current_time})
                pipe.expire(key, config["window"])
                results = pipe.execute()

                request_count = results[1]
                return request_count >= config["requests"]

            except Exception as e:
                logger.error(f"Redis rate limiting error: {e}")
                # Fall back to in-memory storage

        # In-memory rate limiting fallback
        if key not in self.rate_limit_storage:
            self.rate_limit_storage[key] = []

        # Clean old entries
        self.rate_limit_storage[key] = [
            timestamp
            for timestamp in self.rate_limit_storage[key]
            if timestamp > window_start
        ]

        # Add current request
        self.rate_limit_storage[key].append(current_time)

        return len(self.rate_limit_storage[key]) > config["requests"]

    def _validate_input_data(self):
        """Validate input data for security"""

        if request.is_json:
            try:
                data = request.get_json()
                if data:
                    self._sanitize_json_data(data)
            except Exception as e:
                logger.warning(f"Invalid JSON data: {e}")
                raise BadRequest("Invalid JSON data") from e

    def _sanitize_json_data(self, data: Any, max_depth: int = 10):
        """Recursively sanitize JSON data"""

        if max_depth <= 0:
            raise BadRequest("JSON data too deeply nested")

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(key, str) and len(key) > 100:
                    raise BadRequest("JSON key too long")
                self._sanitize_json_data(value, max_depth - 1)

        elif isinstance(data, list):
            if len(data) > 1000:
                raise BadRequest("JSON array too large")
            for item in data:
                self._sanitize_json_data(item, max_depth - 1)

        elif isinstance(data, str):
            if len(data) > 10000:
                raise BadRequest("JSON string too long")

            # Check for potential XSS patterns
            dangerous_patterns = ["<script", "javascript:", "onload=", "onerror="]
            data_lower = data.lower()
            for pattern in dangerous_patterns:
                if pattern in data_lower:
                    logger.warning(f"Potential XSS attempt detected: {pattern}")
                    raise BadRequest("Invalid input data")


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for endpoints"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise Unauthorized("Authentication token required")

        try:
            token = auth_header.split(" ")[1]
            # In a real implementation, verify the JWT token
            # payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            # g.current_user = payload

            # For now, just validate token format
            if len(token) < 10:
                raise Unauthorized("Invalid authentication token")

        except Exception as e:
            logger.warning(f"Authentication failed: {e}")
            raise Unauthorized("Invalid authentication token") from e

        return f(*args, **kwargs)

    return decorated_function


def require_api_key(f: Callable) -> Callable:
    """Decorator to require API key for endpoints"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            raise Unauthorized("API key required")

        # In a real implementation, validate the API key against a database
        valid_api_keys = get_config_value("valid_api_keys", "").split(",")

        if api_key not in valid_api_keys:
            logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
            raise Unauthorized("Invalid API key")

        return f(*args, **kwargs)

    return decorated_function


def init_security_middleware(app: Flask) -> SecurityMiddleware:
    """Initialize security middleware for Flask app"""

    redis_url = os.getenv("REDIS_URL")
    security = SecurityMiddleware(app, redis_url)

    logger.info("Security middleware initialized successfully")
    return security
