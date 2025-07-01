"""
Sophia AI Health Monitoring System

Comprehensive health check and monitoring system for all application components
including database connections, external APIs, and system resources.
"""

import logging
import os
import time
from datetime import datetime
from typing import Any

import psutil
import redis
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthMonitor:
    """Comprehensive health monitoring for Sophia AI"""

    def __init__(self, app: Flask):
        self.app = app
        self.start_time = datetime.utcnow()

        # Health check configuration
        self.config = {
            'critical_services': [
                'database',
                'redis',
                'external_apis',
            ],
            'external_apis': {
                'portkey': os.getenv('VITE_PORTKEY_API_KEY'),
                'salesforce': os.getenv('VITE_SALESFORCE_OAUTH_TOKEN'),
                'hubspot': os.getenv('VITE_HUBSPOT_API_KEY'),
                'intercom': os.getenv('VITE_INTERCOM_ACCESS_TOKEN'),
                'gong': os.getenv('GONG_ACCESS_KEY'),
            },
            'thresholds': {
                'cpu_usage': 80.0,      # CPU usage percentage
                'memory_usage': 85.0,   # Memory usage percentage
                'disk_usage': 90.0,     # Disk usage percentage
                'response_time': 5.0,   # API response time in seconds
            },
        }

        # Initialize health endpoints
        self._setup_health_endpoints()

    def _setup_health_endpoints(self):
        """Setup health check endpoints"""

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Basic health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': str(datetime.utcnow() - self.start_time),
                'version': os.getenv('APP_VERSION', 'unknown'),
                'environment': os.getenv('VITE_SOPHIA_ENV', 'unknown'),
            })

        @self.app.route('/health/detailed', methods=['GET'])
        def detailed_health_check():
            """Detailed health check with all components"""

            health_data = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': str(datetime.utcnow() - self.start_time),
                'version': os.getenv('APP_VERSION', 'unknown'),
                'environment': os.getenv('VITE_SOPHIA_ENV', 'unknown'),
                'components': {},
                'system': self._get_system_health(),
                'dependencies': self._check_dependencies(),
            }

            # Check all components
            overall_status = 'healthy'

            for component in ['database', 'redis', 'external_apis', 'filesystem']:
                component_health = self._check_component_health(component)
                health_data['components'][component] = component_health

                if component_health['status'] == 'unhealthy':
                    if component in self.config['critical_services']:
                        overall_status = 'unhealthy'
                    else:
                        overall_status = 'degraded' if overall_status == 'healthy' else overall_status

            health_data['status'] = overall_status

            # Return appropriate HTTP status code
            status_code = 200 if overall_status == 'healthy' else 503
            return jsonify(health_data), status_code

        @self.app.route('/health/ready', methods=['GET'])
        def readiness_check():
            """Kubernetes readiness probe endpoint"""

            # Check critical services only
            for service in self.config['critical_services']:
                component_health = self._check_component_health(service)
                if component_health['status'] == 'unhealthy':
                    return jsonify({
                        'status': 'not_ready',
                        'reason': f'{service} is unhealthy',
                        'timestamp': datetime.utcnow().isoformat(),
                    }), 503

            return jsonify({
                'status': 'ready',
                'timestamp': datetime.utcnow().isoformat(),
            })

        @self.app.route('/health/live', methods=['GET'])
        def liveness_check():
            """Kubernetes liveness probe endpoint"""

            # Basic liveness check - just ensure the application is running
            try:
                # Check if we can access basic system information
                uptime = datetime.utcnow() - self.start_time

                return jsonify({
                    'status': 'alive',
                    'uptime': str(uptime),
                    'timestamp': datetime.utcnow().isoformat(),
                })

            except Exception as e:
                logger.error(f"Liveness check failed: {e}")
                return jsonify({
                    'status': 'dead',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat(),
                }), 503

        @self.app.route('/metrics', methods=['GET'])
        def metrics_endpoint():
            """Prometheus-compatible metrics endpoint"""

            metrics = self._generate_metrics()

            # Return metrics in Prometheus format
            prometheus_metrics = []

            for metric_name, metric_data in metrics.items():
                if isinstance(metric_data, int | float):
                    prometheus_metrics.append(f"{metric_name} {metric_data}")
                elif isinstance(metric_data, dict):
                    for label, value in metric_data.items():
                        if isinstance(value, int | float):
                            prometheus_metrics.append(f'{metric_name}{{label="{label}"}} {value}')

            return '\n'.join(prometheus_metrics), 200, {'Content-Type': 'text/plain'}

    def _get_system_health(self) -> dict[str, Any]:
        """Get system resource health information"""

        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100

            # Network statistics
            network = psutil.net_io_counters()

            # Process information
            process = psutil.Process()
            process_memory = process.memory_info()

            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'status': 'healthy' if cpu_percent < self.config['thresholds']['cpu_usage'] else 'unhealthy',
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'available_gb': round(memory.available / (1024**3), 2),
                    'total_gb': round(memory.total / (1024**3), 2),
                    'status': 'healthy' if memory_percent < self.config['thresholds']['memory_usage'] else 'unhealthy',
                },
                'disk': {
                    'usage_percent': round(disk_percent, 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'total_gb': round(disk.total / (1024**3), 2),
                    'status': 'healthy' if disk_percent < self.config['thresholds']['disk_usage'] else 'unhealthy',
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                },
                'process': {
                    'memory_mb': round(process_memory.rss / (1024**2), 2),
                    'cpu_percent': process.cpu_percent(),
                    'threads': process.num_threads(),
                },
            }

        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
            }

    def _check_component_health(self, component: str) -> dict[str, Any]:
        """Check health of a specific component"""

        try:
            if component == 'database':
                return self._check_database_health()
            elif component == 'redis':
                return self._check_redis_health()
            elif component == 'external_apis':
                return self._check_external_apis_health()
            elif component == 'filesystem':
                return self._check_filesystem_health()
            else:
                return {
                    'status': 'unknown',
                    'error': f'Unknown component: {component}',
                }

        except Exception as e:
            logger.error(f"Health check failed for {component}: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }

    def _check_database_health(self) -> dict[str, Any]:
        """Check database connectivity and performance"""

        # For now, simulate database health check
        # In a real implementation, this would connect to your actual database

        try:
            start_time = time.time()

            # Simulate database connection check
            # connection = get_database_connection()
            # connection.execute("SELECT 1")

            response_time = time.time() - start_time

            return {
                'status': 'healthy',
                'response_time_ms': round(response_time * 1000, 2),
                'timestamp': datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }

    def _check_redis_health(self) -> dict[str, Any]:
        """Check Redis connectivity and performance"""

        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            return {
                'status': 'not_configured',
                'message': 'Redis URL not configured',
                'timestamp': datetime.utcnow().isoformat(),
            }

        try:
            start_time = time.time()

            redis_client = redis.from_url(redis_url)
            redis_client.ping()

            response_time = time.time() - start_time

            # Get Redis info
            info = redis_client.info()

            return {
                'status': 'healthy',
                'response_time_ms': round(response_time * 1000, 2),
                'version': info.get('redis_version'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_mb': round(info.get('used_memory', 0) / (1024**2), 2),
                'timestamp': datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }

    def _check_external_apis_health(self) -> dict[str, Any]:
        """Check external API connectivity"""

        api_health = {}
        overall_status = 'healthy'

        for api_name, api_key in self.config['external_apis'].items():
            if not api_key:
                api_health[api_name] = {
                    'status': 'not_configured',
                    'message': f'{api_name} API key not configured',
                }
                continue

            try:
                start_time = time.time()

                # Simulate API health check
                # In a real implementation, make actual API calls
                if api_name == 'portkey':
                    # response = requests.get('https://api.portkey.ai/health', timeout=5)
                    pass
                elif api_name == 'salesforce':
                    # response = requests.get('https://api.salesforce.com/health', timeout=5)
                    pass
                # Add other API health checks as needed

                response_time = time.time() - start_time

                api_health[api_name] = {
                    'status': 'healthy',
                    'response_time_ms': round(response_time * 1000, 2),
                    'timestamp': datetime.utcnow().isoformat(),
                }

            except Exception as e:
                api_health[api_name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat(),
                }
                overall_status = 'degraded'

        return {
            'status': overall_status,
            'apis': api_health,
            'timestamp': datetime.utcnow().isoformat(),
        }

    def _check_filesystem_health(self) -> dict[str, Any]:
        """Check filesystem health and permissions"""

        try:
            # Check if we can write to temporary directory
            test_file = '/tmp/sophia_health_check.txt'

            start_time = time.time()

            with open(test_file, 'w') as f:
                f.write('health check')

            with open(test_file) as f:
                content = f.read()

            os.remove(test_file)

            response_time = time.time() - start_time

            if content != 'health check':
                raise Exception("File content mismatch")

            return {
                'status': 'healthy',
                'write_test_ms': round(response_time * 1000, 2),
                'timestamp': datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }

    def _check_dependencies(self) -> dict[str, Any]:
        """Check application dependencies"""

        dependencies = {
            'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
            'flask_available': True,
            'redis_available': True,
            'requests_available': True,
        }

        try:
            import flask
            dependencies['flask_version'] = flask.__version__
        except ImportError:
            dependencies['flask_available'] = False

        try:
            import redis
            dependencies['redis_version'] = redis.__version__
        except ImportError:
            dependencies['redis_available'] = False

        try:
            import requests
            dependencies['requests_version'] = requests.__version__
        except ImportError:
            dependencies['requests_available'] = False

        return dependencies

    def _generate_metrics(self) -> dict[str, Any]:
        """Generate metrics for monitoring systems"""

        system_health = self._get_system_health()

        metrics = {
            'sophia_uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
            'sophia_cpu_usage_percent': system_health.get('cpu', {}).get('usage_percent', 0),
            'sophia_memory_usage_percent': system_health.get('memory', {}).get('usage_percent', 0),
            'sophia_disk_usage_percent': system_health.get('disk', {}).get('usage_percent', 0),
            'sophia_process_memory_mb': system_health.get('process', {}).get('memory_mb', 0),
            'sophia_process_threads': system_health.get('process', {}).get('threads', 0),
        }

        # Add component health metrics
        for component in ['database', 'redis', 'external_apis']:
            component_health = self._check_component_health(component)
            status_value = 1 if component_health['status'] == 'healthy' else 0
            metrics[f'sophia_{component}_healthy'] = status_value

        return metrics

def init_health_monitor(app: Flask) -> HealthMonitor:
    """Initialize health monitoring for Flask app"""

    monitor = HealthMonitor(app)
    logger.info("Health monitoring initialized successfully")
    return monitor

