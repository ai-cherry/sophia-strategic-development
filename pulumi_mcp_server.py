#!/usr/bin/env python3
"""
Sophia AI Pulumi MCP Server
Direct implementation of Pulumi MCP patterns
"""

import asyncio
import json
import logging
import subprocess
from aiohttp import web
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PulumiMCPServer:
    def __init__(self):
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/preview', self.pulumi_preview)
        self.app.router.add_post('/up', self.pulumi_up)
        self.app.router.add_post('/stack-output', self.stack_output)
        self.app.router.add_get('/list-resources', self.list_resources)
    
    async def health_check(self, request):
        return web.json_response({
            "status": "healthy",
            "service": "Pulumi MCP Server",
            "capabilities": ["preview", "up", "stack-output", "list-resources"]
        })
    
    async def pulumi_preview(self, request):
        try:
            data = await request.json()
            stack = data.get('stack', 'dev')
            
            # Execute pulumi preview
            result = subprocess.run(
                ['pulumi', 'preview', '--stack', stack, '--non-interactive'],
                cwd='./infrastructure',
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return web.json_response({
                "action": "preview",
                "stack": stack,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            })
        except Exception as e:
            return web.json_response({
                "error": f"Preview failed: {str(e)}"
            }, status=500)
    
    async def pulumi_up(self, request):
        try:
            data = await request.json()
            stack = data.get('stack', 'dev')
            
            # Execute pulumi up
            result = subprocess.run(
                ['pulumi', 'up', '--stack', stack, '--non-interactive', '--yes'],
                cwd='./infrastructure',
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return web.json_response({
                "action": "up",
                "stack": stack,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            })
        except Exception as e:
            return web.json_response({
                "error": f"Deployment failed: {str(e)}"
            }, status=500)
    
    async def stack_output(self, request):
        try:
            data = await request.json()
            stack = data.get('stack', 'dev')
            
            # Get stack outputs
            result = subprocess.run(
                ['pulumi', 'stack', 'output', '--json', '--stack', stack],
                cwd='./infrastructure',
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                outputs = json.loads(result.stdout) if result.stdout else {}
            else:
                outputs = {}
            
            return web.json_response({
                "action": "stack-output",
                "stack": stack,
                "success": result.returncode == 0,
                "outputs": outputs,
                "error": result.stderr if result.returncode != 0 else None
            })
        except Exception as e:
            return web.json_response({
                "error": f"Stack output failed: {str(e)}"
            }, status=500)
    
    async def list_resources(self, request):
        return web.json_response({
            "resources": [
                {
                    "type": "docker:index:Container",
                    "description": "Docker container resource"
                },
                {
                    "type": "aws:s3:Bucket", 
                    "description": "AWS S3 bucket resource"
                }
            ]
        })

async def main():
    server = PulumiMCPServer()
    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3001)
    await site.start()
    
    logger.info("✅ Pulumi MCP Server running on http://0.0.0.0:3001")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🔄 Shutting down Pulumi MCP Server...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
