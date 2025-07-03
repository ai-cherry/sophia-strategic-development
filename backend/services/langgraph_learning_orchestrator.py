
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional

class LearningWorkflowState(TypedDict):
    messages: List[Any]
    business_context: Dict[str, Any]
    learning_objectives: List[str]
    agent_feedback: Dict[str, Any]
    memory_updates: List[Dict[str, Any]]
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
        