"""
Builds the initial Pay Ready Knowledge Base using the ResearchAgent.
"""
import asyncio
import logging
import tempfile
from pathlib import Path

from backend.agents.specialized.research_agent import ResearchAgent
from backend.agents.core.base_agent import AgentConfig, Task
from backend.mcp.mcp_client import MCPClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Research Topics ---
RESEARCH_TOPICS = [
    "Comprehensive analysis of Entrata property management software",
    "Comprehensive analysis of Yardi Voyager property management software",
    "Comprehensive analysis of RealPage property management software",
    "Top 3 challenges in the property management industry 2024",
    "Key takeaways from the '2024 State of the Property Management Industry' report",
    "Key takeaways from the 'NMHC/Grace Hill Renter Preferences Survey' report"
]

async def run_knowledge_base_build():
    """
    Orchestrates the creation of the mini Pay Ready knowledge base.
    """
    research_agent = ResearchAgent(AgentConfig(name="ResearchAgent"))
    mcp_client = MCPClient("http://localhost:8090")
    
    try:
        await mcp_client.connect()
        logger.info("--- Starting Knowledge Base Build ---")
        
        for topic in RESEARCH_TOPICS:
            logger.info(f"--- Researching Topic: {topic} ---")
            
            # 1. Use the ResearchAgent to get a brief on the topic
            research_task = Task(command=topic)
            research_result = await research_agent.execute_task(research_task)
            
            if research_result.status != "success":
                logger.error(f"Research failed for topic: {topic}. Error: {research_result.output}")
                continue
                
            brief_content = research_result.output
            logger.info(f"Successfully generated research brief for '{topic}'.")
            
            # 2. Ingest the resulting brief into our knowledge base
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False) as temp_file:
                temp_file.write(brief_content)
                temp_file_path = temp_file.name
            
            logger.info(f"Ingesting brief into Knowledge Base from temp file: {temp_file_path}")
            
            ingest_result = await mcp_client.call_tool(
                "knowledge",
                "ingest_document",
                file_path=str(temp_file_path),
                document_type="research_brief",
                tags=["pay_ready_kb", topic.replace(" ", "_").lower()]
            )
            
            if ingest_result.get("success"):
                logger.info(f"Successfully ingested brief for '{topic}'.")
            else:
                logger.error(f"Failed to ingest brief for '{topic}'. Reason: {ingest_result.get('error')}")
            
            # Clean up the temporary file
            Path(temp_file_path).unlink()

        logger.info("--- Knowledge Base Build Complete ---")

    finally:
        await mcp_client.close()


if __name__ == "__main__":
    # Assumes the necessary MCP servers are running
    # docker-compose up -d apify-mcp knowledge-mcp
    asyncio.run(run_knowledge_base_build()) 