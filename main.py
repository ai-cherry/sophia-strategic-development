#!/usr/bin/env python3
"""
Sophia AI - Distributed Enterprise AI Orchestration Platform
Main Application Entry Point

This is the canonical entry point for the Sophia AI distributed platform.
It handles instance detection, role-based service initialization, and
distributed architecture management across 4 Lambda Labs GPU instances.

Architecture:
- Primary K3s Cluster (GH200 96GB): Main orchestration and database
- MCP Orchestrator (A6000 48GB): AI orchestration and MCP servers  
- Data Pipeline (A100 40GB): Data processing and ML training
- Development Instance (A10 24GB): Testing and development

Author: Sophia AI Team
Date: July 2025
"""

import os
import sys
import asyncio
import logging
import signal
from pathlib import Path
from typing import Optional

# Set up structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sophia-ai.log') if not os.getenv('DISABLE_FILE_LOGGING') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Global variables for graceful shutdown
app_instance = None
shutdown_event = asyncio.Event()


def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        shutdown_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """
    Main entry point for Sophia AI distributed platform.
    
    This function handles:
    - Instance role detection
    - Service initialization based on role
    - Distributed service coordination
    - Graceful shutdown handling
    """
    global app_instance
    
    try:
        logger.info("🚀 Starting Sophia AI Distributed Enterprise Platform...")
        logger.info("📍 Entry Point: main.py (distributed architecture)")
        
        # Set up signal handlers
        setup_signal_handlers()
        
        # Import required modules
        try:
            from config.infrastructure import InfrastructureConfig, InstanceRole
            from services.service_discovery import ServiceDiscovery
            from utils.health_check import HealthChecker
            from api.main import create_app
            import uvicorn
        except ImportError as e:
            logger.error(f"❌ Failed to import required modules: {e}")
            logger.error("🔧 Please ensure all dependencies are installed via requirements.txt")
            sys.exit(1)
        
        # Determine current instance configuration
        current_instance = InfrastructureConfig.get_current_instance()
        if not current_instance:
            logger.error("❌ Unable to determine current instance configuration")
            logger.error("🔧 Please set CURRENT_INSTANCE_IP or INSTANCE_NAME environment variable")
            sys.exit(1)
        
        logger.info("🏗️ Instance Configuration:")
        logger.info(f"   📛 Name: {current_instance.name}")
        logger.info(f"   🌐 IP: {current_instance.ip}")
        logger.info(f"   🎯 Role: {current_instance.role.value}")
        logger.info(f"   🖥️ GPU: {current_instance.gpu}")
        logger.info(f"   🌍 Region: {current_instance.region}")
        logger.info(f"   🔌 Port Range: {current_instance.port_allocation.start}-{current_instance.port_allocation.end}")
        logger.info(f"   🛠️ Services: {[service.value for service in current_instance.services]}")
        
        # Initialize service discovery
        logger.info("🔍 Initializing service discovery...")
        service_discovery = ServiceDiscovery()
        await service_discovery.initialize()
        
        # Initialize health checker
        logger.info("🏥 Initializing health checker...")
        health_checker = HealthChecker()
        await health_checker.start_monitoring()
        
        # Create and configure app based on instance role
        logger.info(f"🔧 Creating application for role: {current_instance.role.value}")
        app_instance = create_app(current_instance)
        
        # Configure uvicorn based on instance role
        worker_count = 4 if current_instance.role == InstanceRole.PRIMARY else 2
        if current_instance.role == InstanceRole.DATA_PIPELINE:
            worker_count = 1  # Single worker for ML operations to avoid resource conflicts
        
        logger.info(f"🌐 Starting server on {current_instance.ip}:{current_instance.primary_port}")
        logger.info(f"👥 Workers: {worker_count}")
        
        # Configure uvicorn server
        config = uvicorn.Config(
            app=app_instance,
            host="0.0.0.0",
            port=current_instance.primary_port,
            workers=worker_count,
            log_level="info",
            access_log=True,
            reload=False,  # Production mode
            loop="asyncio",
            timeout_keep_alive=current_instance.timeout_seconds,
            limit_max_requests=current_instance.max_connections
        )
        
        server = uvicorn.Server(config)
        
        # Start server with graceful shutdown handling
        logger.info("✅ Sophia AI distributed instance started successfully")
        logger.info(f"🔗 Health endpoint: {current_instance.health_endpoint}")
        
        # Run server with shutdown handling
        try:
            await server.serve()
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt received")
        finally:
            # Graceful shutdown
            await shutdown_services(service_discovery, health_checker)
            
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        sys.exit(1)


async def shutdown_services(service_discovery, health_checker):
    """
    Gracefully shutdown all services.
    
    Args:
        service_discovery: Service discovery instance
        health_checker: Health checker instance
    """
    logger.info("🔄 Initiating graceful shutdown...")
    
    try:
        # Stop health monitoring
        if health_checker:
            await health_checker.shutdown()
            logger.info("✅ Health checker stopped")
        
        # Stop service discovery
        if service_discovery:
            await service_discovery.shutdown()
            logger.info("✅ Service discovery stopped")
        
        logger.info("✅ Graceful shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


async def create_application():
    """
    Create the FastAPI application instance for the current environment.
    
    This function provides an async interface for creating the app,
    useful for testing and programmatic usage.
    
    Returns:
        FastAPI: The configured application instance
    """
    try:
        from config.infrastructure import InfrastructureConfig
        from api.main import create_app
        
        # Determine current instance
        current_instance = InfrastructureConfig.get_current_instance()
        if not current_instance:
            # Fallback to development instance for testing
            from config.infrastructure import InstanceRole
            current_instance = InfrastructureConfig.get_instance_by_role(
                InstanceRole.DEVELOPMENT
            )
        
        if current_instance is None:
            raise RuntimeError("Unable to determine instance configuration")
        
        return create_app(current_instance)
        
    except Exception as e:
        logger.error(f"❌ Application creation failed: {e}")
        raise


def get_app():
    """
    Get the FastAPI application instance for ASGI servers.
    
    This function is called by ASGI servers like uvicorn when using
    the application programmatically (e.g., uvicorn main:app).
    
    Returns:
        FastAPI: The configured application instance
    """
    try:
        import asyncio
        
        # Create event loop if none exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Create application
        return loop.run_until_complete(create_application())
        
    except Exception as e:
        logger.error(f"❌ Failed to get app: {e}")
        raise


def validate_environment():
    """
    Validate the environment configuration.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    try:
        from config.infrastructure import InfrastructureConfig
        
        # Validate infrastructure configuration
        errors = InfrastructureConfig.validate_configuration()
        if errors:
            logger.error("❌ Infrastructure configuration validation failed:")
            for error in errors:
                logger.error(f"   - {error}")
            return False
        
        # Check current instance detection
        current_instance = InfrastructureConfig.get_current_instance()
        if not current_instance:
            logger.warning("⚠️ Unable to detect current instance, will use development mode")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Environment validation failed: {e}")
        return False


if __name__ == "__main__":
    # Validate environment before starting
    if not validate_environment():
        logger.error("❌ Environment validation failed, exiting")
        sys.exit(1)
    
    # Run the main application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Application terminated by user")
    except Exception as e:
        logger.error(f"❌ Application failed: {e}", exc_info=True)
        sys.exit(1)
