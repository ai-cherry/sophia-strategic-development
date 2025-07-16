"""
Centralized rate limiting utilities for Sophia AI
Provides common patterns for rate limiting API calls and operations
"""

import asyncio
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

from shared.utils.errors import RateLimitError

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""

    max_calls: int
    time_window: float  # seconds
    burst_limit: Optional[int] = None
    service_name: Optional[str] = None

class RateLimiter:
    """Thread-safe rate limiter with burst support"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.calls: deque = deque()
        self.lock = asyncio.Lock()

        # Use burst limit if specified, otherwise use max_calls
        self.burst_limit = config.burst_limit or config.max_calls

    async def acquire(self):
        """Acquire permission to make a call"""
        async with self.lock:
            now = time.time()

            # Remove old calls outside the time window
            cutoff_time = now - self.config.time_window
            while self.calls and self.calls[0] <= cutoff_time:
                self.calls.popleft()

            # Check if we're at the limit
            if len(self.calls) >= self.burst_limit:
                # Calculate wait time until the oldest call expires
                oldest_call = self.calls[0]
                wait_time = self.config.time_window - (now - oldest_call)

                if wait_time > 0:
                    raise RateLimitError(
                        message=f"Rate limit exceeded for {self.config.service_name or 'service'}",
                        retry_after=int(wait_time) + 1,
                        service=self.config.service_name,
                    )

            # Add current call
            self.calls.append(now)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass

    def reset(self):
        """Reset the rate limiter"""
        self.calls.clear()

class MultiServiceRateLimiter:
    """Rate limiter that manages multiple services"""

    def __init__(self):
        self.limiters: dict[str, RateLimiter] = {}
        self.lock = asyncio.Lock()

    def add_service(self, service_name: str, config: RateLimitConfig):
        """Add a service with its rate limit configuration"""
        config.service_name = service_name
        self.limiters[service_name] = RateLimiter(config)

    async def acquire(self, service_name: str):
        """Acquire permission for a specific service"""
        if service_name not in self.limiters:
            # No rate limit configured for this service
            return

        await self.limiters[service_name].acquire()

    def reset(self, service_name: Optional[str] = None):
        """Reset rate limiter(s)"""
        if service_name:
            if service_name in self.limiters:
                self.limiters[service_name].reset()
        else:
            # Reset all
            for limiter in self.limiters.values():
                limiter.reset()

class TokenBucketRateLimiter:
    """Token bucket rate limiter for smooth rate limiting"""

    def __init__(
        self,
        rate: float,  # tokens per second
        capacity: int,  # maximum tokens
        service_name: Optional[str] = None,
    ):
        self.rate = rate
        self.capacity = capacity
        self.service_name = service_name
        self.tokens = float(capacity)
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the bucket.
        Returns wait time if tokens are not available.
        """
        async with self.lock:
            now = time.time()

            # Add tokens based on time elapsed
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0.0  # No wait needed

            # Calculate wait time
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.rate

            raise RateLimitError(
                message=f"Rate limit exceeded for {self.service_name or 'service'}",
                retry_after=int(wait_time) + 1,
                service=self.service_name,
            )

    async def acquire_with_wait(self, tokens: int = 1) -> None:
        """Acquire tokens, waiting if necessary"""
        while True:
            try:
                await self.acquire(tokens)
                return
            except RateLimitError as e:
                if e.retry_after:
                    await asyncio.sleep(e.retry_after)

def rate_limit(max_calls: int, time_window: float, burst_limit: Optional[int] = None):
    """Decorator for rate limiting async functions"""

    def decorator(func: Callable) -> Callable:
        # Create a rate limiter for this function
        config = RateLimitConfig(
            max_calls=max_calls,
            time_window=time_window,
            burst_limit=burst_limit,
            service_name=func.__name__,
        )
        limiter = RateLimiter(config)

        async def wrapper(*args, **kwargs):
            async with limiter:
                return await func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator

# Global rate limiter instance for shared use
_global_rate_limiter: Optional[MultiServiceRateLimiter] = None

def get_global_rate_limiter() -> MultiServiceRateLimiter:
    """Get or create the global rate limiter"""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = MultiServiceRateLimiter()
    return _global_rate_limiter
