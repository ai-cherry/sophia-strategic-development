"""
Foundational Knowledge API Routes
Extends the existing knowledge base system with Pay Ready's foundational business information
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.auth import get_current_user
from backend.services.foundational_knowledge_service import (
    FoundationalKnowledgeService, 
    FoundationalDataType
)
from backend.core.cache_manager import DashboardCacheManager
from backend.core.logger import logger

router = APIRouter(prefix="/api/v1/knowledge/foundational", tags=["foundational-knowledge"])

# Initialize services
foundational_service = FoundationalKnowledgeService()
cache_manager = DashboardCacheManager()


@router.post("/sync")
async def sync_foundational_data(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Sync foundational Pay Ready data from Snowflake to knowledge base
    
    This extends the existing knowledge base with:
    - Employee directory and organizational structure
    - Customer profiles and relationship data
    - Product catalog and competitive intelligence
    - Business processes and organizational values
    """
    try:
        # Check if user has admin permissions
        if not await _check_admin_permissions(user_id):
            raise HTTPException(status_code=403, detail="Admin permissions required")
        
        # Perform sync
        sync_result = await foundational_service.sync_foundational_data_to_knowledge_base()
        
        # Invalidate knowledge base cache
        await cache_manager.invalidate_pattern("knowledge_stats:*")
        await cache_manager.invalidate_pattern("foundational_*")
        
        logger.info(f"Foundational knowledge sync completed by {user_id}: {sync_result['synced_records']} records")
        
        return {
            "status": "success",
            "message": f"Synced {sync_result['synced_records']} foundational records to knowledge base",
            "details": sync_result
        }
        
    except Exception as e:
        logger.error(f"Foundational knowledge sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to sync foundational knowledge")


