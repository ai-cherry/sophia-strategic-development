from typing import Any, Optional, TypedDict

from langgraph.graph import END, StateGraph


class LearningWorkflowState(TypedDict):
    messages: list[Any]
    business_context: dict[str, Any]
    learning_objectives: list[str]
    agent_feedback: dict[str, Any]
    memory_updates: list[dict[str, Any]]
    final_outcome: Optional[str]


class LangGraphLearningOrchestrator:
    def __init__(self):
        self.workflow = StateGraph(LearningWorkflowState)
        self._setup_workflow()

    def _setup_workflow(self):
        self.workflow.add_node("supervisor", self.supervisor_agent)
        self.workflow.add_node("memory_curator", self.memory_curator_agent)
        self.workflow.add_edge("supervisor", "memory_curator")
        self.workflow.add_edge("memory_curator", END)
        self.workflow.set_entry_point("supervisor")
