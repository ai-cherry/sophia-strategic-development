#!/usr/bin/env python3
"""
Sophia AI Status Dashboard
Comprehensive view of all MCP servers and services
"""

import asyncio
import aiohttp
from aiohttp import web
import json

class StatusDashboard:
    def __init__(self):
        self.app = web.Application()
        self._setup_routes()
        self.services = {
            "sophia-backend": "http://localhost:8000",
            "mcp-gateway": "http://localhost:8090", 
            "pulumi-mcp": "http://localhost:3001",
            "github-mcp": "http://localhost:3002",
            "slack-mcp": "http://localhost:3004",
            "ai-integration": "http://localhost:8001"
        }
    
    def _setup_routes(self):
        self.app.router.add_get('/', self.dashboard)
        self.app.router.add_get('/status', self.get_status)
        self.app.router.add_get('/health', self.health_check)
    
    async def dashboard(self, request):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sophia AI - MCP Status Dashboard</title>
            <style>
                body { font-family: Arial; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .service-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .service-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .status-healthy { color: #28a745; }
                .status-error { color: #dc3545; }
                .refresh-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Sophia AI - MCP Gateway Dashboard</h1>
                    <p>Modern AI Orchestrator with Docker MCP Catalog Integration</p>
                </div>
                
                <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Status</button>
                
                <div id="services" class="service-grid">
                    <!-- Services loaded via JavaScript -->
                </div>
            </div>
            
            <script>
                async function loadStatus() {
                    try {
                        const response = await fetch('/status');
                        const data = await response.json();
                        const container = document.getElementById('services');
                        
                        container.innerHTML = '';
                        
                        for (const [name, status] of Object.entries(data.services)) {
                            const card = document.createElement('div');
                            card.className = 'service-card';
                            
                            const statusClass = status.healthy ? 'status-healthy' : 'status-error';
                            const statusIcon = status.healthy ? '✅' : '❌';
                            
                            card.innerHTML = `
                                <h3>${statusIcon} ${name}</h3>
                                <p><strong>Status:</strong> <span class="${statusClass}">${status.healthy ? 'Healthy' : 'Error'}</span></p>
                                <p><strong>URL:</strong> ${status.url}</p>
                                <p><strong>Response Time:</strong> ${status.response_time || 'N/A'}</p>
                                ${status.capabilities ? `<p><strong>Capabilities:</strong> ${status.capabilities.join(', ')}</p>` : ''}
                            `;
                            
                            container.appendChild(card);
                        }
                    } catch (error) {
                        console.error('Failed to load status:', error);
                    }
                }
                
                loadStatus();
                setInterval(loadStatus, 30000); // Refresh every 30 seconds
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def get_status(self, request):
        status = {"services": {}}
        
        async with aiohttp.ClientSession() as session:
            for name, url in self.services.items():
                try:
                    start_time = asyncio.get_event_loop().time()
                    async with session.get(f"{url}/health", timeout=5) as resp:
                        end_time = asyncio.get_event_loop().time()
                        response_time = f"{(end_time - start_time) * 1000:.2f}ms"
                        
                        if resp.status == 200:
                            data = await resp.json()
                            status["services"][name] = {
                                "healthy": True,
                                "url": url,
                                "response_time": response_time,
                                "capabilities": data.get("capabilities", [])
                            }
                        else:
                            status["services"][name] = {
                                "healthy": False,
                                "url": url,
                                "response_time": response_time,
                                "error": f"HTTP {resp.status}"
                            }
                except Exception as e:
                    status["services"][name] = {
                        "healthy": False,
                        "url": url,
                        "error": str(e)
                    }
        
        return web.json_response(status)
    
    async def health_check(self, request):
        return web.json_response({
            "status": "healthy",
            "service": "Sophia AI Status Dashboard"
        })

async def main():
    dashboard = StatusDashboard()
    runner = web.AppRunner(dashboard.app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print("✅ Status Dashboard running on http://localhost:8080")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
