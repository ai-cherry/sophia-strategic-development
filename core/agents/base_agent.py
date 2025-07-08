"""
Base Agent class for Sophia AI Agent framework
Provides foundational capabilities for all agents
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from core.config_manager import get_config_value as config


class AgentStatus(Enum):
    """Agent status enumeration"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class AgentConfig:
    """Configuration for agents"""

    name: str
    version: str = "1.0.0"
    max_concurrent_tasks: int = 10
    retry_attempts: int = 3
    timeout_seconds: int = 30
    log_level: str = "INFO"
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task representation for agents"""

    id: str
    type: str
    payload: dict[str, Any]
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of agent task execution"""

    task_id: str
    status: str  # success, error, timeout
    result: Any
    error: str | None = None
    execution_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all Sophia AI agents
    Provides common functionality and interface
    """

    def __init__(self, config_dict: dict | None = None):
        self.config_dict = config_dict or {}
        self.agent_config = self._create_agent_config()
        self.status = AgentStatus.INITIALIZING
        self.logger = self._setup_logger()
        self.tasks_queue = asyncio.Queue()
        self.active_tasks: dict[str, asyncio.Task] = {}
        self.task_history: list[TaskResult] = []
        self.initialized = False
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_timeout": 0,
            "avg_execution_time": 0.0,
            "last_activity": None,
        }

    def _create_agent_config(self) -> AgentConfig:
        """Create agent configuration from config dict"""
        return AgentConfig(
            name=self.config_dict.get("name", self.__class__.__name__),
            version=self.config_dict.get("version", "1.0.0"),
            max_concurrent_tasks=self.config_dict.get("max_concurrent_tasks", 10),
            retry_attempts=self.config_dict.get("retry_attempts", 3),
            timeout_seconds=self.config_dict.get("timeout_seconds", 30),
            log_level=self.config_dict.get("log_level", "INFO"),
            capabilities=self.config_dict.get("capabilities", []),
            metadata=self.config_dict.get("metadata", {}),
        )

    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the agent"""
        logger = logging.getLogger(f"sophia.agent.{self.agent_config.name}")
        logger.setLevel(getattr(logging, self.agent_config.log_level))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f"%(asctime)s - {self.agent_config.name} - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def initialize(self):
        """Initialize the agent"""
        try:
            self.logger.info(f"Initializing {self.agent_config.name} agent...")

            # Load configuration from ESC
            self.esc_config = config

            # Perform agent-specific initialization
            await self._agent_initialize()

            self.status = AgentStatus.ACTIVE
            self.initialized = True
            self.metrics["last_activity"] = datetime.now(UTC)

            self.logger.info(f"{self.agent_config.name} agent initialized successfully")

        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.exception(
                f"Failed to initialize {self.agent_config.name}: {e!s}"
            )
            raise

    @abstractmethod
    async def _agent_initialize(self):
        """Agent-specific initialization logic"""
        pass

    async def start(self):
        """Start the agent and begin processing tasks"""
        if not self.initialized:
            await self.initialize()

        self.logger.info(f"Starting {self.agent_config.name} agent...")

        # Start task processing loop
        asyncio.create_task(self._task_processing_loop())

        # Start health monitoring
        asyncio.create_task(self._health_monitoring_loop())

    async def stop(self):
        """Stop the agent gracefully"""
        self.logger.info(f"Stopping {self.agent_config.name} agent...")
        self.status = AgentStatus.STOPPED

        # Cancel all active tasks
        for task_id, task in self.active_tasks.items():
            if not task.done():
                task.cancel()
                self.logger.info(f"Cancelled task {task_id}")

        # Wait for tasks to complete
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)

        self.logger.info(f"{self.agent_config.name} agent stopped")

    async def submit_task(self, task: Task) -> str:
        """Submit a task to the agent"""
        await self.tasks_queue.put(task)
        self.logger.debug(f"Task {task.id} submitted to {self.agent_config.name}")
        return task.id

    async def get_task_result(
        self, task_id: str, timeout: int | None = None
    ) -> TaskResult | None:
        """Get result of a specific task"""
        # Check task history first
        for result in self.task_history:
            if result.task_id == task_id:
                return result

        # Wait for task to complete if it's active
        if task_id in self.active_tasks:
            try:
                await asyncio.wait_for(self.active_tasks[task_id], timeout=timeout)
                # Check history again
                for result in self.task_history:
                    if result.task_id == task_id:
                        return result
            except TimeoutError:
                return None

        return None

    async def _task_processing_loop(self):
        """Main task processing loop"""
        while self.status != AgentStatus.STOPPED:
            try:
                # Get task from queue
                task = await asyncio.wait_for(self.tasks_queue.get(), timeout=1.0)

                # Check if we have capacity
                if len(self.active_tasks) >= self.agent_config.max_concurrent_tasks:
                    await self.tasks_queue.put(task)  # Put it back
                    await asyncio.sleep(0.1)
                    continue

                # Process task
                asyncio.create_task(self._process_task(task))

            except TimeoutError:
                # No tasks available, continue
                continue
            except Exception as e:
                self.logger.exception(f"Error in task processing loop: {e!s}")
                await asyncio.sleep(1.0)

    async def _process_task(self, task: Task):
        """Process a single task"""
        start_time = datetime.now(UTC)
        self.active_tasks[task.id] = asyncio.current_task()

        try:
            self.logger.debug(f"Processing task {task.id} of type {task.type}")

            # Execute the task
            result = await asyncio.wait_for(
                self._execute_task(task),
                timeout=task.timeout or self.agent_config.timeout_seconds,
            )

            # Calculate execution time
            execution_time = (datetime.now(UTC) - start_time).total_seconds()

            # Create result
            task_result = TaskResult(
                task_id=task.id,
                status="success",
                result=result,
                execution_time=execution_time,
                metadata={"completed_at": datetime.now(UTC).isoformat()},
            )

            # Update metrics
            self.metrics["tasks_completed"] += 1
            self._update_avg_execution_time(execution_time)

            self.logger.debug(
                f"Task {task.id} completed successfully in {execution_time:.2f}s"
            )

        except TimeoutError:
            task_result = TaskResult(
                task_id=task.id,
                status="timeout",
                result=None,
                error="Task execution timed out",
                execution_time=(datetime.now(UTC) - start_time).total_seconds(),
            )
            self.metrics["tasks_timeout"] += 1
            self.logger.warning(f"Task {task.id} timed out")

        except Exception as e:
            task_result = TaskResult(
                task_id=task.id,
                status="error",
                result=None,
                error=str(e),
                execution_time=(datetime.now(UTC) - start_time).total_seconds(),
            )
            self.metrics["tasks_failed"] += 1
            self.logger.exception(f"Task {task.id} failed: {e!s}")

        finally:
            # Store result and cleanup
            self.task_history.append(task_result)
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            self.metrics["last_activity"] = datetime.now(UTC)

            # Limit history size
            if len(self.task_history) > 1000:
                self.task_history = self.task_history[-500:]

    @abstractmethod
    async def _execute_task(self, task: Task) -> Any:
        """Execute a specific task - must be implemented by subclasses"""
        pass

    async def _health_monitoring_loop(self):
        """Health monitoring loop"""
        while self.status != AgentStatus.STOPPED:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                # Update status based on activity
                if self.metrics["last_activity"]:
                    time_since_activity = (
                        datetime.now(UTC) - self.metrics["last_activity"]
                    ).total_seconds()
                    if time_since_activity > 300:  # 5 minutes
                        if self.status == AgentStatus.ACTIVE:
                            self.status = AgentStatus.IDLE
                            self.logger.info(
                                f"{self.agent_config.name} agent is now idle"
                            )
                    elif self.status == AgentStatus.IDLE:
                        self.status = AgentStatus.ACTIVE
                        self.logger.info(
                            f"{self.agent_config.name} agent is now active"
                        )

            except Exception as e:
                self.logger.exception(f"Error in health monitoring: {e!s}")

    def _update_avg_execution_time(self, execution_time: float):
        """Update average execution time metric"""
        completed = self.metrics["tasks_completed"]
        if completed == 1:
            self.metrics["avg_execution_time"] = execution_time
        else:
            current_avg = self.metrics["avg_execution_time"]
            self.metrics["avg_execution_time"] = (
                (current_avg * (completed - 1)) + execution_time
            ) / completed

    def get_status(self) -> dict[str, Any]:
        """Get agent status and metrics"""
        return {
            "name": self.agent_config.name,
            "status": self.status.value,
            "initialized": self.initialized,
            "active_tasks": len(self.active_tasks),
            "queue_size": self.tasks_queue.qsize(),
            "capabilities": self.agent_config.capabilities,
            "metrics": self.metrics.copy(),
            "config": {
                "version": self.agent_config.version,
                "max_concurrent_tasks": self.agent_config.max_concurrent_tasks,
                "timeout_seconds": self.agent_config.timeout_seconds,
            },
        }

    def get_capabilities(self) -> list[str]:
        """Get agent capabilities"""
        return self.agent_config.capabilities.copy()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check"""
        try:
            health_status = {
                "healthy": self.status in [AgentStatus.ACTIVE, AgentStatus.IDLE],
                "status": self.status.value,
                "initialized": self.initialized,
                "active_tasks": len(self.active_tasks),
                "error_rate": self._calculate_error_rate(),
                "last_activity": (
                    self.metrics["last_activity"].isoformat()
                    if self.metrics["last_activity"]
                    else None
                ),
                "uptime": self._calculate_uptime(),
            }

            # Perform agent-specific health checks
            agent_health = await self._agent_health_check()
            health_status.update(agent_health)

            return health_status

        except Exception as e:
            return {"healthy": False, "status": "error", "error": str(e)}

    async def _agent_health_check(self) -> dict[str, Any]:
        """Agent-specific health check - can be overridden by subclasses"""
        return {}

    def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        total_tasks = (
            self.metrics["tasks_completed"]
            + self.metrics["tasks_failed"]
            + self.metrics["tasks_timeout"]
        )
        if total_tasks == 0:
            return 0.0
        return (
            self.metrics["tasks_failed"] + self.metrics["tasks_timeout"]
        ) / total_tasks

    def _calculate_uptime(self) -> str | None:
        """Calculate uptime since initialization"""
        if self.metrics["last_activity"]:
            # This is a simple approximation - in production you'd track initialization time
            return "uptime_calculation_placeholder"
        return None
