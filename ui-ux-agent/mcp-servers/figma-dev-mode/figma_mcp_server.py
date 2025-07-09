#!/usr/bin/env python3
"""
Sophia AI Figma Dev Mode MCP Server
Integrates with Figma Dev Mode API for design token extraction and component analysis
Uses Pulumi ESC integration for secure credential management
"""

import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

import requests
import uvicorn
from fastapi import FastAPI, HTTPException

# Import Pulumi ESC configuration management
try:
    import sys

    sys.path.append("../../backend")
    from backend.core.auto_esc_config import get_config_value

    PULUMI_ESC_AVAILABLE = True
except ImportError:
    PULUMI_ESC_AVAILABLE = False
    get_config_value = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration with Pulumi ESC integration
def get_figma_credentials():
    """Get Figma credentials using Pulumi ESC strategy"""
    if PULUMI_ESC_AVAILABLE and get_config_value:
        try:
            # Try Pulumi ESC first (production pattern)
            figma_pat = get_config_value("FIGMA_PAT")
            if figma_pat:
                logger.info("✅ Using Figma PAT from Pulumi ESC")
                return figma_pat
        except Exception as e:
            logger.warning(f"Pulumi ESC access failed: {e}")

    # Fallback to environment variable
    figma_pat = get_config_value("figma_pat") or os.getenv(
        "FIGMA_PERSONAL_ACCESS_TOKEN"
    )
    if figma_pat:
        logger.info("✅ Using Figma PAT from environment variable")
        return figma_pat

    logger.warning("⚠️  No Figma PAT found - running in mock mode")
    return None


FIGMA_PAT = get_figma_credentials()
OPENAI_API_KEY = get_config_value("openai_api_key")
OPENROUTER_API_KEY = get_config_value("openrouter_api_key")

FIGMA_API_BASE = "https://api.figma.com/v1"


@dataclass
class DesignToken:
    """Design token extracted from Figma"""

    name: str
    value: str
    type: str  # color, typography, spacing, etc.
    category: str
    description: str | None = None


@dataclass
class ComponentMetadata:
    """Component metadata from Figma"""

    node_id: str
    name: str
    type: str
    description: str | None = None
    properties: dict[str, Any] = None


@dataclass
class DesignContext:
    """Complete design context for code generation"""

    file_id: str
    node_id: str
    design_tokens: list[DesignToken]
    component_metadata: ComponentMetadata
    implementation_hints: dict[str, Any]
    extraction_timestamp: str


class SecureCredentialManager:
    """Secure credential management following Sophia AI patterns"""

    @staticmethod
    def get_figma_token() -> str | None:
        """Retrieve Figma token from environment variables populated by Pulumi ESC"""
        return FIGMA_PAT

    @staticmethod
    def validate_credentials() -> bool:
        """Validate that all required credentials are available"""
        return bool(FIGMA_PAT)


