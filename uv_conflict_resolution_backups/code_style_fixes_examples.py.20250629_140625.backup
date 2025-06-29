#!/usr/bin/env python3
"""
Sophia AI - Code Style Fixes Examples
This file demonstrates practical implementations of code style fixes for identified issues.
"""

import abc
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

# -----------------------------------------------------------------------------
# 1. Abstract Class Instantiation Fixes
# -----------------------------------------------------------------------------


# PROBLEMATIC - Abstract class that's being directly instantiated
class AbstractAgent(abc.ABC):
    """Abstract base class for agents."""

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config

    @abc.abstractmethod
    def process_data(self, data: Any) -> Any:
        """Process data (abstract method)."""
        pass

    @abc.abstractmethod
    def generate_response(self, query: str) -> str:
        """Generate a response (abstract method)."""
        pass


# INCORRECT Usage - Direct instantiation of abstract class
# agent = AbstractAgent(name="test", config={})  # This will raise TypeError


# CORRECT - Create a concrete subclass
class ConcreteAgent(AbstractAgent):
    """Concrete implementation of AbstractAgent."""

    def process_data(self, data: Any) -> Any:
        """Implement the abstract method."""
        return f"Processed: {data}"

    def generate_response(self, query: str) -> str:
        """Implement the abstract method."""
        return f"Response to: {query}"


# CORRECT Usage - Instantiate the concrete subclass
# agent = ConcreteAgent(name="test", config={})


# ALTERNATIVE - Factory method to create appropriate agent
def create_agent(agent_type: str, name: str, config: dict[str, Any]) -> AbstractAgent:
    """Factory method to create the appropriate agent type."""
    if agent_type == "concrete":
        return ConcreteAgent(name=name, config=config)
    elif agent_type == "specialized":
        return SpecializedAgent(name=name, config=config)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


# Another concrete implementation
class SpecializedAgent(AbstractAgent):
    """Specialized implementation of AbstractAgent."""

    def process_data(self, data: Any) -> Any:
        """Specialized data processing."""
        return f"Specialized processing: {data}"

    def generate_response(self, query: str) -> str:
        """Specialized response generation."""
        return f"Specialized response to: {query}"


# -----------------------------------------------------------------------------
# 2. Constructor/Method Argument Mismatch Fixes
# -----------------------------------------------------------------------------


# PROBLEMATIC - Class with specific expected arguments
class ConfigurationManager:
    """Configuration manager with specific expected arguments."""

    def __init__(
        self, config_path: str, enable_caching: bool = True, refresh_interval: int = 300
    ):
        self.config_path = config_path
        self.enable_caching = enable_caching
        self.refresh_interval = refresh_interval


# INCORRECT Usage - Missing or unexpected arguments
# config_mgr = ConfigurationManager()  # Missing required argument
# config_mgr = ConfigurationManager("config.json", cache_ttl=60)  # Unexpected argument


# CORRECT Usage - Proper arguments matching the constructor
# config_mgr = ConfigurationManager(config_path="config.json", enable_caching=True)


# IMPROVED - Using dataclass for clearer parameter structure
@dataclass
class ProcessingConfig:
    """Processing configuration with well-defined parameters."""

    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1000
    cache_ttl_minutes: int = 60
    enable_logging: bool = True


# CORRECT Usage with dataclass
# config = ProcessingConfig(model_name="gpt-4")


# IMPROVED - Add explicit validation for required parameters
class AIProcessingConfig:
    """AI processing configuration with validation."""

    def __init__(
        self,
        embedding_model: str,
        llm_model: str,
        enable_caching: bool = True,
        cache_ttl_minutes: int = 60,
    ):
        # Validate required parameters
        if not embedding_model:
            raise ValueError("embedding_model is required")
        if not llm_model:
            raise ValueError("llm_model is required")

        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.enable_caching = enable_caching
        self.cache_ttl_minutes = cache_ttl_minutes


# -----------------------------------------------------------------------------
# 3. Class Duplication Fixes
# -----------------------------------------------------------------------------

# PROBLEMATIC - Duplicate class definitions


# First definition (in one file)
class SlackAnalysisAgent:
    """Slack analysis agent - first definition."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def analyze_conversation(self, conversation_id: str) -> dict[str, Any]:
        """Analyze a Slack conversation."""
        return {"id": conversation_id, "sentiment": 0.8}


# Second definition (in another file) - Duplicate!
# class SlackAnalysisAgent:  # This causes a name collision
#     """Slack analysis agent - second definition."""
#
#     def __init__(self, credentials: Dict[str, str]):
#         self.credentials = credentials
#
#     def process_channel(self, channel_id: str) -> List[Dict[str, Any]]:
#         """Process a Slack channel."""
#         return [{"channel": channel_id, "activity": "high"}]


# CORRECT - Rename one of the classes to avoid collision
class SlackChannelAnalyzer:
    """Renamed class to avoid collision with SlackAnalysisAgent."""

    def __init__(self, credentials: dict[str, str]):
        self.credentials = credentials

    def process_channel(self, channel_id: str) -> list[dict[str, Any]]:
        """Process a Slack channel."""
        return [{"channel": channel_id, "activity": "high"}]


# ALTERNATIVE - Use namespaces or modules to organize related classes
class SlackAnalysis:
    """Namespace class for Slack analysis functionality."""

    class ConversationAnalyzer:
        """Analyzes individual conversations."""

        def __init__(self, api_key: str):
            self.api_key = api_key

        def analyze_conversation(self, conversation_id: str) -> dict[str, Any]:
            """Analyze a Slack conversation."""
            return {"id": conversation_id, "sentiment": 0.8}

    class ChannelAnalyzer:
        """Analyzes entire channels."""

        def __init__(self, credentials: dict[str, str]):
            self.credentials = credentials

        def process_channel(self, channel_id: str) -> list[dict[str, Any]]:
            """Process a Slack channel."""
            return [{"channel": channel_id, "activity": "high"}]


# -----------------------------------------------------------------------------
# 4. Member Access Before Definition Fixes
# -----------------------------------------------------------------------------


# PROBLEMATIC - Accessing class members before they're defined
class DataQuality:
    """Class with member access before definition issues."""

    def analyze_quality(self, data_point: float) -> None:
        """Analyze data point quality.
        ISSUE: Accessing self._quality_window before it's defined."""
        # This would cause an error if _quality_window isn't defined yet
        # self._quality_window.append(data_point)
        # if len(self._quality_window) > 100:
        #     self._quality_window.pop(0)
        pass


