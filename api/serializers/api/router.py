"""
Master Router for Sophia AI Platform

This module consolidates all API routes into a single router that can be
included in the main FastAPI application.
"""

import logging

logger = logging.getLogger(__name__)
from fastapi import APIRouter

logger = logging.getLogger(__name__)

from api import (
    ai_memory_health_routes,
    asana_integration_routes,
    ceo_dashboard_routes,
    codacy_integration_routes,
    deployment_status_routes,
    enhanced_cortex_routes,
    kb_management_routes,
    knowledge_dashboard_routes,
    lambda_labs_health_routes,
    large_data_import_routes,
    linear_integration_routes,
    llm_strategy_routes,
    notion_integration_routes,
    slack_linear_knowledge_routes,
    snowflake_intelligence_routes,
    sophia_universal_chat_routes,
    unified_health_routes,
)

# Import ephemeral credentials routes
from infrastructure.security.ephemeral_credentials.routes import (
    router as ephemeral_credentials_router,
)

# Import RBAC routes
from infrastructure.security.rbac.routes import router as rbac_router


def _setup_core_routes(router: APIRouter) -> None:
    """Setup core AI and chat routes"""
    router.include_router(
        enhanced_cortex_routes.router, prefix="/api/v1/cortex", tags=["cortex", "ai"]
    )
    router.include_router(
        sophia_universal_chat_routes.router, prefix="/api/v1/chat", tags=["chat", "ai"]
    )
    router.include_router(
        llm_strategy_routes.router, prefix="/api/v1/llm", tags=["llm", "ai"]
    )
    # Add Unified Dashboard routes
    router.include_router(
        ceo_dashboard_routes.router, tags=["ceo", "dashboard", "executive"]
    )


def _setup_integration_routes(router: APIRouter) -> None:
    """Setup third-party integration routes"""
    router.include_router(
        asana_integration_routes.router,
        prefix="/api/v1/integrations/asana",
        tags=["integrations", "asana"],
    )
    router.include_router(
        linear_integration_routes.router,
        prefix="/api/v1/integrations/linear",
        tags=["integrations", "linear"],
    )
    router.include_router(
        notion_integration_routes.router,
        prefix="/api/v1/integrations/notion",
        tags=["integrations", "notion"],
    )


def _setup_data_routes(router: APIRouter) -> None:
    """Setup data and analytics routes"""
    router.include_router(
        snowflake_intelligence_routes.router,
        prefix="/api/v1/intelligence",
        tags=["intelligence", "analytics"],
    )
    router.include_router(
        knowledge_dashboard_routes.router,
        prefix="/api/v1/knowledge",
        tags=["knowledge", "dashboard"],
    )
    router.include_router(
        large_data_import_routes.router, prefix="/api/v1/data", tags=["data", "import"]
    )


def _setup_admin_routes(router: APIRouter) -> None:
    """Setup administrative and management routes"""
    router.include_router(
        kb_management_routes.router,
        prefix="/api/v1/kb",
        tags=["knowledge-base", "admin"],
    )
    router.include_router(
        slack_linear_knowledge_routes.router,
        prefix="/api/v1/slack-linear",
        tags=["slack", "linear", "knowledge"],
    )
    router.include_router(
        codacy_integration_routes.router,
        prefix="/api/v1/integrations/codacy",
        tags=["integrations", "codacy"],
    )


def _setup_monitoring_routes(router: APIRouter) -> None:
    """Setup monitoring and health check routes"""
    router.include_router(
        ai_memory_health_routes.router,
    )
    router.include_router(
        deployment_status_routes.router,
    )
    router.include_router(
        unified_health_routes.router,
    )
    router.include_router(
        lambda_labs_health_routes.router,
    )


def _setup_security_routes(router: APIRouter) -> None:
    """Setup security and access control routes"""
    router.include_router(
        rbac_router,
        tags=["security", "rbac", "access-control"],
    )
    router.include_router(
        ephemeral_credentials_router,
        tags=["security", "credentials", "access-control"],
    )


def create_application_router() -> APIRouter:
    """
    Create and configure the main application router with all endpoints

    Returns:
        APIRouter: Configured router with all application routes
    """
    router = APIRouter()

    # Setup route groups in logical order
    _setup_core_routes(router)
    _setup_integration_routes(router)
    _setup_data_routes(router)
    _setup_admin_routes(router)
    _setup_monitoring_routes(router)
    _setup_security_routes(router)  # Add security routes

    logger.info("✅ Application router created with all endpoints")
    return router
