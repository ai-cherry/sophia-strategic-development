"""
Contact Repository Interface

This module defines the repository interface for Contact entities.
This is a port in the hexagonal architecture.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from backend.domain.entities.contact import Contact, ContactType, EngagementLevel


class ContactRepository(ABC):
    """
    Abstract repository interface for Contact entities.

    This interface defines the contract for data access operations
    related to contacts. Concrete implementations will handle the actual
    persistence mechanism (e.g., database, API, etc.).
    """

    @abstractmethod
    async def get_by_id(self, contact_id: str) -> Optional[Contact]:
        """
        Retrieve a contact by its ID.

        Args:
            contact_id: The unique identifier of the contact

        Returns:
            Optional[Contact]: The contact if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Contact]:
        """
        Retrieve a contact by email address.

        Args:
            email: The email address to search for

        Returns:
            Optional[Contact]: The contact if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_external_id(self, external_id: str) -> Optional[Contact]:
        """
        Retrieve a contact by its external ID (e.g., HubSpot ID).

        Args:
            external_id: The external identifier of the contact

        Returns:
            Optional[Contact]: The contact if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_company(self, company: str) -> List[Contact]:
        """
        Retrieve all contacts from a specific company.

        Args:
            company: The company name

        Returns:
            List[Contact]: List of contacts from the company
        """
        pass

    @abstractmethod
    async def get_by_type(self, contact_type: ContactType) -> List[Contact]:
        """
        Retrieve all contacts of a specific type.

        Args:
            contact_type: The type of contact to filter by

        Returns:
            List[Contact]: List of contacts of the specified type
        """
        pass

    @abstractmethod
    async def get_by_engagement_level(self, level: EngagementLevel) -> List[Contact]:
        """
        Retrieve all contacts with a specific engagement level.

        Args:
            level: The engagement level to filter by

        Returns:
            List[Contact]: List of contacts with the specified engagement level
        """
        pass

    @abstractmethod
    async def get_decision_makers(self, company: Optional[str] = None) -> List[Contact]:
        """
        Retrieve all contacts marked as decision makers.

        Args:
            company: Optional filter by company

        Returns:
            List[Contact]: List of decision maker contacts
        """
        pass

    @abstractmethod
    async def get_needing_nurture(self, days: int = 30) -> List[Contact]:
        """
        Retrieve contacts that need nurturing based on interaction history.

        Args:
            days: Number of days since last interaction (default: 30)

        Returns:
            List[Contact]: List of contacts needing nurture
        """
        pass

    @abstractmethod
    async def save(self, contact: Contact) -> Contact:
        """
        Save a contact (create or update).

        Args:
            contact: The contact to save

        Returns:
            Contact: The saved contact with updated metadata
        """
        pass

    @abstractmethod
    async def delete(self, contact_id: str) -> bool:
        """
        Delete a contact by its ID.

        Args:
            contact_id: The ID of the contact to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        company: Optional[str] = None,
        contact_type: Optional[ContactType] = None,
        engagement_level: Optional[EngagementLevel] = None,
        is_decision_maker: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Contact]:
        """
        Search for contacts based on various criteria.

        Args:
            query: Search query string
            company: Filter by company
            contact_type: Filter by contact type
            engagement_level: Filter by engagement level
            is_decision_maker: Filter by decision maker status
            tags: Filter by tags
            limit: Maximum number of results

        Returns:
            List[Contact]: List of matching contacts
        """
        pass

    @abstractmethod
    async def bulk_update_engagement(
        self, contact_ids: List[str], new_level: EngagementLevel
    ) -> int:
        """
        Update the engagement level for multiple contacts.

        Args:
            contact_ids: List of contact IDs to update
            new_level: The new engagement level to set

        Returns:
            int: Number of contacts updated
        """
        pass

    @abstractmethod
    async def get_by_deal(self, deal_id: str) -> List[Contact]:
        """
        Retrieve all contacts associated with a specific deal.

        Args:
            deal_id: The ID of the deal

        Returns:
            List[Contact]: List of contacts associated with the deal
        """
        pass

    @abstractmethod
    async def record_interaction(
        self, contact_id: str, interaction_type: str, notes: Optional[str] = None
    ) -> bool:
        """
        Record an interaction with a contact.

        Args:
            contact_id: The ID of the contact
            interaction_type: Type of interaction (e.g., 'email', 'call', 'meeting')
            notes: Optional notes about the interaction

        Returns:
            bool: True if recorded successfully
        """
        pass
