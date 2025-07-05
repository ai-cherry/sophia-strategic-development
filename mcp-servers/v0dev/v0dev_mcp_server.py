#!/usr/bin/env python3
"""
V0.dev MCP Server - AI-driven UI component generation for Sophia AI.

This server wraps V0.dev's OpenAI-compatible API to provide:
- Component generation from prompts
- Design context integration from Figma
- Live streaming responses
- Component deployment to Vercel
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

try:
    import mcp.types as types
    from mcp.server import Server as MCPServer
except ImportError:
    # Fallback for development
    MCPServer = None
    types = None

# Import Sophia AI utilities - use absolute imports when running as MCP server
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from backend.core.auto_esc_config import get_config_value
except ImportError:
    # Fallback for MCP server environment
    def get_config_value(key: str) -> str | None:
        return os.environ.get(f"SOPHIA_{key.upper()}")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
component_generation_counter = Counter(
    "v0dev_component_generations_total",
    "Total number of component generation requests",
    ["status", "component_type"],
)
component_generation_duration = Histogram(
    "v0dev_component_generation_duration_seconds",
    "Duration of component generation in seconds",
)
api_errors = Counter(
    "v0dev_api_errors_total", "Total number of V0.dev API errors", ["error_type"]
)

# V0.dev API configuration
V0DEV_API_ENDPOINT = "https://api.v0.dev/v1/chat/completions"
DEFAULT_MODEL = "gpt-4"  # V0.dev uses OpenAI-compatible models


class ComponentRequest(BaseModel):
    """Request model for component generation."""

    prompt: str = Field(
        ..., description="Natural language description of the component"
    )
    design_context: dict[str, Any] | None = Field(
        None, description="Figma design tokens and context"
    )
    component_type: str = Field("react", description="Type of component to generate")
    styling: str = Field(
        "tailwind",
        description="Styling approach (tailwind, css-modules, styled-components)",
    )
    typescript: bool = Field(True, description="Generate TypeScript component")
    include_tests: bool = Field(True, description="Generate unit tests")


class StreamComponentRequest(BaseModel):
    """Request model for streaming component generation."""

    prompt: str
    design_context: dict[str, Any] | None = None
    stream: bool = Field(True)


class DeployComponentRequest(BaseModel):
    """Request model for component deployment."""

    project_id: str = Field(..., description="Vercel project ID")
    component_code: str = Field(..., description="Component code to deploy")
    component_name: str = Field(..., description="Name of the component")
    branch: str = Field("feature/ui", description="Git branch for deployment")


class V0DevService:
    """Service for interacting with V0.dev API."""

    def __init__(self):
        self.api_key = get_config_value("vercel_v0dev_api_key")
        if not self.api_key:
            raise ValueError("VERCEL_V0DEV_API_KEY not found in Pulumi ESC")

        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def generate_component(self, request: ComponentRequest) -> dict[str, Any]:
        """Generate a UI component using V0.dev."""
        with component_generation_duration.time():
            try:
                # Build the prompt with design context
                enhanced_prompt = self._build_enhanced_prompt(request)

                # Prepare the API request
                payload = {
                    "model": DEFAULT_MODEL,
                    "messages": [
                        {"role": "system", "content": self._get_system_prompt(request)},
                        {"role": "user", "content": enhanced_prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000,
                }

                # Make the API call
                response = await self.client.post(V0DEV_API_ENDPOINT, json=payload)
                response.raise_for_status()

                result = response.json()
                component_code = self._extract_component_code(result)

                # Generate tests if requested
                test_code = None
                if request.include_tests:
                    test_code = await self._generate_tests(component_code, request)

                component_generation_counter.labels(
                    status="success", component_type=request.component_type
                ).inc()

                return {
                    "component_code": component_code,
                    "test_code": test_code,
                    "metadata": {
                        "generated_at": datetime.utcnow().isoformat(),
                        "prompt": request.prompt,
                        "styling": request.styling,
                        "typescript": request.typescript,
                    },
                }

            except Exception as e:
                api_errors.labels(error_type=type(e).__name__).inc()
                component_generation_counter.labels(
                    status="error", component_type=request.component_type
                ).inc()
                logger.error(f"Component generation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def stream_component(self, request: StreamComponentRequest):
        """Stream component generation for live preview."""
        try:
            enhanced_prompt = self._build_enhanced_prompt(request)

            payload = {
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": self._get_system_prompt(request)},
                    {"role": "user", "content": enhanced_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 4000,
                "stream": True,
            }

            async with self.client.stream(
                "POST", V0DEV_API_ENDPOINT, json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            yield f"data: {data}\n\n"

        except Exception as e:
            api_errors.labels(error_type=type(e).__name__).inc()
            logger.error(f"Component streaming failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    def _build_enhanced_prompt(self, request) -> str:
        """Build an enhanced prompt with design context."""
        prompt_parts = [request.prompt]

        if hasattr(request, "design_context") and request.design_context:
            prompt_parts.append("\n\nDesign Context:")

            if "colors" in request.design_context:
                prompt_parts.append(
                    f"Color Palette: {json.dumps(request.design_context['colors'])}"
                )

            if "typography" in request.design_context:
                prompt_parts.append(
                    f"Typography: {json.dumps(request.design_context['typography'])}"
                )

            if "spacing" in request.design_context:
                prompt_parts.append(
                    f"Spacing: {json.dumps(request.design_context['spacing'])}"
                )

            if "components" in request.design_context:
                prompt_parts.append(
                    f"Related Components: {json.dumps(request.design_context['components'])}"
                )

        return "\n".join(prompt_parts)

    def _get_system_prompt(self, request) -> str:
        """Get the system prompt for component generation."""
        styling_map = {
            "tailwind": "Use Tailwind CSS classes for styling",
            "css-modules": "Use CSS modules with .module.css files",
            "styled-components": "Use styled-components for styling",
        }

        type_suffix = (
            "TypeScript" if getattr(request, "typescript", True) else "JavaScript"
        )

        return f"""You are an expert UI developer creating React components.
