"""Specialized agent exports.

Historically this module imported all Pay Ready agent classes during package
initialisation which triggered heavy dependencies (``pandas``, ``sqlalchemy``
etc.) even when the agents were not used.  This caused import errors during test
collection on minimal environments.  The exports are now loaded lazily the first
time they are accessed.
"""

from importlib import import_module
from typing import Any

__all__ = [
    "PayReadyAgentOrchestrator",
    "ClientHealthAgent",
    "SalesIntelligenceAgent",
    "MarketResearchAgent",
    "ComplianceMonitoringAgent",
    "WorkflowAutomationAgent",
    "AgentPriority",
    "AgentStatus",
    "AgentTask",
    "AgentResult",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin wrapper
    if name in __all__:
        mod = import_module("backend.agents.specialized.pay_ready_agents")
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
