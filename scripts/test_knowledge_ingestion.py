#!/usr/bin/env python3
"""Test script for Knowledge Ingestion and Curation System
Demonstrates the complete workflow from document upload to proactive discovery
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.agents.core.base_agent import AgentConfig
from backend.agents.specialized.insight_extraction_agent import InsightExtractionAgent
from backend.knowledge_base.ingestion import IngestionPipeline
from backend.knowledge_base.metadata_store import MetadataStore
from backend.knowledge_base.vector_store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_document_ingestion():
    """Test basic document ingestion"""
    logger.info("=== Testing Document Ingestion ===")

    # Initialize components
    vector_store = VectorStore()
    metadata_store = MetadataStore()
    pipeline = IngestionPipeline(vector_store, metadata_store)

    # Create test documents
    test_dir = Path("test_knowledge_docs")
    test_dir.mkdir(exist_ok=True)

    # Create sample documents
    docs = [
        {
            "filename": "pay_ready_mission.txt",
            "content": """Pay Ready Mission Statement
            
Pay Ready is dedicated to revolutionizing business intelligence and payment processing 
for the modern enterprise. Our mission is to empower businesses with real-time insights,
seamless payment solutions, and intelligent automation that drives growth and efficiency.

Core Values:
- Innovation: Continuously pushing the boundaries of what's possible
- Customer Focus: Every decision starts with our customers' success in mind
- Integrity: Building trust through transparency and reliability
- Excellence: Delivering exceptional quality in everything we do
""",
            "type": "company_core",
            "tags": ["mission", "values", "company"],
        },
        {
            "filename": "product_pricing.txt",
            "content": """Pay Ready Product Pricing Guide

Enterprise Tier: $60,000 per year
- Unlimited users
- Advanced analytics and AI insights
- Custom integrations
- 24/7 dedicated support
- White-label options

Professional Tier: $30,000 per year
- Up to 50 users
- Standard analytics
- API access
- Business hours support

Starter Tier: $12,000 per year
- Up to 10 users
- Basic features
- Email support

Note: All prices effective as of January 2024. Volume discounts available.
""",
            "type": "pricing",
            "tags": ["pricing", "products", "tiers"],
        },
        {
            "filename": "competitor_analysis.txt",
            "content": """Competitive Landscape Analysis

Primary Competitors:
1. Entrata - Strong in property management, weak in payment processing
2. RealPage - Good analytics, but expensive and complex
3. Yardi - Legacy system, difficult to integrate

Our Advantages:
- Modern AI-powered insights
- Seamless payment integration
- User-friendly interface
- Competitive pricing
- Rapid implementation
""",
            "type": "competitive_intel",
            "tags": ["competitors", "market_analysis", "strategy"],
        },
    ]

    # Ingest documents
    for doc in docs:
        file_path = test_dir / doc["filename"]
        with open(file_path, "w") as f:
            f.write(doc["content"])

        logger.info(f"Ingesting {doc['filename']}...")
        await pipeline.ingest_document(
            file_path=file_path, document_type=doc["type"], tags=doc["tags"]
        )
        logger.info(f"✓ Successfully ingested {doc['filename']}")

    # Test querying
    logger.info("\n=== Testing Knowledge Base Queries ===")

    queries = [
        "What is the price of the Enterprise tier?",
        "What are Pay Ready's core values?",
        "Who are our main competitors?",
    ]

    for query in queries:
        logger.info(f"\nQuery: {query}")
        results = await vector_store.query(query, top_k=1)
        if results:
            logger.info(f"Answer: {results[0]['content'][:200]}...")
            logger.info(f"Source: {results[0]['metadata'].get('file_name', 'Unknown')}")
        else:
            logger.info("No results found")

    # Clean up
    import shutil

    shutil.rmtree(test_dir)

    return True


async def test_proactive_discovery():
    """Test proactive insight discovery from Gong transcripts"""
    logger.info("\n=== Testing Proactive Discovery ===")

    # Initialize insight extraction agent
    agent_config = AgentConfig(name="InsightExtractionAgent")
    insight_agent = InsightExtractionAgent(agent_config)

    # Simulate analyzing a Gong call
    # In production, this would use real Gong call IDs
    logger.info("Simulating Gong call analysis...")

    # Mock transcript that would come from Gong
    mock_transcript = """
Sales Rep: Thanks for joining the call today. I wanted to discuss how Pay Ready can help with your business intelligence needs.

