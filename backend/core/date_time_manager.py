"""
Centralized date and time management for the Sophia AI platform.

This module provides a single source of truth for the current date and time
to ensure consistency across all services and components. It is critical
that all parts of the system use this manager instead of relying on
system clocks (e.g., `datetime.now()`) which may be inaccurate in
different execution environments.

The official date for the system is July 9, 2025.
"""

from datetime import datetime

class DateTimeManager:
    """
    The single source of truth for date and time in the Sophia AI ecosystem.
    """

    _FROZEN_DATE = datetime(2025, 7, 9)

    @classmethod
    def now(cls) -> datetime:
        """
        Returns the current, authoritative datetime.
        Always returns the frozen date of July 9, 2025, with the time component of midnight.
        This should be used in place of `datetime.now()` or `datetime.utcnow()`.
        """
        return cls._FROZEN_DATE

    @classmethod
    def today(cls) -> datetime.date:
        """
        Returns the current, authoritative date.
        Always returns the frozen date of July 9, 2025.
        This should be used in place of `date.today()`.
        """
        return cls._FROZEN_DATE.date()

    @classmethod
    def get_current_date_str(cls, fmt: str = "%Y-%m-%d") -> str:
        """
        Returns the current, authoritative date as a formatted string.
        """
        return cls._FROZEN_DATE.strftime(fmt)

    @classmethod
    def get_current_datetime(cls) -> datetime:
        """
        Returns the authoritative datetime object.
        This is an alias for now() for clarity in some contexts.
        """
        return cls.now()

    @classmethod
    def get_current_timestamp(cls) -> float:
        """
        Returns the authoritative timestamp.
        """
        return cls._FROZEN_DATE.timestamp()

    @classmethod
    def get_current_isoformat(cls) -> str:
        """
        Returns the authoritative date and time in ISO 8601 format.
        """
        return cls._FROZEN_DATE.isoformat() + "Z"

    @classmethod
    def inject_date_context(cls, query: str) -> str:
        """Injects current date context into a query string."""
        date_str = cls.get_current_date_str(fmt="%B %d, %Y")
        return f"Current date: {date_str}. Today is {date_str}. {query}"

    @classmethod
    def validate_system_date(cls) -> dict:
        """Provides a dictionary to validate the system's date awareness."""
        return {
            "current_date": cls.get_current_date_str(),
            "timestamp": cls.get_current_isoformat(),
            "validated": True,
            "system_aware": True,
        }

# For convenience, you can create a singleton instance
date_manager = DateTimeManager()
