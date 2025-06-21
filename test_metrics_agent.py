import asyncio
from backend.agents.specialized.metrics_agent import MetricsAgent, AgentConfig
from backend.agents.core.base_agent import Task
from datetime import datetime

async def test():
    config = AgentConfig(
        agent_id='metrics_agent_01',
        agent_type='utility',
        specialization='Metrics'
    )
    agent = await MetricsAgent.pooled(config)
    task = Task(
        task_id='test_metrics',
        task_type='show_metrics',
        agent_id='metrics',
        task_data={'query': 'show agent metrics', 'timestamp': datetime.utcnow().isoformat()},
        status=None,
        created_at=datetime.utcnow(),
        started_at=None,
        completed_at=None,
        result=None,
        error_message=None,
        priority=1,
    )
    result = await agent.process_task(task)
    print("=== LIVE METRICS AGENT RESULT ===")
    print(result)

if __name__ == "__main__":
    asyncio.run(test()) 