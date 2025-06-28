"""
Master Router for Sophia AI Platform

This module consolidates all API routes into a single router that can be
included in the main FastAPI application.
"""

from fastapi import APIRouter
from backend.api import (
    enhanced_ceo_chat_routes,
    simplified_llm_routes,
    unified_intelligence_routes,
    asana_integration_routes,
    codacy_integration_routes,
    cortex_routes,
    costar_routes,
    data_flow_routes,
    enhanced_cortex_routes,
    foundational_knowledge_routes,
    kb_management_routes,
    knowledge_dashboard_routes,
    large_data_import_routes,
    linear_integration_routes,
    llm_strategy_routes,
    notion_integration_routes,
    project_dashboard_routes,
    slack_linear_knowledge_routes,
    smart_ai_routes,
    snowflake_intelligence_routes,
    sophia_ai_phase1_routes,
    sophia_universal_chat_routes,
    unified_ai_routes,
    universal_chat_routes,
)


def create_application_router() -> APIRouter:
    """
    Create and configure all application routes.

    Returns:
        APIRouter: The master router with all endpoints configured
    """
    router = APIRouter()

    # CEO Dashboard Routes
    router.include_router(
        enhanced_ceo_chat_routes.router, prefix="/api/v1/ceo", tags=["CEO Dashboard"]
    )

    # LLM and AI Routes
    router.include_router(
        simplified_llm_routes.router, prefix="/api/v1/llm", tags=["LLM Strategy"]
    )
    router.include_router(
        llm_strategy_routes.router, prefix="/api/v1/llm-strategy", tags=["LLM Strategy"]
    )
    router.include_router(
        smart_ai_routes.router, prefix="/api/v1/smart-ai", tags=["Smart AI"]
    )

    # Unified Intelligence Routes
    router.include_router(
        unified_intelligence_routes.router,
        prefix="/api/unified-intelligence",
        tags=["Unified Intelligence"],
    )
    router.include_router(
        unified_ai_routes.router, prefix="/api/v1/unified-ai", tags=["Unified AI"]
    )

    # Integration Routes
    router.include_router(
        asana_integration_routes.router,
        prefix="/api/v1/asana",
        tags=["Asana Integration"],
    )
    router.include_router(
        codacy_integration_routes.router,
        prefix="/api/v1/codacy",
        tags=["Codacy Integration"],
    )
    router.include_router(
        linear_integration_routes.router,
        prefix="/api/v1/linear",
        tags=["Linear Integration"],
    )
    router.include_router(
        notion_integration_routes.router,
        prefix="/api/v1/notion",
        tags=["Notion Integration"],
    )

    # Cortex and AI Processing Routes
    router.include_router(
        cortex_routes.router, prefix="/api/v1/cortex", tags=["Cortex AI"]
    )
    router.include_router(
        enhanced_cortex_routes.router,
        prefix="/api/v1/enhanced-cortex",
        tags=["Enhanced Cortex"],
    )
    router.include_router(
        costar_routes.router, prefix="/api/v1/costar", tags=["COSTAR"]
    )

    # Data and Knowledge Management Routes
    router.include_router(
        data_flow_routes.router, prefix="/api/v1/data-flow", tags=["Data Flow"]
    )
    router.include_router(
        foundational_knowledge_routes.router,
        prefix="/api/v1/knowledge",
        tags=["Foundational Knowledge"],
    )
    router.include_router(
        kb_management_routes.router,
        prefix="/api/v1/kb",
        tags=["Knowledge Base Management"],
    )
    router.include_router(
        knowledge_dashboard_routes.router,
        prefix="/api/v1/knowledge-dashboard",
        tags=["Knowledge Dashboard"],
    )
    router.include_router(
        large_data_import_routes.router,
        prefix="/api/v1/data-import",
        tags=["Data Import"],
    )

    # Project and Dashboard Routes
    router.include_router(
        project_dashboard_routes.router,
        prefix="/api/v1/projects",
        tags=["Project Dashboard"],
    )
    router.include_router(
        slack_linear_knowledge_routes.router,
        prefix="/api/v1/slack-linear",
        tags=["Slack Linear Knowledge"],
    )

    # Snowflake Intelligence Routes
    router.include_router(
        snowflake_intelligence_routes.router,
        prefix="/api/v1/snowflake",
        tags=["Snowflake Intelligence"],
    )

    # Sophia AI Core Routes
    router.include_router(
        sophia_ai_phase1_routes.router,
        prefix="/api/v1/sophia",
        tags=["Sophia AI Phase 1"],
    )
    router.include_router(
        sophia_universal_chat_routes.router,
        prefix="/api/v1/chat",
        tags=["Sophia Universal Chat"],
    )
    router.include_router(
        universal_chat_routes.router,
        prefix="/api/v1/universal-chat",
        tags=["Universal Chat"],
    )

    return router
