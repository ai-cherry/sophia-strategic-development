"""
Prometheus Exporter for Autonomous Agents

Provides HTTP endpoint for Prometheus to scrape metrics from all running agents.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from aiohttp import web
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """
    HTTP server that exposes Prometheus metrics from autonomous agents
    
    Features:
    - Configurable port (default 9090)
    - Health check endpoint
    - Metrics endpoint with all agent metrics
    """
    
    def __init__(self):
        """Initialize Prometheus exporter"""
        self.port = int(get_config_value("PROMETHEUS_EXPORTER_PORT", "9090") or "9090")
        self.host = get_config_value("PROMETHEUS_EXPORTER_HOST", "0.0.0.0") or "0.0.0.0"
        
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"Prometheus exporter initialized on {self.host}:{self.port}")
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/metrics', self.metrics_handler)
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/', self.index_handler)
    
    async def start(self):
        """Start the HTTP server"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"Prometheus exporter started on http://{self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start Prometheus exporter: {e}")
            raise
    
    async def stop(self):
        """Stop the HTTP server"""
        try:
            if self.site:
                await self.site.stop()
            
            if self.runner:
                await self.runner.cleanup()
            
            logger.info("Prometheus exporter stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Prometheus exporter: {e}")
    
    async def metrics_handler(self, request: web.Request) -> web.Response:
        """
        Handle metrics endpoint request
        
        Returns all metrics from the Prometheus registry
        """
        try:
            # Generate metrics in Prometheus format
            metrics_data = generate_latest(REGISTRY)
            
            return web.Response(
                body=metrics_data,
                content_type=CONTENT_TYPE_LATEST
            )
            
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return web.Response(
                text=f"Error generating metrics: {e}",
                status=500
            )
    
    async def health_handler(self, request: web.Request) -> web.Response:
        """
        Handle health check endpoint
        
        Used by monitoring systems to verify service is running
        """
        return web.Response(
            text="OK",
            status=200
        )
    
    async def index_handler(self, request: web.Request) -> web.Response:
        """
        Handle root endpoint with basic information
        """
        html = """
        <html>
        <head><title>Sophia AI Autonomous Agents - Prometheus Exporter</title></head>
        <body>
            <h1>Sophia AI Autonomous Agents - Prometheus Exporter</h1>
            <p>Available endpoints:</p>
            <ul>
                <li><a href="/metrics">/metrics</a> - Prometheus metrics</li>
                <li><a href="/health">/health</a> - Health check</li>
            </ul>
            <p>Configure Prometheus to scrape metrics from: http://{host}:{port}/metrics</p>
        </body>
        </html>
        """.format(host=self.host if self.host != "0.0.0.0" else "localhost", port=self.port)
        
        return web.Response(
            text=html,
            content_type='text/html'
        )


class AgentMetricsCollector:
    """
    Collects and aggregates metrics from multiple agents
    
    This would be expanded to collect metrics from all running agents
    and provide a unified view for monitoring
    """
    
    def __init__(self):
        """Initialize metrics collector"""
        self.agents: Dict[str, Any] = {}
    
    def register_agent(self, agent_name: str, agent_instance: Any):
        """
        Register an agent for metrics collection
        
        Args:
            agent_name: Name of the agent
            agent_instance: Instance of the agent
        """
        self.agents[agent_name] = agent_instance
        logger.info(f"Registered agent for metrics collection: {agent_name}")
    
    def unregister_agent(self, agent_name: str):
        """
        Unregister an agent from metrics collection
        
        Args:
            agent_name: Name of the agent to unregister
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Unregistered agent from metrics collection: {agent_name}")
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get metrics from all registered agents
        
        Returns:
            Dictionary of metrics by agent name
        """
        metrics = {}
        
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'get_status'):
                    metrics[agent_name] = agent.get_status()
            except Exception as e:
                logger.error(f"Error collecting metrics from {agent_name}: {e}")
                metrics[agent_name] = {"error": str(e)}
        
        return metrics


# Global instances
exporter = PrometheusExporter()
collector = AgentMetricsCollector()


# For standalone testing
async def main():
    """Test the Prometheus exporter"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Start exporter
        await exporter.start()
        
        print(f"Prometheus exporter running on http://localhost:{exporter.port}")
        print("Press Ctrl+C to stop...")
        
        # Keep running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await exporter.stop()


if __name__ == "__main__":
    asyncio.run(main())
