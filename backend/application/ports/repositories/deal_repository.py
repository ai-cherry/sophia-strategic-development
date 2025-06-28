"""
Deal Repository Interface

This module defines the repository interface for Deal entities.
This is a port in the hexagonal architecture.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from backend.domain.entities.deal import Deal, DealStage


class DealRepository(ABC):
    """
    Abstract repository interface for Deal entities.
    
    This interface defines the contract for data access operations
    related to deals. Concrete implementations will handle the actual
    persistence mechanism (e.g., database, API, etc.).
    """
    
    @abstractmethod
    async def get_by_id(self, deal_id: str) -> Optional[Deal]:
        """
        Retrieve a deal by its ID.
        
        Args:
            deal_id: The unique identifier of the deal
            
        Returns:
            Optional[Deal]: The deal if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_external_id(self, external_id: str) -> Optional[Deal]:
        """
        Retrieve a deal by its external ID (e.g., HubSpot ID).
        
        Args:
            external_id: The external identifier of the deal
            
        Returns:
            Optional[Deal]: The deal if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_owner(self, owner_id: str) -> List[Deal]:
        """
        Retrieve all deals owned by a specific user.
        
        Args:
            owner_id: The ID of the deal owner
            
        Returns:
            List[Deal]: List of deals owned by the user
        """
        pass
    
    @abstractmethod
    async def get_by_stage(self, stage: DealStage) -> List[Deal]:
        """
        Retrieve all deals in a specific stage.
        
        Args:
            stage: The deal stage to filter by
            
        Returns:
            List[Deal]: List of deals in the specified stage
        """
        pass
    
    @abstractmethod
    async def get_by_contact(self, contact_id: str) -> List[Deal]:
        """
        Retrieve all deals associated with a specific contact.
        
        Args:
            contact_id: The ID of the contact
            
        Returns:
            List[Deal]: List of deals associated with the contact
        """
        pass
    
    @abstractmethod
    async def get_closing_soon(self, days: int = 30) -> List[Deal]:
        """
        Retrieve deals expected to close within the specified number of days.
        
        Args:
            days: Number of days to look ahead (default: 30)
            
        Returns:
            List[Deal]: List of deals closing soon
        """
        pass
    
    @abstractmethod
    async def get_at_risk(self) -> List[Deal]:
        """
        Retrieve deals that are at risk based on business rules.
        
        Returns:
            List[Deal]: List of at-risk deals
        """
        pass
    
    @abstractmethod
    async def save(self, deal: Deal) -> Deal:
        """
        Save a deal (create or update).
        
        Args:
            deal: The deal to save
            
        Returns:
            Deal: The saved deal with updated metadata
        """
        pass
    
    @abstractmethod
    async def delete(self, deal_id: str) -> bool:
        """
        Delete a deal by its ID.
        
        Args:
            deal_id: The ID of the deal to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        owner_id: Optional[str] = None,
        stage: Optional[DealStage] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Deal]:
        """
        Search for deals based on various criteria.
        
        Args:
            query: Search query string
            owner_id: Filter by owner ID
            stage: Filter by deal stage
            min_amount: Minimum deal amount
            max_amount: Maximum deal amount
            start_date: Filter by close date start
            end_date: Filter by close date end
            limit: Maximum number of results
            
        Returns:
            List[Deal]: List of matching deals
        """
        pass
    
    @abstractmethod
    async def get_pipeline_summary(self, owner_id: Optional[str] = None) -> dict:
        """
        Get a summary of the deal pipeline.
        
        Args:
            owner_id: Optional filter by owner
            
        Returns:
            dict: Pipeline summary with counts and amounts by stage
        """
        pass
    
    @abstractmethod
    async def bulk_update_stage(self, deal_ids: List[str], new_stage: DealStage) -> int:
        """
        Update the stage for multiple deals.
        
        Args:
            deal_ids: List of deal IDs to update
            new_stage: The new stage to set
            
        Returns:
            int: Number of deals updated
        """
        pass 