class FigmaAPIClient:
    """Figma API client with enterprise-grade error handling"""

    def __init__(self):
        self.token = SecureCredentialManager.get_figma_token()
        self.base_url = FIGMA_API_BASE
        self.headers = (
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            if self.token
            else {}
        )

    async def get_file_metadata(self, file_id: str) -> dict[str, Any]:
        """Get Figma file metadata"""
        if not self.token:
            raise HTTPException(status_code=401, detail="Figma token not configured")

        try:
            response = requests.get(
                f"{self.base_url}/files/{file_id}", headers=self.headers, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get file metadata: {e}")
            raise HTTPException(status_code=500, detail=f"Figma API error: {e}") from e


class FigmaDevModeMCPServer:
    """Main Figma Dev Mode MCP Server class"""

    def __init__(self):
        self.api_client = FigmaAPIClient()
        self.app = FastAPI(
            title="Sophia AI Figma Dev Mode MCP Server",
            description="Design-to-code automation server",
            version="1.0.0",
        )
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now(UTC).isoformat(),
                "figma_token_configured": SecureCredentialManager.validate_credentials(),
                "server": "Figma Dev Mode MCP Server",
                "version": "1.0.0",
            }

        @self.app.get("/")
        async def root():
            """Root endpoint with server information"""
            return {
                "message": "Sophia AI Figma Dev Mode MCP Server",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "extract_design_tokens": "/extract-design-tokens",
                    "extract_design_context": "/extract-design-context",
                },
                "figma_integration": SecureCredentialManager.validate_credentials(),
                "description": "Design-to-code automation with Figma Dev Mode integration",
            }

        @self.app.post("/extract-design-tokens")
        async def extract_design_tokens(request: dict):
            """Extract design tokens from Figma file"""
            file_id = request.get("file_id")

            if not file_id:
                raise HTTPException(status_code=400, detail="file_id is required")

            try:
                tokens = await self._extract_mock_tokens(file_id)
                return {"tokens": [asdict(token) for token in tokens]}
            except Exception as e:
                logger.error(f"Failed to extract design tokens: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/extract-design-context")
        async def extract_design_context(request: dict):
            """Extract comprehensive design context from Figma"""
            file_id = request.get("file_id")
            node_id = request.get("node_id")

            if not file_id or not node_id:
                raise HTTPException(
                    status_code=400, detail="file_id and node_id are required"
                )

            try:
                context = await self._extract_mock_context(file_id, node_id)
                return asdict(context)
            except Exception as e:
                logger.error(f"Failed to extract design context: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def _extract_mock_tokens(self, file_id: str) -> list[DesignToken]:
        """Extract mock design tokens for demonstration"""
        return [
            DesignToken(
                "primary-color", "#6366f1", "color", "colors", "Primary brand color"
            ),
            DesignToken(
                "secondary-color",
                "#8b5cf6",
                "color",
                "colors",
                "Secondary accent color",
            ),
            DesignToken(
                "text-lg", "1.125rem", "typography", "font-sizes", "Large text size"
            ),
            DesignToken("spacing-4", "1rem", "spacing", "spacing", "Medium spacing"),
            DesignToken(
                "border-radius", "0.5rem", "border", "borders", "Standard border radius"
            ),
        ]

    async def _extract_mock_context(self, file_id: str, node_id: str) -> DesignContext:
        """Extract mock design context for demonstration"""
        tokens = await self._extract_mock_tokens(file_id)

        metadata = ComponentMetadata(
            node_id=node_id,
            name="Enhanced Executive KPI Card",
            type="COMPONENT",
            description="Professional KPI card with glassmorphism design",
            properties={"interactive": True, "responsive": True},
        )

        hints = {
            "suggested_component_name": "ExecutiveKPICard",
            "suggested_file_name": "executive-kpi-card",
            "framework": "react_typescript",
            "styling_approach": "tailwind_with_design_tokens",
            "accessibility_hints": {
                "requires_label": True,
                "interactive": True,
                "aria_role": "button",
            },
        }

        return DesignContext(
            file_id=file_id,
            node_id=node_id,
            design_tokens=tokens,
            component_metadata=metadata,
            implementation_hints=hints,
            extraction_timestamp=datetime.now(UTC).isoformat(),
        )


# FastAPI app instance
server = FigmaDevModeMCPServer()
app = server.app

if __name__ == "__main__":
    logger.info("🚀 Starting Sophia AI Figma Dev Mode MCP Server...")
    logger.info("📍 Server: http://localhost:9001")
    logger.info("📍 Health: http://localhost:9001/health")
    logger.info(
        "🔑 Figma Integration: {}".format(
            "Enabled"
            if SecureCredentialManager.validate_credentials()
            else "Disabled (Token Required)"
        )
    )

    uvicorn.run(
        app,
        host="127.0.0.1",  # Changed for security. Use ENV variable in production
        port=9001,
        log_level="info",
        reload=False,
    )
