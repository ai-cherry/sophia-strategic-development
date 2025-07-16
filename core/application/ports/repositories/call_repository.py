"""
Call Repository Interface

This module defines the interface for call data persistence.
This is a "port" in the hexagonal architecture.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.call import Call

class CallRepository(ABC):
    """
    Interface for call data persistence.

    This abstract class defines the contract that any call
    repository implementation must follow.
    """

    @abstractmethod
    async def get_by_id(self, call_id: str) -> Call | None:
        """
        Retrieve a call by its ID.

        Args:
            call_id: The unique identifier of the call

        Returns:
            Optional[Call]: The call if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_external_id(self, external_id: str) -> Call | None:
        """
        Retrieve a call by its external system ID (e.g., Gong ID).

        Args:
            external_id: The external system identifier

        Returns:
            Optional[Call]: The call if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_recent_calls(self, limit: int = 10, offset: int = 0) -> list[Call]:
        """
        Get recent calls ordered by scheduled date.

        Args:
            limit: Maximum number of calls to return
            offset: Number of calls to skip for pagination

        Returns:
            List[Call]: List of recent calls
        """
        pass

    @abstractmethod
    async def get_calls_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Call]:
        """
        Get calls within a specific date range.

        Args:
            start_date: Start of the date range
            end_date: End of the date range

        Returns:
            List[Call]: List of calls in the date range
        """
        pass

    @abstractmethod
    async def get_calls_requiring_followup(self) -> list[Call]:
        """
        Get all calls that require followup based on business rules.

        Returns:
            List[Call]: List of calls requiring followup
        """
        pass

    @abstractmethod
    async def save(self, call: Call) -> Call:
        """
        Persist a call.

        Args:
            call: The call to save

        Returns:
            Call: The saved call with any updates (e.g., generated ID)
        """
        pass

    @abstractmethod
    async def update(self, call: Call) -> Call:
        """
        Update an existing call.

        Args:
            call: The call with updated data

        Returns:
            Call: The updated call
        """
        pass

    @abstractmethod
    async def delete(self, call_id: str) -> bool:
        """
        Delete a call by ID.

        Args:
            call_id: The ID of the call to delete

        Returns:
            bool: True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def search_by_participant_email(self, email: str) -> list[Call]:
        """
        Search for calls by participant email.

        Args:
            email: The email address to search for

        Returns:
            List[Call]: List of calls with the participant
        """
        pass

    @abstractmethod
    async def get_high_value_calls(self) -> list[Call]:
        """
        Get all high-value calls based on business rules.

        Returns:
            List[Call]: List of high-value calls
        """
        pass

    @abstractmethod
    async def get_by_deal(self, deal_id: str) -> list[Call]:
        """
        Retrieve calls associated with a specific deal.

        Args:
            deal_id: The ID of the deal

        Returns:
            List[Call]: List of calls associated with the deal
        """
        pass