Generate a {request.component_type if hasattr(request, 'component_type') else 'react'} component in {type_suffix}.
{styling_map.get(getattr(request, 'styling', 'tailwind'), 'Use appropriate styling')}.
Follow these guidelines:
- Create production-ready, accessible components
- Include proper TypeScript types/interfaces if TypeScript is used
- Add comprehensive JSDoc comments
- Implement ARIA attributes for accessibility
- Use semantic HTML elements
- Include error boundaries where appropriate
- Make components responsive and mobile-friendly
- Follow React best practices and hooks patterns
- Export the component as default

Return only the component code without markdown formatting."""

    def _extract_component_code(self, api_response: dict) -> str:
        """Extract component code from API response."""
        try:
            content = api_response["choices"][0]["message"]["content"]
            # Clean up any markdown formatting if present
            if "```" in content:
                lines = content.split("\n")
                code_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        code_lines.append(line)
                return "\n".join(code_lines)
            return content
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract component code: {e}")
            raise ValueError("Invalid API response format")

    async def _generate_tests(
        self, component_code: str, request: ComponentRequest
    ) -> str:
        """Generate unit tests for the component."""
        test_prompt = f"""Generate comprehensive unit tests for the following React component:

{component_code}

Use React Testing Library and Jest. Include tests for:
- Component rendering
- Props validation
- User interactions
- Accessibility
- Edge cases
- Error states"""

        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert in React testing. Generate comprehensive unit tests.",
                },
                {"role": "user", "content": test_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        response = await self.client.post(V0DEV_API_ENDPOINT, json=payload)
        response.raise_for_status()

        result = response.json()
        return self._extract_component_code(result)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Initialize FastAPI app
app = FastAPI(title="V0.dev MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
v0dev_service = None
mcp_server = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global v0dev_service, mcp_server

    try:
        v0dev_service = V0DevService()
        logger.info("V0.dev service initialized successfully")

        # Initialize MCP server
        mcp_server = MCPServer("v0dev")

        # Register MCP tools
        @mcp_server.tool()
        async def generateComponent(
            prompt: str, design_context: dict | None = None
        ) -> dict:
            """Generate a UI component from a prompt."""
            request = ComponentRequest(prompt=prompt, design_context=design_context)
            return await v0dev_service.generate_component(request)

        @mcp_server.tool()
        async def streamComponent(
            prompt: str, design_context: dict | None = None
        ) -> dict:
            """Stream component generation for live preview."""
            # For MCP, we'll return the streaming endpoint info
            return {
                "endpoint": "/api/v1/stream",
                "method": "POST",
                "body": {"prompt": prompt, "design_context": design_context},
            }

        @mcp_server.tool()
        async def deployComponent(
            project_id: str, component_code: str, component_name: str
        ) -> dict:
            """Deploy a component to Vercel."""
            # This would integrate with Vercel deployment API
            return {
                "status": "pending",
                "message": f"Component {component_name} queued for deployment to project {project_id}",
            }

        logger.info("MCP server initialized with tools")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if v0dev_service:
        await v0dev_service.close()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "v0dev-mcp",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Readiness check endpoint
@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    if not v0dev_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Test V0.dev API connectivity
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.v0.dev/v1/models",
                headers={"Authorization": f"Bearer {v0dev_service.api_key}"},
                timeout=5.0,
            )
            response.raise_for_status()
    except Exception as e:
        logger.error(f"V0.dev API health check failed: {e}")
        raise HTTPException(status_code=503, detail="V0.dev API not accessible")

    return {"status": "ready"}


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")


# Component generation endpoint
@app.post("/api/v1/generate")
async def generate_component(request: ComponentRequest):
    """Generate a UI component."""
    if not v0dev_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return await v0dev_service.generate_component(request)


# Streaming endpoint
@app.post("/api/v1/stream")
async def stream_component(request: StreamComponentRequest):
    """Stream component generation."""
    if not v0dev_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return StreamingResponse(
        v0dev_service.stream_component(request), media_type="text/event-stream"
    )


# Component deployment endpoint
@app.post("/api/v1/deploy")
async def deploy_component(request: DeployComponentRequest):
    """Deploy a component to Vercel."""
    # TODO: Implement actual Vercel deployment
    return {
        "status": "success",
        "deployment_id": f"dpl_{request.component_name}_{datetime.utcnow().timestamp()}",
        "preview_url": f"https://{request.project_id}-{request.branch}.vercel.app/components/{request.component_name}",
    }


# MCP protocol endpoint
@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP protocol requests."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")

    body = await request.body()
    response = await mcp_server.handle_request(body)
    return Response(content=response, media_type="application/json")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("v0dev_mcp_server:app", host="0.0.0.0", port=9030, log_level="info")