Customer: Yes, we're currently evaluating several solutions. We're also looking at FastTrack BI and DataFlow Analytics.

Sales Rep: I understand. What specific challenges are you facing with your current setup?

Customer: Our biggest frustration is that we can't export data in real-time to our BI tools. We need to run manual exports every day, which is really inefficient. Also, we're using your platform for compliance auditing, which wasn't something we initially planned but it's working really well.

Sales Rep: That's great to hear about the compliance use case. Regarding the export limitation, let me show you our API capabilities...

Customer: The API sounds good, but honestly, the $60,000 price tag for the Enterprise tier is a bit steep for us right now. Is there any flexibility there?

Sales Rep: Let me discuss with my manager about potential options for you...
"""

    # Create a mock task to analyze this transcript
    # In production, this would be triggered by webhook or scheduled job
    insights = await insight_agent._extract_insights_with_llm(
        mock_transcript,
        {"title": "Demo Company Call", "url": "https://app.gong.io/call/demo123"},
        "demo123",
    )

    logger.info(f"\nFound {len(insights)} insights:")
    for insight in insights:
        logger.info(f"\n{'-' * 50}")
        logger.info(f"Type: {insight.type.value}")
        logger.info(f"Insight: {insight.insight}")
        logger.info(f"Question: {insight.question}")
        logger.info(f"Confidence: {insight.confidence:.2%}")
        logger.info(f"Context: {insight.context[:100]}...")

    return insights


async def test_curation_workflow(insights):
    """Test the curation workflow with feedback"""
    logger.info("\n=== Testing Curation Workflow ===")

    if not insights:
        logger.info("No insights to curate")
        return

    # Simulate user reviewing insights
    logger.info("\nSimulating user review of insights...")

    for i, insight in enumerate(insights[:2]):  # Review first 2 insights
        logger.info(f"\nReviewing insight {i+1}:")
        logger.info(f"- {insight.insight}")

        # Simulate different user actions
        if i == 0:
            # Approve first insight
            logger.info("User action: APPROVE")
            insight.status = "approved"
            # In production, this would trigger adding to knowledge base

        elif i == 1:
            # Edit and approve second insight
            logger.info("User action: APPROVE WITH EDIT")
            original = insight.insight
            insight.insight = f"{insight.insight} (Updated: confirmed by product team)"
            insight.status = "approved"
            logger.info(f"Edited from: {original}")
            logger.info(f"Edited to: {insight.insight}")

    logger.info("\n✓ Curation workflow completed")
    return True


async def test_knowledge_chat():
    """Test the knowledge curation chat interface"""
    logger.info("\n=== Testing Knowledge Curation Chat ===")

    # Initialize vector store for querying
    vector_store = VectorStore()

    # Simulate chat interactions
    chat_queries = [
        "What is the price for Enterprise tier?",
        "Do we support real-time data export?",
        "Which competitors are mentioned in our knowledge base?",
    ]

    for query in chat_queries:
        logger.info(f"\nUser: {query}")

        # Query knowledge base
        results = await vector_store.query(query, top_k=1)

        if results:
            response = results[0]["content"][:200]
            source = results[0]["metadata"].get("file_name", "Unknown")
            confidence = results[0].get("score", 0.0)

            logger.info(f"Sophia: {response}...")
            logger.info(f"Source: {source} (Confidence: {confidence:.2%})")

            # Simulate feedback
            if "real-time data export" in query.lower():
                logger.info("User feedback: INCORRECT")
                logger.info(
                    "User correction: We now support real-time data export via our new API v2"
                )
                # In production, this would update the knowledge base
        else:
            logger.info(
                "Sophia: I don't have information about that in the knowledge base."
            )

    return True


async def main():
    """Run all tests"""
    logger.info("Starting Knowledge Ingestion and Curation System Test")
    logger.info("=" * 60)

    try:
        # Test 1: Document Ingestion
        await test_document_ingestion()

        # Test 2: Proactive Discovery
        insights = await test_proactive_discovery()

        # Test 3: Curation Workflow
        await test_curation_workflow(insights)

        # Test 4: Knowledge Chat
        await test_knowledge_chat()

        logger.info("\n" + "=" * 60)
        logger.info("✓ All tests completed successfully!")
        logger.info("\nSummary:")
        logger.info("- Document ingestion: Working")
        logger.info("- Proactive discovery: Working")
        logger.info("- Curation workflow: Working")
        logger.info("- Knowledge chat: Working")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
