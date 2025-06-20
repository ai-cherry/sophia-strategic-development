"""
Demonstrates a high-level content strategy workflow using Sophia's agents.
"""
import asyncio
import logging

from backend.agents.brain_agent import BrainAgent
from backend.agents.core.base_agent import AgentConfig, Task
from backend.integrations.portkey_client import PortkeyClient # Assuming it exists

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_content_creation_task(topic: str):
    """
    Orchestrates a content creation task from research to final draft.
    
    Args:
        topic: The high-level topic for the content (e.g., a blog post title).
    """
    logger.info(f"--- Starting Content Creation Workflow for: '{topic}' ---")
    
    # In a real system, the BrainAgent would be a long-running service.
    # Here, we instantiate it for this specific task.
    # The PortkeyClient would also be properly initialized.
    brain_agent = BrainAgent(
        AgentConfig(name="BrainAgent"), 
        portkey_client=PortkeyClient() # Placeholder
    )

    # This is a conceptual plan that the BrainAgent would generate and execute.
    # This demonstrates how the different agents and tools would be used.
    
    # Step 1: BrainAgent deconstructs the topic into a research query.
    research_query = f"Comprehensive competitive analysis: Pay Ready vs. {topic}"
    logger.info(f"[BRAIN] Generated research query: '{research_query}'")

    # Step 2: BrainAgent delegates to the ResearchAgent.
    # In a real system, this would be a tool call: `research.run_research(topic=...)`
    logger.info("[BRAIN] Delegating to ResearchAgent...")
    # research_brief = await research_agent.execute_task(Task(command=research_query))
    research_brief = {"output": f"This is a detailed brief comparing Pay Ready and {topic}..."} # Simulated result
    logger.info("[RESEARCH AGENT] Research complete.")

    # Step 3: BrainAgent uses the research to generate a blog post draft.
    logger.info("[BRAIN] Generating blog post draft from research...")
    drafting_prompt = f"""
    You are an expert content writer for Pay Ready, specializing in the property management industry.
    Using the following research brief, write a compelling blog post titled '{topic}'.
    The tone should be professional, confident, and highlight Pay Ready's key advantages.
    
    Research Brief:
    ---
    {research_brief['output']}
    ---
    """
    # This would be an LLM call, likely using the `generate_code` tool in a 'generate_text' mode.
    # final_draft = await brain_agent.generate_text(drafting_prompt) 
    final_draft = f"<h1>{topic}</h1>\n\n<p>Here is the compelling blog post content...</p>" # Simulated result
    logger.info("[BRAIN] Draft generation complete.")

    print("\n--- FINAL CONTENT DRAFT ---")
    print(final_draft)
    print("--------------------------")

if __name__ == "__main__":
    content_topic = "Why Pay Ready is the Superior Choice Over Entrata"
    asyncio.run(run_content_creation_task(content_topic)) 