@router.get("/stats")
async def get_foundational_stats(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get statistics about foundational knowledge in the knowledge base
    
    Returns counts and metrics for each type of foundational data
    """
    try:
        # Use cache for stats
        cache_key = f"foundational_stats:{user_id}"
        
        async def fetch_stats():
            return await foundational_service.get_foundational_stats()
        
        stats = await cache_manager.get_or_set(
            cache_key,
            fetch_stats,
            ttl=300  # 5 minutes cache
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching foundational stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch foundational statistics")


@router.get("/search")
async def search_foundational_knowledge(
    query: str = Query(..., description="Search query"),
    data_types: Optional[List[str]] = Query(None, description="Filter by data types"),
    limit: int = Query(10, description="Maximum results to return"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Search foundational knowledge using semantic search
    
    Searches across all foundational data types or specific types:
    - employee: Team members and organizational structure
    - customer: Customer profiles and relationship data
    - product: Product catalog and features
    - competitor: Competitive intelligence
    - business_process: Business processes and procedures
    - organizational_value: Mission, vision, values
    - knowledge_article: Internal documentation
    """
    try:
        # Convert string data types to enum
        filtered_types = None
        if data_types:
            try:
                filtered_types = [FoundationalDataType(dt) for dt in data_types]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid data type: {str(e)}")
        
        # Perform search
        results = await foundational_service.search_foundational_knowledge(
            query=query,
            data_types=filtered_types,
            limit=limit
        )
        
        return {
            "query": query,
            "data_types_filter": data_types,
            "results": results,
            "total_results": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Foundational knowledge search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search foundational knowledge")


@router.get("/insights")
async def get_foundational_insights(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get AI-generated insights about foundational knowledge
    
    Provides business intelligence insights including:
    - Department composition and tenure analysis
    - Customer segment distribution and value
    - Competitive landscape assessment
    - Product portfolio performance
    """
    try:
        # Use cache for insights
        cache_key = f"foundational_insights:{user_id}"
        
        async def fetch_insights():
            return await foundational_service.generate_foundational_insights()
        
        insights = await cache_manager.get_or_set(
            cache_key,
            fetch_insights,
            ttl=3600  # 1 hour cache
        )
        
        return {
            "generated_at": datetime.now().isoformat(),
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error generating foundational insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate foundational insights")


@router.get("/data-types")
async def get_available_data_types(
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get available foundational data types and their descriptions
    """
    data_types = {
        "employee": {
            "name": "Employees",
            "description": "Team members, organizational structure, skills, and contact information",
            "fields": ["name", "department", "job_title", "skills", "email", "location"]
        },
        "customer": {
            "name": "Customers", 
            "description": "Customer profiles, industry data, relationship status, and business metrics",
            "fields": ["company_name", "industry", "segment", "tier", "revenue_range", "contact_info"]
        },
        "product": {
            "name": "Products & Services",
            "description": "Product catalog, features, pricing, and competitive positioning",
            "fields": ["product_name", "category", "pricing_model", "value_proposition", "features"]
        },
        "competitor": {
            "name": "Competitors",
            "description": "Competitive intelligence, market positioning, and win/loss analysis",
            "fields": ["company_name", "threat_level", "strengths", "weaknesses", "market_share"]
        },
        "business_process": {
            "name": "Business Processes",
            "description": "Standard operating procedures, workflows, and process documentation",
            "fields": ["process_name", "category", "steps", "tools", "owner", "documentation"]
        },
        "organizational_value": {
            "name": "Organizational Values",
            "description": "Mission, vision, core values, and organizational principles",
            "fields": ["value_name", "type", "statement", "description", "examples"]
        },
        "knowledge_article": {
            "name": "Knowledge Articles",
            "description": "Internal documentation, FAQs, and knowledge base articles",
            "fields": ["title", "category", "content", "keywords", "author", "visibility"]
        }
    }
    
    return {
        "data_types": data_types,
        "total_types": len(data_types)
    }


@router.put("/update/{data_type}/{record_id}")
async def update_foundational_record(
    data_type: str,
    record_id: str,
    updates: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Update a foundational knowledge record
    
    Updates both the source data in Snowflake and the knowledge base representation
    """
    try:
        # Check admin permissions
        if not await _check_admin_permissions(user_id):
            raise HTTPException(status_code=403, detail="Admin permissions required")
        
        # Validate data type
        try:
            foundational_type = FoundationalDataType(data_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid data type: {data_type}")
        
        # Perform update
        success = await foundational_service.update_foundational_record(
            record_id=record_id,
            data_type=foundational_type,
            updates=updates
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Record not found or update failed")
        
        # Invalidate cache
        await cache_manager.invalidate_pattern("foundational_*")
        await cache_manager.invalidate_pattern("knowledge_stats:*")
        
        return {
            "status": "success",
            "message": f"Updated {data_type} record {record_id}",
            "updated_fields": list(updates.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update foundational record: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update record")


@router.get("/context/{context_type}")
async def get_contextual_knowledge(
    context_type: str,
    context_id: Optional[str] = Query(None, description="Specific ID for context"),
    limit: int = Query(20, description="Maximum results to return"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get foundational knowledge relevant to a specific context
    
    Context types:
    - gong_call: Get relevant customer, product, and competitor info for a call
    - hubspot_deal: Get customer and product info for a deal
    - slack_conversation: Get relevant foundational context for discussions
    - employee_profile: Get comprehensive employee and team information
    """
    try:
        context_queries = {
            "gong_call": await _get_gong_call_context(context_id, limit),
            "hubspot_deal": await _get_hubspot_deal_context(context_id, limit),
            "slack_conversation": await _get_slack_context(context_id, limit),
            "employee_profile": await _get_employee_context(context_id, limit)
        }
        
        if context_type not in context_queries:
            raise HTTPException(status_code=400, detail=f"Invalid context type: {context_type}")
        
        results = context_queries[context_type]
        
        return {
            "context_type": context_type,
            "context_id": context_id,
            "results": results,
            "total_results": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contextual knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contextual knowledge")


# Helper functions

async def _check_admin_permissions(user_id: str) -> bool:
    """Check if user has admin permissions for foundational knowledge management"""
    # TODO: Implement proper role-based access control
    # For now, allow all authenticated users
    return True


async def _get_gong_call_context(call_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
    """Get foundational context relevant to a Gong call"""
    if not call_id:
        return []
    
    # Query for customer, product, and competitor information related to the call
    context_query = f"""
    SELECT DISTINCT
        fk.record_id,
        fk.data_type,
        fk.title,
        fk.description,
        fk.metadata
    FROM VW_COMPREHENSIVE_KNOWLEDGE_SEARCH fk
    JOIN STG_TRANSFORMED.STG_GONG_CALLS gc ON (
        (fk.KNOWLEDGE_TYPE = 'CUSTOMER' AND gc.HUBSPOT_COMPANY_ID = fk.metadata:hubspot_company_id::string) OR
        (fk.KNOWLEDGE_TYPE = 'PRODUCT' AND fk.record_id IN (
            SELECT DISTINCT VALUE 
            FROM TABLE(FLATTEN(gc.KEY_TOPICS)) 
            WHERE VALUE LIKE '%product%'
        ))
    )
    WHERE gc.CALL_ID = '{call_id}'
    LIMIT {limit}
    """
    
    # This would be executed through the foundational service
    # For now, return empty list
    return []


async def _get_hubspot_deal_context(deal_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
    """Get foundational context relevant to a HubSpot deal"""
    if not deal_id:
        return []
    
    # Similar implementation for HubSpot deal context
    return []


async def _get_slack_context(conversation_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
    """Get foundational context relevant to a Slack conversation"""
    if not conversation_id:
        return []
    
    # Similar implementation for Slack context
    return []


async def _get_employee_context(employee_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
    """Get comprehensive employee and team context"""
    if not employee_id:
        return []
    
    # Similar implementation for employee context
    return [] 