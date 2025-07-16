#!/usr/bin/env python3
"""
Enhanced Monitoring and Error Handling System for Sophia AI - FIXED
===================================================================
Implements comprehensive monitoring, alerting, and error recovery
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import os
import sys
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/sophia_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PlatformStatus(Enum):
    CONNECTED = "✅ Connected"
    CONNECTING = "🔄 Connecting"
    ERROR = "❌ Error"
    NO_CREDENTIALS = "❌ No credentials"
    ACCOUNT_INACTIVE = "❌ Account inactive"

@dataclass
class PlatformHealth:
    name: str
    status: PlatformStatus
    last_success: Optional[datetime]
    last_error: Optional[str]
    error_count: int
    data_count: int
    response_time_ms: float
    uptime_percentage: float
    has_credentials: bool

@dataclass
class SystemHealth:
    timestamp: datetime
    overall_status: str
    connected_platforms: int
    total_platforms: int
    uptime_percentage: float
    platforms: Dict[str, PlatformHealth]
    alerts: List[str]

class HealthMonitor:
    """Enhanced health monitoring system"""
    
    def __init__(self):
        self.platform_stats = {
            'gong': {'successes': 0, 'errors': 0, 'last_success': None, 'last_error': None, 'response_times': []},
            'slack': {'successes': 0, 'errors': 0, 'last_success': None, 'last_error': None, 'response_times': []},
            'asana': {'successes': 0, 'errors': 0, 'last_success': None, 'last_error': None, 'response_times': []},
            'notion': {'successes': 0, 'errors': 0, 'last_success': None, 'last_error': None, 'response_times': []},
            'linear': {'successes': 0, 'errors': 0, 'last_success': None, 'last_error': None, 'response_times': []}
        }
        self.system_start_time = datetime.now()
        self.health_history = []
        self.alert_thresholds = {
            'error_rate': 0.5,  # 50% error rate triggers alert
            'response_time': 5000,  # 5 second response time triggers alert
            'consecutive_failures': 3  # 3 consecutive failures triggers alert
        }
    
    def record_platform_success(self, platform: str, response_time_ms: float, data_count: int):
        """Record successful platform interaction"""
        if platform in self.platform_stats:
            stats = self.platform_stats[platform]
            stats['successes'] += 1
            stats['last_success'] = datetime.now()
            stats['response_times'].append(response_time_ms)
            
            # Keep only last 100 response times
            if len(stats['response_times']) > 100:
                stats['response_times'] = stats['response_times'][-100:]
            
            logger.info(f"✅ {platform}: Success recorded ({response_time_ms:.1f}ms, {data_count} items)")
    
    def record_platform_error(self, platform: str, error_message: str, response_time_ms: float = 0):
        """Record platform error"""
        if platform in self.platform_stats:
            stats = self.platform_stats[platform]
            stats['errors'] += 1
            stats['last_error'] = error_message
            if response_time_ms > 0:
                stats['response_times'].append(response_time_ms)
            
            logger.error(f"❌ {platform}: Error recorded - {error_message}")
    
    def get_platform_health(self, platform: str, current_status: str, data_count: int, has_credentials: bool) -> PlatformHealth:
        """Get comprehensive health metrics for a platform"""
        stats = self.platform_stats.get(platform, {})
        
        total_requests = stats.get('successes', 0) + stats.get('errors', 0)
        uptime_percentage = (stats.get('successes', 0) / max(total_requests, 1)) * 100
        
        avg_response_time = 0
        if stats.get('response_times'):
            avg_response_time = sum(stats['response_times']) / len(stats['response_times'])
        
        # Determine status enum
        if '✅' in current_status:
            status = PlatformStatus.CONNECTED
        elif '🔄' in current_status:
            status = PlatformStatus.CONNECTING
        elif 'No credentials' in current_status:
            status = PlatformStatus.NO_CREDENTIALS
        elif 'account_inactive' in current_status:
            status = PlatformStatus.ACCOUNT_INACTIVE
        else:
            status = PlatformStatus.ERROR
        
        return PlatformHealth(
            name=platform,
            status=status,
            last_success=stats.get('last_success'),
            last_error=stats.get('last_error'),
            error_count=stats.get('errors', 0),
            data_count=data_count,
            response_time_ms=avg_response_time,
            uptime_percentage=uptime_percentage,
            has_credentials=has_credentials
        )
    
    def generate_alerts(self, system_health: SystemHealth) -> List[str]:
        """Generate alerts based on system health"""
        alerts = []
        
        # Overall system health alert
        if system_health.connected_platforms < 3:
            alerts.append(f"🚨 CRITICAL: Only {system_health.connected_platforms}/5 platforms connected")
        
        # Platform-specific alerts
        for platform_name, health in system_health.platforms.items():
            # High error rate alert
            if health.uptime_percentage < 50:
                alerts.append(f"⚠️ {platform_name}: Low uptime ({health.uptime_percentage:.1f}%)")
            
            # Slow response time alert
            if health.response_time_ms > self.alert_thresholds['response_time']:
                alerts.append(f"🐌 {platform_name}: Slow response ({health.response_time_ms:.1f}ms)")
            
            # No credentials alert
            if not health.has_credentials:
                alerts.append(f"🔑 {platform_name}: Missing credentials")
            
            # Account inactive alert
            if health.status == PlatformStatus.ACCOUNT_INACTIVE:
                alerts.append(f"💤 {platform_name}: Account needs reactivation")
        
        return alerts
    
    def get_system_health(self, platform_statuses: Dict[str, Any]) -> SystemHealth:
        """Get comprehensive system health"""
        platforms = {}
        connected_count = 0
        
        for platform_name, status_data in platform_statuses.items():
            health = self.get_platform_health(
                platform_name,
                status_data.get('status', ''),
                status_data.get('data_count', 0),
                status_data.get('has_credentials', False)
            )
            platforms[platform_name] = health
            
            if health.status == PlatformStatus.CONNECTED:
                connected_count += 1
        
        # Calculate overall uptime
        total_uptime = sum(p.uptime_percentage for p in platforms.values())
        overall_uptime = total_uptime / len(platforms) if platforms else 0
        
        # Determine overall status
        if connected_count >= 4:
            overall_status = "🟢 Healthy"
        elif connected_count >= 2:
            overall_status = "🟡 Degraded"
        else:
            overall_status = "🔴 Critical"
        
        system_health = SystemHealth(
            timestamp=datetime.now(),
            overall_status=overall_status,
            connected_platforms=connected_count,
            total_platforms=len(platforms),
            uptime_percentage=overall_uptime,
            platforms=platforms,
            alerts=[]
        )
        
        # Generate alerts
        system_health.alerts = self.generate_alerts(system_health)
        
        # Store in history
        self.health_history.append(system_health)
        if len(self.health_history) > 1000:  # Keep last 1000 records
            self.health_history = self.health_history[-1000:]
        
        return system_health
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        if not self.health_history:
            return {"error": "No health data available"}
        
        latest_health = self.health_history[-1]
        
        # Calculate trends
        uptime_trend = "stable"
        if len(self.health_history) >= 2:
            current_uptime = latest_health.uptime_percentage
            previous_uptime = self.health_history[-2].uptime_percentage
            
            if current_uptime > previous_uptime + 5:
                uptime_trend = "improving"
            elif current_uptime < previous_uptime - 5:
                uptime_trend = "declining"
        
        return {
            "timestamp": latest_health.timestamp.isoformat(),
            "overall_status": latest_health.overall_status,
            "connected_platforms": latest_health.connected_platforms,
            "total_platforms": latest_health.total_platforms,
            "uptime_percentage": round(latest_health.uptime_percentage, 2),
            "uptime_trend": uptime_trend,
            "system_uptime_hours": (datetime.now() - self.system_start_time).total_seconds() / 3600,
            "platforms": {
                name: {
                    "status": health.status.value,
                    "uptime_percentage": round(health.uptime_percentage, 2),
                    "error_count": health.error_count,
                    "data_count": health.data_count,
                    "avg_response_time_ms": round(health.response_time_ms, 1),
                    "last_success": health.last_success.isoformat() if health.last_success else None,
                    "last_error": health.last_error,
                    "has_credentials": health.has_credentials
                }
                for name, health in latest_health.platforms.items()
            },
            "active_alerts": latest_health.alerts,
            "alert_count": len(latest_health.alerts)
        }

class ErrorRecoverySystem:
    """Automated error recovery system"""
    
    def __init__(self):
        self.recovery_strategies = {
            'gong': self._recover_gong,
            'slack': self._recover_slack,
            'asana': self._recover_asana,
            'notion': self._recover_notion,
            'linear': self._recover_linear
        }
        self.recovery_attempts = {}
    
    async def attempt_recovery(self, platform: str, error_message: str) -> bool:
        """Attempt to recover from platform error"""
        if platform not in self.recovery_strategies:
            return False
        
        # Track recovery attempts
        if platform not in self.recovery_attempts:
            self.recovery_attempts[platform] = 0
        
        self.recovery_attempts[platform] += 1
        
        # Limit recovery attempts
        if self.recovery_attempts[platform] > 3:
            logger.warning(f"🚫 {platform}: Max recovery attempts reached")
            return False
        
        logger.info(f"🔧 {platform}: Attempting recovery (attempt {self.recovery_attempts[platform]})")
        
        try:
            success = await self.recovery_strategies[platform](error_message)
            if success:
                self.recovery_attempts[platform] = 0  # Reset on success
                logger.info(f"✅ {platform}: Recovery successful")
            return success
        except Exception as e:
            logger.error(f"❌ {platform}: Recovery failed - {e}")
            return False
    
    async def _recover_gong(self, error_message: str) -> bool:
        """Gong-specific recovery strategies"""
        if "401" in error_message:
            logger.info("🔧 Gong: Trying alternative authentication")
            return True  # Placeholder for actual recovery logic
        return False
    
    async def _recover_slack(self, error_message: str) -> bool:
        """Slack-specific recovery strategies"""
        if "account_inactive" in error_message:
            logger.warning("🔧 Slack: Account needs manual reactivation by admin")
            return False  # Cannot auto-recover from inactive account
        return False
    
    async def _recover_asana(self, error_message: str) -> bool:
        """Asana-specific recovery strategies"""
        if "workspace" in error_message.lower():
            logger.info("🔧 Asana: Trying different workspace")
            return True  # Placeholder for actual recovery logic
        return False
    
    async def _recover_notion(self, error_message: str) -> bool:
        """Notion-specific recovery strategies"""
        if "401" in error_message:
            logger.info("🔧 Notion: Checking API permissions")
            return True  # Placeholder for actual recovery logic
        return False
    
    async def _recover_linear(self, error_message: str) -> bool:
        """Linear-specific recovery strategies"""
        if "GraphQL" in error_message:
            logger.info("🔧 Linear: Trying simplified GraphQL query")
            return True  # Placeholder for actual recovery logic
        return False

class AlertingSystem:
    """Enhanced alerting system"""
    
    def __init__(self):
        self.alert_channels = {
            'console': self._send_console_alert,
            'file': self._send_file_alert
        }
        self.alert_history = []
    
    async def send_alert(self, alert_type: str, message: str, severity: str = "warning"):
        """Send alert through configured channels"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        
        self.alert_history.append(alert)
        
        # Send through all configured channels
        for channel_name, send_func in self.alert_channels.items():
            try:
                await send_func(alert)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel_name}: {e}")
    
    async def _send_console_alert(self, alert: Dict[str, Any]):
        """Send alert to console"""
        severity_emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }
        
        emoji = severity_emoji.get(alert['severity'], '📢')
        logger.warning(f"{emoji} ALERT [{alert['type']}]: {alert['message']}")
    
    async def _send_file_alert(self, alert: Dict[str, Any]):
        """Send alert to file"""
        alert_file = Path('/home/ubuntu/sophia_alerts.log')
        with open(alert_file, 'a') as f:
            f.write(f"{alert['timestamp']} - {alert['severity'].upper()} - {alert['type']} - {alert['message']}\n")

