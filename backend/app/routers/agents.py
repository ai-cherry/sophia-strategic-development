"""
Agent Monitoring API Router

Provides endpoints for monitoring and controlling autonomous agents
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
import asyncio
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Agent Manager (singleton pattern)
class AgentManager:
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.actions: List[Dict] = []
        self.websockets: List[WebSocket] = []
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize with known agents"""
        self.agents = {
            'lambda-monitor': {
                'id': 'lambda-monitor',
                'name': 'Lambda Labs Monitor',
                'type': 'infrastructure',
                'status': 'running',
                'health': 'healthy',
                'description': 'Monitors Lambda Labs GPU instances and optimizes usage',
                'version': '1.0.0',
                'uptime': 86400,
                'lastActivity': datetime.now().isoformat(),
                'metrics': {
                    'actionsToday': 24,
                    'successRate': 98.5,
                    'avgResponseTime': 120,
                    'resourceUsage': {'cpu': 15, 'memory': 32, 'gpu': 78}
                },
                'config': {
                    'autoRestart': True,
                    'maxActionsPerHour': 10,
                    'thresholds': {'gpu_utilization': 80, 'cost_limit': 100}
                }
            },
            'qdrant-optimizer': {
                'id': 'qdrant-optimizer',
                'name': 'Qdrant Optimizer',
                'type': 'optimization',
                'status': 'running',
                'health': 'healthy',
                'description': 'Optimizes Qdrant vector database performance and indexing',
                'version': '1.0.0',
                'uptime': 172800,
                'lastActivity': datetime.now().isoformat(),
                'metrics': {
                    'actionsToday': 18,
                    'successRate': 99.2,
                    'avgResponseTime': 85,
                    'resourceUsage': {'cpu': 22, 'memory': 45}
                },
                'config': {
                    'autoRestart': True,
                    'maxActionsPerHour': 20,
                    'thresholds': {'query_latency': 100, 'index_size': 1000000}
                }
            },
            'prometheus-exporter': {
                'id': 'prometheus-exporter',
                'name': 'Prometheus Metrics Exporter',
                'type': 'monitoring',
                'status': 'running',
                'health': 'healthy',
                'description': 'Exports system metrics to Prometheus for monitoring',
                'version': '1.0.0',
                'uptime': 259200,
                'lastActivity': datetime.now().isoformat(),
                'metrics': {
                    'actionsToday': 288,
                    'successRate': 100,
                    'avgResponseTime': 15,
                    'resourceUsage': {'cpu': 5, 'memory': 12}
                },
                'config': {
                    'autoRestart': True,
                    'maxActionsPerHour': 60,
                    'thresholds': {'metric_lag': 5}
                }
            }
        }
        
        # Generate some sample actions
        self._generate_sample_actions()
    
    def _generate_sample_actions(self):
        """Generate sample action history"""
        action_templates = [
            {
                'agentId': 'lambda-monitor',
                'agentName': 'Lambda Labs Monitor',
                'actions': [
                    'Scaled down idle GPU instance',
                    'Detected high GPU utilization',
                    'Optimized instance allocation',
                    'Generated cost report'
                ]
            },
            {
                'agentId': 'qdrant-optimizer',
                'agentName': 'Qdrant Optimizer',
                'actions': [
                    'Optimized vector index for faster queries',
                    'Compacted database segments',
                    'Rebalanced shards',
                    'Updated index configuration'
                ]
            },
            {
                'agentId': 'prometheus-exporter',
                'agentName': 'Prometheus Metrics Exporter',
                'actions': [
                    'Exported system metrics',
                    'Updated metric labels',
                    'Cleaned up stale metrics',
                    'Synchronized with Prometheus server'
                ]
            }
        ]
        
        # Generate actions for the past 24 hours
        for hours_ago in range(24):
            for template in action_templates:
                if random.random() < 0.3:  # 30% chance of action per hour
                    action = random.choice(template['actions'])
                    self.actions.append({
                        'id': str(len(self.actions) + 1),
                        'agentId': template['agentId'],
                        'agentName': template['agentName'],
                        'type': random.choice(['automated', 'scheduled']),
                        'action': action,
                        'status': 'completed' if random.random() > 0.05 else 'failed',
                        'timestamp': (datetime.now() - timedelta(hours=hours_ago)).isoformat(),
                        'duration': random.randint(5, 300),
                        'impact': self._generate_impact(template['agentId']),
                        'canRollback': random.random() > 0.3
                    })
    
    def _generate_impact(self, agent_id: str) -> Optional[Dict]:
        """Generate impact data for actions"""
        if agent_id == 'lambda-monitor':
            if random.random() > 0.5:
                return {
                    'type': 'cost_savings',
                    'value': round(random.uniform(5, 50), 2),
                    'unit': 'USD'
                }
        elif agent_id == 'qdrant-optimizer':
            if random.random() > 0.5:
                return {
                    'type': 'performance',
                    'value': round(random.uniform(10, 50), 1),
                    'unit': '%'
                }
        return None
    
    async def broadcast_update(self, update_type: str, data: Dict):
        """Broadcast updates to all connected WebSocket clients"""
        message = json.dumps({
            'type': update_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
        disconnected = []
        for ws in self.websockets:
            try:
                await ws.send_text(message)
            except (ConnectionError, RuntimeError, Exception) as e:
                # Log the specific error for debugging
                logger.warning(f"WebSocket send failed, disconnecting client: {e}")
                disconnected.append(ws)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.websockets.remove(ws)

# Initialize agent manager
agent_manager = AgentManager()

# Pydantic models
class AgentControlRequest(BaseModel):
    action: str  # 'start', 'stop', 'restart'
    
class EmergencyStopRequest(BaseModel):
    confirm: bool

# Agent status endpoint
@router.get("/status")
async def get_agent_status() -> List[Dict]:
    """Get status of all agents"""
    return list(agent_manager.agents.values())

# Get specific agent
@router.get("/{agent_id}")
async def get_agent(agent_id: str) -> Dict:
    """Get details of a specific agent"""
    agent = agent_manager.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# Agent actions endpoint
@router.get("/actions")
async def get_all_actions(
    range: str = Query("24h", regex="^(1h|24h|7d|30d)$")
) -> List[Dict]:
    """Get action history for all agents"""
    # Parse time range
    hours = {
        '1h': 1,
        '24h': 24,
        '7d': 168,
        '30d': 720
    }.get(range, 24)
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Filter actions by time range
    filtered_actions = [
        action for action in agent_manager.actions
        if datetime.fromisoformat(action['timestamp']) > cutoff_time
    ]
    
    # Sort by timestamp descending
    filtered_actions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return filtered_actions

# Agent-specific actions
@router.get("/{agent_id}/actions")
async def get_agent_actions(
    agent_id: str,
    range: str = Query("24h", regex="^(1h|24h|7d|30d)$")
) -> List[Dict]:
    """Get action history for a specific agent"""
    # Check if agent exists
    if agent_id not in agent_manager.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Parse time range
    hours = {
        '1h': 1,
        '24h': 24,
        '7d': 168,
        '30d': 720
    }.get(range, 24)
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Filter actions by agent and time range
    filtered_actions = [
        action for action in agent_manager.actions
        if action['agentId'] == agent_id and
        datetime.fromisoformat(action['timestamp']) > cutoff_time
    ]
    
    # Sort by timestamp descending
    filtered_actions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return filtered_actions

# Agent control endpoint
@router.post("/{agent_id}/control")
async def control_agent(agent_id: str, request: AgentControlRequest) -> Dict:
    """Control agent (start/stop/restart)"""
    agent = agent_manager.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent status
    if request.action == 'start':
        agent['status'] = 'running'
        agent['health'] = 'healthy'
    elif request.action == 'stop':
        agent['status'] = 'stopped'
    elif request.action == 'restart':
        agent['status'] = 'running'
        agent['health'] = 'healthy'
        agent['uptime'] = 0
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    agent['lastActivity'] = datetime.now().isoformat()
    
    # Create action record
    action = {
        'id': str(len(agent_manager.actions) + 1),
        'agentId': agent_id,
        'agentName': agent['name'],
        'type': 'manual',
        'action': f"Agent {request.action}",
        'status': 'completed',
        'timestamp': datetime.now().isoformat(),
        'duration': 1,
        'canRollback': False
    }
    agent_manager.actions.append(action)
    
    # Broadcast update
    await agent_manager.broadcast_update('agent_update', {
        'agentId': agent_id,
        'update': agent
    })
    
    return {'status': 'success', 'agent': agent}

# Analytics endpoint
@router.get("/analytics")
async def get_analytics(
    range: str = Query("24h", regex="^(1h|24h|7d|30d)$")
) -> Dict:
    """Get analytics data for all agents"""
    # Parse time range
    hours = {
        '1h': 1,
        '24h': 24,
        '7d': 168,
        '30d': 720
    }.get(range, 24)
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Calculate analytics
    total_agents = len(agent_manager.agents)
    active_agents = sum(1 for agent in agent_manager.agents.values() if agent['status'] == 'running')
    
    # Filter actions by time range
    recent_actions = [
        action for action in agent_manager.actions
        if datetime.fromisoformat(action['timestamp']) > cutoff_time
    ]
    
    total_actions = len(recent_actions)
    successful_actions = sum(1 for action in recent_actions if action['status'] == 'completed')
    success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 100
    
    # Calculate cost savings
    cost_savings = {
        'today': sum(
            action['impact']['value'] 
            for action in recent_actions 
            if action.get('impact', {}).get('type') == 'cost_savings' and 
            datetime.fromisoformat(action['timestamp']) > datetime.now() - timedelta(days=1)
        ),
        'week': sum(
            action['impact']['value'] 
            for action in recent_actions 
            if action.get('impact', {}).get('type') == 'cost_savings' and 
            datetime.fromisoformat(action['timestamp']) > datetime.now() - timedelta(days=7)
        ),
        'month': sum(
            action['impact']['value'] 
            for action in recent_actions 
            if action.get('impact', {}).get('type') == 'cost_savings' and 
            datetime.fromisoformat(action['timestamp']) > datetime.now() - timedelta(days=30)
        ),
        'total': sum(
            action['impact']['value'] 
            for action in agent_manager.actions 
            if action.get('impact', {}).get('type') == 'cost_savings'
        )
    }
    
    # Calculate ROI metrics
    automation_roi = {
        'timeSaved': total_actions * 2,  # Assume each action saves 2 hours
        'manualInterventionsAvoided': int(total_actions * 0.8),
        'efficiencyGain': round(success_rate * 0.5, 1)
    }
    
    # Performance metrics
    avg_response_time = sum(
        agent['metrics']['avgResponseTime'] 
        for agent in agent_manager.agents.values()
    ) / total_agents if total_agents > 0 else 0
    
    return {
        'totalAgents': total_agents,
        'activeAgents': active_agents,
        'totalActions': total_actions,
        'successRate': round(success_rate, 1),
        'costSavings': cost_savings,
        'automationROI': automation_roi,
        'performanceMetrics': {
            'avgResponseTime': round(avg_response_time, 1),
            'uptime': 99.8,
            'reliability': round(success_rate, 1)
        }
    }

# Emergency stop endpoint
@router.post("/emergency-stop")
async def emergency_stop(request: EmergencyStopRequest) -> Dict:
    """Emergency stop all agents"""
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Emergency stop not confirmed")
    
    stopped_agents = []
    
    # Stop all running agents
    for agent_id, agent in agent_manager.agents.items():
        if agent['status'] == 'running':
            agent['status'] = 'stopped'
            agent['health'] = 'unhealthy'
            agent['lastActivity'] = datetime.now().isoformat()
            stopped_agents.append(agent_id)
            
            # Create action record
            action = {
                'id': str(len(agent_manager.actions) + 1),
                'agentId': agent_id,
                'agentName': agent['name'],
                'type': 'manual',
                'action': 'Emergency stop executed',
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'duration': 1,
                'canRollback': False
            }
            agent_manager.actions.append(action)
    
    # Broadcast update
    await agent_manager.broadcast_update('emergency_stop', {
        'stoppedAgents': stopped_agents
    })
    
    return {
        'status': 'success',
        'message': f'Emergency stop executed. {len(stopped_agents)} agents stopped.',
        'stoppedAgents': stopped_agents
    }

# Rollback action endpoint
@router.post("/actions/{action_id}/rollback")
async def rollback_action(action_id: str) -> Dict:
    """Rollback a specific action"""
    # Find the action
    action = next((a for a in agent_manager.actions if a['id'] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if not action.get('canRollback', False):
        raise HTTPException(status_code=400, detail="Action cannot be rolled back")
    
    if action['status'] == 'rolled_back':
        raise HTTPException(status_code=400, detail="Action already rolled back")
    
    # Update action status
    action['status'] = 'rolled_back'
    
    # Create rollback action record
    rollback_action = {
        'id': str(len(agent_manager.actions) + 1),
        'agentId': action['agentId'],
        'agentName': action['agentName'],
        'type': 'manual',
        'action': f"Rolled back: {action['action']}",
        'status': 'completed',
        'timestamp': datetime.now().isoformat(),
        'duration': 5,
        'canRollback': False
    }
    agent_manager.actions.append(rollback_action)
    
    # Broadcast update
    await agent_manager.broadcast_update('action_rollback', {
        'actionId': action_id,
        'rollbackAction': rollback_action
    })
    
    return {'status': 'success', 'message': 'Action rolled back successfully'}

# WebSocket endpoint for real-time updates
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agent updates"""
    await websocket.accept()
    agent_manager.websockets.append(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_text(json.dumps({
            'type': 'connection',
            'message': 'Connected to agent monitoring WebSocket',
            'timestamp': datetime.now().isoformat()
        }))
        
        # Keep connection alive
        while True:
            # Receive messages (if any)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Process incoming messages if needed
                message = json.loads(data)
                logger.info(f"Received WebSocket message: {message}")
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text(json.dumps({
                    'type': 'ping',
                    'timestamp': datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        agent_manager.websockets.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in agent_manager.websockets:
            agent_manager.websockets.remove(websocket)

# Simulate agent activity (for demo purposes)
async def simulate_agent_activity():
    """Background task to simulate agent activity"""
    while True:
        await asyncio.sleep(30)  # Every 30 seconds
        
        # Randomly update agent metrics
        for agent in agent_manager.agents.values():
            if agent['status'] == 'running':
                # Update metrics
                agent['metrics']['actionsToday'] += random.randint(0, 2)
                agent['metrics']['avgResponseTime'] = random.randint(50, 200)
                agent['metrics']['resourceUsage']['cpu'] = random.randint(5, 50)
                agent['metrics']['resourceUsage']['memory'] = random.randint(10, 60)
                if 'gpu' in agent['metrics']['resourceUsage']:
                    agent['metrics']['resourceUsage']['gpu'] = random.randint(20, 90)
                
                agent['uptime'] += 30
                agent['lastActivity'] = datetime.now().isoformat()
                
                # Occasionally create new actions
                if random.random() < 0.3:
                    action_type = 'automated'
                    action_name = {
                        'lambda-monitor': 'Optimized GPU allocation',
                        'qdrant-optimizer': 'Reindexed vector collection',
                        'prometheus-exporter': 'Exported metrics batch'
                    }.get(agent['id'], 'Performed maintenance')
                    
                    action = {
                        'id': str(len(agent_manager.actions) + 1),
                        'agentId': agent['id'],
                        'agentName': agent['name'],
                        'type': action_type,
                        'action': action_name,
                        'status': 'completed' if random.random() > 0.05 else 'failed',
                        'timestamp': datetime.now().isoformat(),
                        'duration': random.randint(5, 120),
                        'impact': agent_manager._generate_impact(agent['id']),
                        'canRollback': random.random() > 0.3
                    }
                    agent_manager.actions.append(action)
                    
                    # Broadcast new action
                    await agent_manager.broadcast_update('new_action', action)

# Start background task
asyncio.create_task(simulate_agent_activity())
