#!/usr/bin/env python3
"""
Sophia AI Figma Context MCP Server
Provides design integration and component extraction
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import sys
from pathlib import Path
from typing import Any, Optional

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

import httpx
from base.unified_standardized_base import (
    ServerConfig,
    ToolDefinition,
    ToolParameter,
)
from base.unified_standardized_base import (
    UnifiedStandardizedMCPServer as StandardizedMCPServer,
)

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class FigmaContextMCPServer(StandardizedMCPServer):
    """Figma Context MCP Server for design integration"""

    def __init__(self):
        config = ServerConfig(
            name="figma_context",
            version="1.0.0",
            port=9014,
            capabilities=["DESIGN", "COMPONENTS", "EXPORT"],
            tier="SECONDARY",
        )
        super().__init__(config)

        # Figma configuration
        self.api_key = get_config_value("figma_access_token")
        self.api_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": self.api_key,
            "Content-Type": "application/json",
        }

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define Figma Context tools"""
        return [
            ToolDefinition(
                name="get_file",
                description="Get Figma file information and structure",
                parameters=[
                    ToolParameter(
                        name="file_key",
                        type="string",
                        description="Figma file key",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_components",
                description="Get components from a Figma file",
                parameters=[
                    ToolParameter(
                        name="file_key",
                        type="string",
                        description="Figma file key",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="export_component",
                description="Export a component as code",
                parameters=[
                    ToolParameter(
                        name="file_key",
                        type="string",
                        description="Figma file key",
                        required=True,
                    ),
                    ToolParameter(
                        name="node_id",
                        type="string",
                        description="Node/component ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="format",
                        type="string",
                        description="Export format (react, vue, html)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_styles",
                description="Get design system styles from a file",
                parameters=[
                    ToolParameter(
                        name="file_key",
                        type="string",
                        description="Figma file key",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_images",
                description="Get images/assets from a Figma file",
                parameters=[
                    ToolParameter(
                        name="file_key",
                        type="string",
                        description="Figma file key",
                        required=True,
                    ),
                    ToolParameter(
                        name="node_ids",
                        type="array",
                        description="Specific node IDs to export",
                        required=False,
                    ),
                ],
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Figma Context tool calls"""

        if tool_name == "get_file":
            return await self._get_file(**arguments)
        elif tool_name == "get_components":
            return await self._get_components(**arguments)
        elif tool_name == "export_component":
            return await self._export_component(**arguments)
        elif tool_name == "get_styles":
            return await self._get_styles(**arguments)
        elif tool_name == "get_images":
            return await self._get_images(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _make_request(
        self, method: str, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a request to Figma API"""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.api_url}{endpoint}",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def _get_file(self, file_key: str) -> dict[str, Any]:
        """Get Figma file information"""

        result = await self._make_request("GET", f"/files/{file_key}")

        # Extract file info
        file_info = {
            "name": result.get("name", ""),
            "last_modified": result.get("lastModified", ""),
            "version": result.get("version", ""),
            "pages": [],
        }

        # Extract page structure
        document = result.get("document", {})
        for page in document.get("children", []):
            if page.get("type") == "CANVAS":
                file_info["pages"].append(
                    {
                        "id": page.get("id"),
                        "name": page.get("name"),
                        "children_count": len(page.get("children", [])),
                    }
                )

        return file_info

    async def _get_components(self, file_key: str) -> dict[str, Any]:
        """Get components from a Figma file"""

        # Get file data
        file_data = await self._make_request("GET", f"/files/{file_key}")

        # Extract components
        components = []

        def extract_components(node: dict[str, Any], path: str = ""):
            """Recursively extract components"""
            node_type = node.get("type", "")
            node_name = node.get("name", "")
            current_path = f"{path}/{node_name}" if path else node_name

            if node_type in ["COMPONENT", "COMPONENT_SET"]:
                components.append(
                    {
                        "id": node.get("id"),
                        "name": node_name,
                        "type": node_type,
                        "path": current_path,
                        "description": node.get("description", ""),
                    }
                )

            # Recurse through children
            for child in node.get("children", []):
                extract_components(child, current_path)

        # Start extraction from document
        document = file_data.get("document", {})
        extract_components(document)

        return {
            "file_key": file_key,
            "components": components,
            "count": len(components),
        }

    async def _export_component(
        self, file_key: str, node_id: str, format: str = "react"
    ) -> dict[str, Any]:
        """Export a component as code"""

        # Get node data
        node_data = await self._make_request(
            "GET", f"/files/{file_key}/nodes", {"ids": node_id}
        )

        nodes = node_data.get("nodes", {})
        if not nodes:
            return {"error": "Node not found"}

        node = list(nodes.values())[0]
        document = node.get("document", {})

        # Generate component code based on format
        if format == "react":
            code = self._generate_react_component(document)
        elif format == "vue":
            code = self._generate_vue_component(document)
        else:
            code = self._generate_html_component(document)

        return {
            "node_id": node_id,
            "format": format,
            "code": code,
            "component_name": document.get("name", "Component"),
        }

    def _generate_react_component(self, node: dict[str, Any]) -> str:
        """Generate React component from Figma node"""
        name = node.get("name", "Component").replace(" ", "")

        # Basic React component template
        code = f"""import React from 'react';

const {name} = () => {{
  return (
    <div className="{name.lower()}">
      {{/* Component content */}}
    </div>
  );
}};

export default {name};"""

        return code

    def _generate_vue_component(self, node: dict[str, Any]) -> str:
        """Generate Vue component from Figma node"""
        name = node.get("name", "Component").replace(" ", "")

        code = f"""<template>
  <div class="{name.lower()}">
    <!-- Component content -->
  </div>
</template>

<script>
export default {{
  name: '{name}'
}}
</script>

<style scoped>
.{name.lower()} {{
  /* Component styles */
}}
</style>"""

        return code

    def _generate_html_component(self, node: dict[str, Any]) -> str:
        """Generate HTML from Figma node"""
        name = node.get("name", "Component").replace(" ", "")

        code = f"""<div class="{name.lower()}">
  <!-- Component content -->
</div>

<style>
.{name.lower()} {{
  /* Component styles */
}}
</style>"""

        return code

    async def _get_styles(self, file_key: str) -> dict[str, Any]:
        """Get design system styles"""

        # Get file styles
        styles_data = await self._make_request("GET", f"/files/{file_key}/styles")

        meta = styles_data.get("meta", {})
        styles = meta.get("styles", [])

        # Organize styles by type
        style_categories = {
            "colors": [],
            "text": [],
            "effects": [],
            "grids": [],
        }

        for style in styles:
            style_type = style.get("style_type", "").lower()
            if style_type == "fill":
                style_categories["colors"].append(
                    {
                        "id": style.get("key"),
                        "name": style.get("name"),
                        "description": style.get("description", ""),
                    }
                )
            elif style_type == "text":
                style_categories["text"].append(
                    {
                        "id": style.get("key"),
                        "name": style.get("name"),
                        "description": style.get("description", ""),
                    }
                )
            elif style_type == "effect":
                style_categories["effects"].append(
                    {
                        "id": style.get("key"),
                        "name": style.get("name"),
                        "description": style.get("description", ""),
                    }
                )
            elif style_type == "grid":
                style_categories["grids"].append(
                    {
                        "id": style.get("key"),
                        "name": style.get("name"),
                        "description": style.get("description", ""),
                    }
                )

        return {
            "file_key": file_key,
            "styles": style_categories,
            "total_count": len(styles),
        }

    async def _get_images(
        self, file_key: str, node_ids: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Get images/assets from Figma"""

        params = {
            "format": "png",
            "scale": 2,
        }

        if node_ids:
            params["ids"] = ",".join(node_ids)

        # Get image URLs
        images_data = await self._make_request("GET", f"/images/{file_key}", params)

        images = images_data.get("images", {})

        return {
            "file_key": file_key,
            "images": [
                {"node_id": node_id, "url": url} for node_id, url in images.items()
            ],
            "count": len(images),
        }

# Create and run server
if __name__ == "__main__":
    server = FigmaContextMCPServer()
    server.run()