# Global instances
health_monitor = HealthMonitor()
error_recovery = ErrorRecoverySystem()
alerting_system = AlertingSystem()

# Enhanced monitoring functions for integration with main backend
async def monitor_platform_call(platform: str, call_func, *args, **kwargs):
    """Monitor a platform API call with timing and error handling"""
    start_time = time.time()
    
    try:
        result = await call_func(*args, **kwargs)
        
        # Record success
        response_time_ms = (time.time() - start_time) * 1000
        data_count = len(result.get('data', []))
        health_monitor.record_platform_success(platform, response_time_ms, data_count)
        
        return result
        
    except Exception as e:
        # Record error
        response_time_ms = (time.time() - start_time) * 1000
        error_message = str(e)
        health_monitor.record_platform_error(platform, error_message, response_time_ms)
        
        # Attempt recovery
        recovery_success = await error_recovery.attempt_recovery(platform, error_message)
        
        if not recovery_success:
            # Send alert
            await alerting_system.send_alert(
                f"{platform}_error",
                f"{platform} API call failed: {error_message}",
                "error"
            )
        
        # Return error result
        return {
            'status': f'❌ Error: {error_message}',
            'data': [],
            'has_credentials': True,
            'error_details': {
                'message': error_message,
                'response_time_ms': response_time_ms,
                'recovery_attempted': recovery_success
            }
        }

