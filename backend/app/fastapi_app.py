# Import route modules
from backend.api import (
    asana_integration_routes,
    codacy_integration_routes,
    data_flow_routes,
    # llm_strategy_routes,
    notion_integration_routes,
    unified_routes,  # NEW: Single unified routes file
)

# Include routers
logger.info("Including API routers...")
app.include_router(unified_routes.router, tags=["Unified API"])  # NEW: Unified routes
app.include_router(asana_integration_routes.router, tags=["Asana"])
app.include_router(data_flow_routes.router, tags=["Data Flow"])
# app.include_router(llm_strategy_routes.router, tags=["LLM Strategy"])
app.include_router(notion_integration_routes.router, tags=["Notion"])
app.include_router(codacy_integration_routes.router, tags=["Codacy"])

# Remove old chat route imports - these are now in unified_routes
# app.include_router(unified_chat_routes.router, tags=["Chat"])
# app.include_router(enhanced_unified_chat_routes.router, tags=["Enhanced Chat"])
# app.include_router(unified_chat_routes_v2.router, tags=["Chat V2"])