# CORRECT - Initialize all members in __init__
class ImprovedDataQuality:
    """Improved class with proper member initialization."""

    def __init__(self):
        """Initialize all class members."""
        self._quality_window = []
        self._threshold = 0.7
        self._total_processed = 0

    def analyze_quality(self, data_point: float) -> None:
        """Analyze data point quality."""
        self._quality_window.append(data_point)
        if len(self._quality_window) > 100:
            self._quality_window.pop(0)

        self._total_processed += 1


# -----------------------------------------------------------------------------
# 5. Function Call with No Return Value Fixes
# -----------------------------------------------------------------------------


# PROBLEMATIC - Function without return value being assigned
def run_cleanup_process() -> None:
    """Run cleanup process without returning a value."""
    print("Cleaning up resources...")
    # No return statement


# INCORRECT Usage - Assigning result of void function
# result = run_cleanup_process()  # result will be None


# CORRECT - Function with proper return value
def run_cleanup_process_with_result() -> dict[str, Any]:
    """Run cleanup process and return a result."""
    print("Cleaning up resources...")
    return {
        "status": "success",
        "items_cleaned": 5,
        "timestamp": "2025-06-28T12:00:00Z",
    }


# CORRECT Usage - Assign result of function that returns a value
# result = run_cleanup_process_with_result()


# CORRECT - Don't assign if no return value needed
# run_cleanup_process()  # No assignment


# -----------------------------------------------------------------------------
# 6. Too Many Arguments for Logging Format String Fixes
# -----------------------------------------------------------------------------


# PROBLEMATIC - Logging with mismatched format specifiers and arguments
def problematic_logging():
    """Logging with mismatched format specifiers and arguments."""
    import logging

    logging.getLogger(__name__)

    # Too many arguments for format string
    # logger.info("Processing item %s", "item1", "extra_arg")

    # Not enough arguments for format string
    # logger.error("Error processing items %s and %s", "item1")


# CORRECT - Match format specifiers with arguments
def correct_logging():
    """Logging with properly matched format specifiers and arguments."""
    import logging

    logger = logging.getLogger(__name__)

    # Correct number of arguments
    logger.info("Processing item %s", "item1")
    logger.error("Error processing items %s and %s", "item1", "item2")

    # Alternative using format dictionary
    logger.info(
        "Processing %(item_type)s: %(item_id)s",
        {"item_type": "document", "item_id": "doc123"},
    )


# -----------------------------------------------------------------------------
# 7. Generic Type Improvements
# -----------------------------------------------------------------------------

T = TypeVar("T")
U = TypeVar("U")


# IMPROVED - Using generic types for better type checking
class Repository(Generic[T]):
    """Generic repository for any entity type."""

    def __init__(self):
        self.items: dict[str, T] = {}

    def add(self, id: str, item: T) -> None:
        """Add an item to the repository."""
        self.items[id] = item

    def get(self, id: str) -> T | None:
        """Get an item from the repository."""
        return self.items.get(id)


# Usage example with type checking
# user_repo: Repository[User] = Repository()
# user_repo.add("user1", User(name="Alice"))
# user: Optional[User] = user_repo.get("user1")


# -----------------------------------------------------------------------------
# 8. Dependency Injection for Testability
# -----------------------------------------------------------------------------


# IMPROVED - Using dependency injection for better testability
class ServiceWithDependencies:
    """Service class with dependency injection."""

    def __init__(self, database_client, cache_service, logger):
        """Initialize with injected dependencies."""
        self.db = database_client
        self.cache = cache_service
        self.logger = logger

    def process_request(self, request_id: str) -> dict[str, Any]:
        """Process a request using injected dependencies."""
        self.logger.info("Processing request %s", request_id)

        # Try cache first
        cached = self.cache.get(request_id)
        if cached:
            return cached

        # Fall back to database
        result = self.db.fetch(request_id)
        self.cache.set(request_id, result)
        return result


if __name__ == "__main__":
    # Example usage of the patterns
    print("Code Style Fixes Examples")

    # Abstract class example
    agent = ConcreteAgent(name="test_agent", config={"model": "gpt-4"})
    response = agent.generate_response("Hello")
    print(f"Agent response: {response}")

    # Dataclass config example
    config = ProcessingConfig(model_name="gpt-4")
    print(f"Config: {config}")

    # Slack analysis namespace example
    conversation_analyzer = SlackAnalysis.ConversationAnalyzer(api_key="test-api-key")
    result = conversation_analyzer.analyze_conversation("conv123")
    print(f"Analysis result: {result}")

    print("\nREMEMBER: Always follow good code style practices!")
    print("- Use concrete classes instead of abstract classes")
    print("- Match constructor arguments correctly")
    print("- Avoid class name duplications")
    print("- Initialize all class members in __init__")
    print("- Return values from functions when needed")
    print("- Match logging format specifiers with arguments")