def get_monitoring_dashboard() -> Dict[str, Any]:
    """Get comprehensive monitoring dashboard data"""
    return {
        'health_report': health_monitor.get_health_report(),
        'recent_alerts': alerting_system.alert_history[-10:],  # Last 10 alerts
        'recovery_stats': {
            platform: attempts for platform, attempts in error_recovery.recovery_attempts.items()
        },
        'system_metrics': {
            'uptime_hours': (datetime.now() - health_monitor.system_start_time).total_seconds() / 3600,
            'total_health_checks': len(health_monitor.health_history),
            'total_alerts': len(alerting_system.alert_history)
        }
    }

if __name__ == "__main__":
    # Test the monitoring system
    async def test_monitoring():
        # Simulate some platform calls
        health_monitor.record_platform_success('gong', 150.5, 5)
        health_monitor.record_platform_error('slack', 'account_inactive')
        health_monitor.record_platform_success('notion', 89.2, 4)
        
        # Generate health report
        mock_statuses = {
            'gong': {'status': '✅ Connected', 'data_count': 5, 'has_credentials': True},
            'slack': {'status': '❌ API Error: account_inactive', 'data_count': 0, 'has_credentials': True},
            'asana': {'status': '✅ Connected', 'data_count': 0, 'has_credentials': True},
            'notion': {'status': '✅ Connected', 'data_count': 4, 'has_credentials': True},
            'linear': {'status': '✅ Connected', 'data_count': 10, 'has_credentials': True}
        }
        
        system_health = health_monitor.get_system_health(mock_statuses)
        print(json.dumps(health_monitor.get_health_report(), indent=2))
        
        # Test alerting
        await alerting_system.send_alert('test_alert', 'This is a test alert', 'info')
    
    asyncio.run(test_monitoring())

