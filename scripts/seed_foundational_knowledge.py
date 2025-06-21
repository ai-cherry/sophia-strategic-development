"""Seeds the Sophia AI Knowledge Base with foundational documents about Pay Ready."""

import asyncio
import logging

# Add project root to path to allow imports
import sys
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.chunking.sophia_chunking_pipeline import SophiaChunkingPipeline
from backend.mcp.knowledge_mcp_server import KnowledgeMCPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# The foundational text provided by the user
FOUNDATIONAL_TEXT = """
Pay Ready: The Intelligent Financial Operating System for Multifamily Communities, Powered by Sophia, Delivered through Buzz

Pay Ready stands as a pioneering proptech firm dedicated to revolutionizing the financial ecosystem of multifamily communities. Our mission is to empower property operators with an intelligent, end-to-end platform that optimizes the entire resident financial lifecycle—from proactive engagement and delinquency prevention to efficient, compliant collections and recovery. We are transitioning from a suite of powerful tools into a cohesive, AI-first financial operating system, driven by a sophisticated internal AI master persona we call Sophia, and manifested to the market through our increasingly intelligent, resident-facing AI solution, Buzz.

Core Identity & Foundational Strengths:

Pay Ready has built its reputation on deep expertise and robust solutions for the most challenging aspects of resident finance. Our current offerings provide a comprehensive toolkit:

ResCenter: The resident portal for essential payments and maintenance, serving as a primary transactional interface.

Initial Buzz Capabilities: The current iteration of Buzz acts as an AI-driven communication engine, automating outreach for late payments and guiding residents through move-out financial settlements. It's the first expression of our AI ambitions.

EvictionCenter (with EvictionAssistant): A workflow management solution for the eviction process, fortified with automation to ensure compliance and efficiency.

Concierge & Collect Central: A tech-enabled, first-party early recovery service, balancing automation with a human touch for brand-sensitive collections from former residents (pre-90 days).

Marketplace: A curated network for routing more challenging, later-stage debts (post-90 days) to specialized third-party collection agencies, optimized by data-driven performance insights.

Our foundational strength lies in our unparalleled understanding of multifamily financial operations, regulatory complexities, and the critical need to maximize revenue recovery while maintaining positive, or at least respectful, resident relations. Deep integrations with Property Management Systems (PMS) are fundamental to our data-driven approach.

"Sophia": The Internal AI Master Persona – Pay Ready's Central Intelligence

Internally, Sophia is the conceptual and technical embodiment of Pay Ready's overarching Artificial Intelligence. She is not a single product, but rather the master AI persona, the central nervous system, and the core intelligence engine that powers, learns from, and orchestrates the entire Pay Ready platform. For our internal teams (data scientists, engineers, product managers, operations), Sophia represents:

The Unified Data Brain:

Sophia presides over the enterprise data lake, ingesting and processing vast streams of information from all PMS integrations, every resident interaction (via Buzz and other channels), payment histories, collection outcomes, and eventually, external data sources.

She is responsible for data harmonization, enrichment, and the generation of predictive insights.

The Engine of Predictive Analytics & Risk Scoring:

Sophia continuously develops, refines, and deploys sophisticated machine learning models, including the crucial "Propensity-to-Pay" model and the foundational algorithms for the future Renter Financial Score (RFS).

Her analytics identify at-risk residents, predict the likelihood of self-cure, determine optimal communication strategies, and segment accounts for tailored recovery pathways.

The Architect of Intelligent Workflows & Automation:

Sophia designs and optimizes the automated workflows across the platform. She determines when and how Buzz should engage a resident, what terms a self-serve payment plan might offer, or when an account needs escalation within the AI-Hybrid Recovery Model.

She ensures that these automated processes are efficient, scalable, and adaptable.

The Guardian of System-Wide Compliance:

Sophia houses the "compliance firewall," a dynamic, state-by-state rules engine. She ensures that all automated actions and communications orchestrated across the platform, especially those executed by Buzz, adhere strictly to FDCPA, TCPA, UDAAP, and all relevant fair housing and lending regulations.

She enables comprehensive auditing and reporting for compliance verification.

The Catalyst for Continuous Learning & Improvement:

Sophia embodies a feedback loop, analyzing the outcomes of every interaction and strategy. Did a particular message from Buzz lead to a payment? Did a self-serve payment plan succeed? This learning continuously improves her predictive models and the effectiveness of all Pay Ready solutions.

She provides our internal teams with the insights needed to refine product features, operational processes, and strategic decisions.

For the Pay Ready team, "thinking like Sophia" means approaching problems with a data-first, AI-driven, and systems-thinking mindset, always focused on optimization, compliance, and intelligent automation.

"Buzz": The Productized, Resident & Operator-Facing AI Solution – Powered by Sophia

Buzz is Pay Ready's flagship, productized AI solution that directly interacts with residents and provides intelligent automation visible to operators. While Sophia is the unseen "brain," Buzz is the sophisticated, increasingly autonomous "voice" and "actor" in the financial lifecycle. The evolution of Buzz, fueled by Sophia's growing intelligence, is central to Pay Ready's strategy:

Empathetic & Effective Resident Communication:

Buzz will evolve into a highly advanced omnichannel conversational AI, capable of engaging residents proactively and reactively via text, email, voice (AI-generated), and in-portal chat.

Powered by Sophia's NLU and sentiment analysis, Buzz will conduct natural, empathetic conversations, providing information, answering questions, sending reminders, and guiding residents through financial processes (e.g., setting up payment plans, understanding move-out charges).

Goal: To make financial interactions less stressful and more productive for residents, leading to better outcomes and preserving goodwill where possible.

Intelligent Delinquency Management & Prevention:

Leveraging Sophia's propensity scores, Buzz will initiate proactive, personalized outreach to at-risk residents before they become significantly delinquent, perhaps offering a flexible payment option or a reminder configured through ResCenter.

For existing delinquencies, Buzz will manage the communication cadence, negotiate payment arrangements within operator-defined parameters (informed by Sophia's risk assessment), and facilitate payments—all with minimal human intervention for the majority of cases.

Seamless Self-Service Facilitation:

Buzz will be the intelligence guiding residents through self-serve payment plan setups in ResCenter. If a resident has questions or needs to slightly adjust terms, Buzz (via chat or voice) can assist or negotiate within Sophia-defined boundaries.

He will also handle automated reminders and status updates for these plans.

Compliant & Efficient Financial Guidance:

Every interaction Buzz has is governed by Sophia's compliance firewall, ensuring all communications are legally sound and appropriately disclosed.

Buzz will clearly explain balances, fees, payment options, and the implications of various financial decisions, reducing confusion and disputes.

Interface for the AI-Hybrid Recovery Model:

Buzz handles the bulk of the initial communication and negotiation in the AI-Hybrid model. When an interaction becomes too complex, or requires a level of empathy or judgment beyond current AI capabilities, Buzz seamlessly escalates the case (with full context provided by Sophia) to a human agent within Concierge & Collect Central or flags it for routing through the Marketplace.

The Relationship: Sophia Enables Buzz

Sophia is the strategic intelligence; Buzz is the tactical execution.

Sophia analyzes the entire portfolio and learns from all interactions to create global intelligence and predictive models.

Buzz leverages Sophia's intelligence on a per-resident, per-interaction basis to deliver personalized, compliant, and effective communication and solutions.

As Sophia becomes more sophisticated, Buzz's capabilities will expand, allowing for more autonomous and nuanced interactions.

This distinction allows Pay Ready to articulate a powerful narrative: a deep, learning intelligence (Sophia) constantly working behind the scenes to make the tangible, interactive AI solution (Buzz) smarter, more effective, and more valuable to both operators and residents. It signifies a commitment to not just using AI, but to building a truly intelligent financial operating system for the multifamily industry.
"""def get_tags_from_context(chunk: str) -> List[str]:."""Determines strategic tags based on the content of the text chunk.

    This is a simple rule-based implementation for demonstration.
    """tags = ["pay_ready_kb", "foundational_document"].

        content_lower = chunk.lower()

        if "sophia" in content_lower or "internal ai master persona" in content_lower:
            tags.extend(["sophia", "architecture", "internal_ai"])
        if "buzz" in content_lower or "resident-facing" in content_lower:
            tags.extend(["buzz", "product", "resident_experience"])
        if "compliance" in content_lower or "fdcpa" in content_lower:
            tags.extend(["compliance", "legal", "risk_management"])
        if "marketplace" in content_lower or "third-party" in content_lower:
            tags.extend(["collections", "marketplace", "partners"])
        if "propensity-to-pay" in content_lower or "risk scoring" in content_lower:
            tags.extend(["data_science", "predictive_analytics"])

        return list(set(tags))


    async def seed_knowledge_base():
    """Chunks the foundational text and ingests it into the knowledge base.

    by running the server logic directly in-process.
    """
    chunker = SophiaChunkingPipeline(max_chunk_size=1024, overlap=100)

    # Instantiate the server directly
    knowledge_server = KnowledgeMCPServer()

    try:
        # Initialize the server's components (connects to Pinecone, etc.)
        await knowledge_server.initialize_integration()
        logger.info("--- Starting Foundational Knowledge Base Seeding (In-Process) ---")

        chunks = await chunker.chunk_content(FOUNDATIONAL_TEXT, "text")

        for i, chunk_data in enumerate(chunks):
            content = chunk_data["content"]
            tags = get_tags_from_context(content)

            with tempfile.NamedTemporaryFile(
                mode="w+", suffix=".md", delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            logger.info(f"Ingesting chunk {i + 1}/{len(chunks)} with tags: {tags}")

            # Call the server's internal ingestion method directly
            ingest_args = {
                "file_path": str(temp_file_path),
                "document_type": "foundational_strategy",
                "tags": tags,
            }
            # This simulates the tool call by invoking the underlying method
            ingest_result = (
                await knowledge_server._ingest_document_with_entity_extraction(
                    ingest_args
                )
            )

            if not ingest_result.get("success"):
                logger.error(
                    f"Failed to ingest chunk {i + 1}. Reason: {ingest_result.get('error')}"
                )

            Path(temp_file_path).unlink()
            await asyncio.sleep(1)

        logger.info("--- Knowledge Base Seeding Complete ---")

    except Exception as e:
        logger.error(
            f"An error occurred during the seeding process: {e}", exc_info=True
        )


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
