from datetime import datetime
from typing import Any, Dict

from backend.agents.core.agno_performance_optimizer import AgnoPerformanceOptimizer
from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task


class MetricsAgent(BaseAgent):
    """Agent for querying live agent/system performance metrics.

    Returns AgnoPerformanceOptimizer metrics and summary.
    """
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.optimizer = AgnoPerformanceOptimizer()

    @classmethod
    async def pooled(cls, config: AgentConfig) -> "MetricsAgent":
        optimizer = AgnoPerformanceOptimizer()
        await optimizer.register_agent_class("metrics", cls)
        agent = await optimizer.get_or_create_agent("metrics", {"config": config})
        return agent

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a metrics query task. Returns metrics and summary."""
        metrics = self.optimizer.get_metrics()
        summary = {}
        for agent_type, data in metrics.items():
            inst_times = data.get("instantiation_us", [])
            summary[agent_type] = {
                "avg_instantiation_us": (
                    round(sum(inst_times) / len(inst_times), 2) if inst_times else None
                ),
                "pool_size": len(self.optimizer.agent_pools.get(agent_type, [])),
                "pool_max": self.optimizer.pool_size_per_type,
                "instantiation_samples": len(inst_times),
            }
        return {
            "metrics": metrics,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
        }
