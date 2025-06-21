"""Agno-Native Tools for the AI Design Assistant.

These tools allow a specialized agent to programmatically create and modify
frontend components, enabling an AI-driven design and development workflow.
"""import logging

from pathlib import Path

logger = logging.getLogger(__name__)

# Define a safe, sandboxed directory where the agent can write files.
# This prevents it from modifying files outside the intended scope.
SAFE_COMPONENTS_DIR = Path("sophia-dashboard/src/components/generated")


def create_react_component(component_name: str, jsx_code: str) -> str:
    """Creates a new React component file in the sandboxed 'generated' directory.

            This is a powerful tool. In a production environment, it should have
            strict security controls and require human approval before code is merged.

            :param component_name: The name of the component (e.g., 'KpiCardRevenue').
                                   This will be used to create the filename.
            :param jsx_code: A string containing the full, valid JSX code for the component.
            :return: A confirmation message with the path to the created file.
    """
    if ".." in component_name or "/" in component_name:
        raise ValueError(
            "Invalid component name. Must not contain path traversal characters."
        )

    # Ensure the sandboxed directory exists.
    SAFE_COMPONENTS_DIR.mkdir(parents=True, exist_ok=True)

    file_path = SAFE_COMPONENTS_DIR / f"{component_name}.jsx"

    logger.info(f"Design Agent is creating a new component at: {file_path}")

    try:
        with open(file_path, "w") as f:
            f.write(jsx_code)

        confirmation_message = f"Successfully created React component at {file_path}. A developer should now review and integrate it."
        logger.info(confirmation_message)
        return confirmation_message
    except Exception as e:
        logger.error(f"Failed to create React component: {e}", exc_info=True)
        raise


# Dictionary of tools for registration in the AgentFramework
design_tools = {
    "create_react_component": create_react_component,
}
