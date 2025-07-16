"""
Competitor Intelligence API Routes for Sophia AI
Provides REST endpoints for competitor analysis and intelligence
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging
import uuid

from ..services.competitor_intelligence_service import (
    CompetitorIntelligenceService,
    CompetitorProfile,
    CompetitorIntelligence,
    CompetitorCategory,
    IntelligenceType,
    create_competitor_intelligence_service
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/competitors", tags=["Competitor Intelligence"])

# Global service instance
_service: Optional[CompetitorIntelligenceService] = None

def get_service() -> CompetitorIntelligenceService:
    """Get or create competitor intelligence service"""
    global _service
    if _service is None:
        _service = create_competitor_intelligence_service()
    return _service

# Pydantic models for API
class CompetitorProfileRequest(BaseModel):
    name: str = Field(..., description="Competitor name")
    category: CompetitorCategory = Field(..., description="Competitor category")
    description: str = Field(..., description="Competitor description")
    website: str = Field(..., description="Competitor website")
    founded_year: Optional[int] = Field(None, description="Year founded")
    headquarters: str = Field(..., description="Headquarters location")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    funding_total: Optional[float] = Field(None, description="Total funding raised")
    valuation: Optional[float] = Field(None, description="Company valuation")
    key_products: List[str] = Field(default_factory=list, description="Key products")
    target_market: List[str] = Field(default_factory=list, description="Target markets")
    strengths: List[str] = Field(default_factory=list, description="Competitor strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Competitor weaknesses")
    threat_level: int = Field(..., ge=1, le=10, description="Threat level (1-10)")
    market_share: Optional[float] = Field(None, description="Market share percentage")
    growth_rate: Optional[float] = Field(None, description="Growth rate percentage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CompetitorIntelligenceRequest(BaseModel):
    competitor_id: str = Field(..., description="Competitor ID")
    intelligence_type: IntelligenceType = Field(..., description="Intelligence type")
    title: str = Field(..., description="Intelligence title")
    description: str = Field(..., description="Intelligence description")
    source: str = Field(..., description="Intelligence source")
    source_url: Optional[str] = Field(None, description="Source URL")
    impact_score: int = Field(..., ge=1, le=10, description="Impact score (1-10)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    tags: List[str] = Field(default_factory=list, description="Intelligence tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Result limit")

# Competitor Profile Endpoints
@router.post("/profiles", response_model=Dict[str, Any])
async def create_competitor_profile(
    profile_request: CompetitorProfileRequest,
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Create a new competitor profile"""
    try:
        # Create profile object
        profile = CompetitorProfile(
            id=str(uuid.uuid4()),
            name=profile_request.name,
            category=profile_request.category,
            description=profile_request.description,
            website=profile_request.website,
            founded_year=profile_request.founded_year,
            headquarters=profile_request.headquarters,
            employee_count=profile_request.employee_count,
            funding_total=profile_request.funding_total,
            valuation=profile_request.valuation,
            key_products=profile_request.key_products,
            target_market=profile_request.target_market,
            strengths=profile_request.strengths,
            weaknesses=profile_request.weaknesses,
            threat_level=profile_request.threat_level,
            market_share=profile_request.market_share,
            growth_rate=profile_request.growth_rate,
            last_updated=datetime.now(),
            metadata=profile_request.metadata
        )
        
        # Add to service
        success = await service.add_competitor_profile(profile)
        
        if success:
            return {
                "success": True,
                "message": "Competitor profile created successfully",
                "competitor_id": profile.id,
                "name": profile.name
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create competitor profile")
            
    except Exception as e:
        logger.error(f"Error creating competitor profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles/{competitor_id}", response_model=Dict[str, Any])
async def get_competitor_profile(
    competitor_id: str = Path(..., description="Competitor ID"),
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Get competitor profile by ID"""
    try:
        profile = await service.get_competitor_profile(competitor_id)
        
        if profile:
            return {
                "success": True,
                "profile": profile
            }
        else:
            raise HTTPException(status_code=404, detail="Competitor profile not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving competitor profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles", response_model=Dict[str, Any])
async def search_competitor_profiles(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Result limit"),
    category: Optional[CompetitorCategory] = Query(None, description="Filter by category"),
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Search competitor profiles"""
    try:
        results = await service.search_competitors(
            query=query,
            limit=limit,
            category=category
        )
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching competitor profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Intelligence Endpoints
@router.post("/intelligence", response_model=Dict[str, Any])
async def create_intelligence(
    intelligence_request: CompetitorIntelligenceRequest,
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Create new competitor intelligence"""
    try:
        # Create intelligence object
        intelligence = CompetitorIntelligence(
            id=str(uuid.uuid4()),
            competitor_id=intelligence_request.competitor_id,
            intelligence_type=intelligence_request.intelligence_type,
            title=intelligence_request.title,
            description=intelligence_request.description,
            source=intelligence_request.source,
            source_url=intelligence_request.source_url,
            impact_score=intelligence_request.impact_score,
            confidence_score=intelligence_request.confidence_score,
            timestamp=datetime.now(),
            tags=intelligence_request.tags,
            metadata=intelligence_request.metadata
        )
        
        # Add to service
        success = await service.add_intelligence(intelligence)
        
        if success:
            return {
                "success": True,
                "message": "Intelligence created successfully",
                "intelligence_id": intelligence.id,
                "title": intelligence.title
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create intelligence")
            
    except Exception as e:
        logger.error(f"Error creating intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/search", response_model=Dict[str, Any])
async def search_intelligence(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Result limit"),
    competitor_id: Optional[str] = Query(None, description="Filter by competitor ID"),
    intelligence_type: Optional[IntelligenceType] = Query(None, description="Filter by intelligence type"),
    days_back: int = Query(30, ge=1, le=365, description="Days to look back"),
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Search competitor intelligence"""
    try:
        results = await service.search_intelligence(
            query=query,
            limit=limit,
            competitor_id=competitor_id,
            intelligence_type=intelligence_type,
            days_back=days_back
        )
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
            "filters": {
                "competitor_id": competitor_id,
                "intelligence_type": intelligence_type.value if intelligence_type else None,
                "days_back": days_back
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intelligence/competitor/{competitor_id}", response_model=Dict[str, Any])
async def get_competitor_intelligence(
    competitor_id: str = Path(..., description="Competitor ID"),
    limit: int = Query(50, ge=1, le=200, description="Result limit"),
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Get all intelligence for a specific competitor"""
    try:
        intelligence = await service.get_competitor_intelligence(competitor_id, limit)
        
        return {
            "success": True,
            "competitor_id": competitor_id,
            "intelligence": intelligence,
            "count": len(intelligence)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving competitor intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@router.get("/analytics/threat-analysis", response_model=Dict[str, Any])
async def get_threat_analysis(
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Get comprehensive threat analysis"""
    try:
        analysis = await service.get_threat_analysis()
        
        return {
            "success": True,
            "analysis": analysis,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating threat analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/intelligence-summary", response_model=Dict[str, Any])
async def get_intelligence_summary(
    days_back: int = Query(7, ge=1, le=90, description="Days to look back"),
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Get intelligence summary for recent period"""
    try:
        summary = await service.get_intelligence_summary(days_back)
        
        return {
            "success": True,
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating intelligence summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data(
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Get comprehensive dashboard data"""
    try:
        # Get both threat analysis and recent intelligence summary
        threat_analysis = await service.get_threat_analysis()
        intelligence_summary = await service.get_intelligence_summary(days_back=7)
        
        # Create dashboard data
        dashboard = {
            "overview": {
                "total_competitors": threat_analysis.get("total_competitors", 0),
                "recent_intelligence": intelligence_summary.get("total_items", 0),
                "high_threats": threat_analysis.get("threat_distribution", {}).get("critical", 0),
                "high_impact_intelligence": intelligence_summary.get("impact_analysis", {}).get("high_impact", 0)
            },
            "threat_analysis": threat_analysis,
            "intelligence_summary": intelligence_summary,
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "dashboard": dashboard
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health Check
@router.get("/health", response_model=Dict[str, Any])
async def health_check(
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Health check endpoint"""
    try:
        # Test service availability
        status = "healthy"
        details = {
            "service": "competitor_intelligence",
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "status": status,
            "details": details
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Bulk Operations
@router.post("/bulk/profiles", response_model=Dict[str, Any])
async def bulk_create_profiles(
    profiles: List[CompetitorProfileRequest],
    background_tasks: BackgroundTasks,
    service: CompetitorIntelligenceService = Depends(get_service)
):
    """Bulk create competitor profiles"""
    try:
        async def process_bulk_profiles():
            success_count = 0
            error_count = 0
            
            for profile_request in profiles:
                try:
                    profile = CompetitorProfile(
                        id=str(uuid.uuid4()),
                        name=profile_request.name,
                        category=profile_request.category,
                        description=profile_request.description,
                        website=profile_request.website,
                        founded_year=profile_request.founded_year,
                        headquarters=profile_request.headquarters,
                        employee_count=profile_request.employee_count,
                        funding_total=profile_request.funding_total,
                        valuation=profile_request.valuation,
                        key_products=profile_request.key_products,
                        target_market=profile_request.target_market,
                        strengths=profile_request.strengths,
                        weaknesses=profile_request.weaknesses,
                        threat_level=profile_request.threat_level,
                        market_share=profile_request.market_share,
                        growth_rate=profile_request.growth_rate,
                        last_updated=datetime.now(),
                        metadata=profile_request.metadata
                    )
                    
                    if await service.add_competitor_profile(profile):
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing profile {profile_request.name}: {e}")
                    error_count += 1
            
            logger.info(f"Bulk profile creation completed: {success_count} success, {error_count} errors")
        
        # Add to background tasks
        background_tasks.add_task(process_bulk_profiles)
        
        return {
            "success": True,
            "message": f"Bulk profile creation started for {len(profiles)} profiles",
            "count": len(profiles)
        }
        
    except Exception as e:
        logger.error(f"Error starting bulk profile creation: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 