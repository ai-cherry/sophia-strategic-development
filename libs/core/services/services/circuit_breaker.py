import logging
from collections.abc import Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataError(Exception):
    """Base exception for data-related errors"""

    pass


class ConnectionError(DataError):
    """Raised when connection to data source fails"""

    pass


class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        name: str = "default",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        logger.info(
            f"CircuitBreaker '{self.name}' initialized: threshold={failure_threshold}, timeout={recovery_timeout}s"
        )

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if self._should_attempt_reset():
                logger.warning(
                    f"CircuitBreaker '{self.name}' is now half-open. Attempting reset."
                )
                self.state = "half-open"
            else:
                raise ConnectionError(f"Circuit breaker '{self.name}' is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time
            and datetime.now()
            > self.last_failure_time + timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        if self.state == "half-open":
            logger.info(
                f"CircuitBreaker '{self.name}' successfully reset. State is now closed."
            )
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        logger.warning(
            f"CircuitBreaker '{self.name}' recorded failure #{self.failure_count}."
        )
        if self.failure_count >= self.failure_threshold:
            if self.state != "open":
                logger.error(
                    f"CircuitBreaker '{self.name}' has opened due to reaching failure threshold of {self.failure_threshold}."
                )
                self.state = "open"
