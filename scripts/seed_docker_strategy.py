"""Seeds the Knowledge Base with the strategic document on Docker vs. Cloud."""

import asyncio
import logging

# Add project root to path
import sys
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.chunking.sophia_chunking_pipeline import SophiaChunkingPipeline
from backend.mcp.knowledge_mcp_server import KnowledgeMCPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

STRATEGY_DOCUMENT = """
# Comprehensive Analysis of Docker Local vs. Cloud (June 20, 2025)

## Key Points
- Running Docker locally is great for development and small-scale apps, but cloud Docker scales better for production, though it costs more.
- Pulumi enhances Docker with IaC, making container management easier across clouds.
- Vercel doesn't directly support Docker but works for local dev; Lambda Labs is perfect for AI with GPU-powered Docker setups.
- AI and MCP features in Docker, like Model Runner and Catalog, boost AI workflows, but they're still evolving—expect bugs.

---

## Direct Answer

#### Overview
Deciding between running Docker locally or in the cloud depends on your needs, budget, and patience for DevOps headaches. Local Docker is cheap and fast for tinkering, while cloud Docker scales for production but can drain your wallet. Let's break it down, focusing on Pulumi, Vercel, Lambda Labs, cloud, AI, and MCP.

#### Local vs. Cloud Docker
- **Local Docker**: Perfect for development, testing, and small apps. It's free (beyond your hardware's power bill), with no network lag, but your laptop's resources cap out fast. Scaling? Good luck, it's manual labor.
- **Cloud Docker**: Scales like a dream, with auto-scaling for traffic spikes, but costs can spiral out of control. Network latency slows you down, and debugging feels like yelling into the void.

#### Pulumi and Docker
Pulumi's Docker provider lets you manage containers as code, integrating with cloud builds like Docker Build Cloud. It's a lifesaver for automating workflows, ensuring consistency from dev to prod, but it's another layer of complexity to master.

#### Vercel and Docker
Vercel doesn't support Docker deployments directly—it's all serverless for frontends. Use Docker for local dev to keep things consistent, but for production, you'll need alternatives.

#### Lambda Labs and Docker
Lambda Labs is your AI buddy, offering Docker images with GPU power for deep learning. Perfect for training models, it's all about scaling AI workloads.

#### Cloud, AI, and MCP
Docker's cloud features, like Build Cloud, work with AI tools like Model Runner for local LLM packaging and MCP Catalog for secure AI agent integration. It's a mess of shiny toys, but they're still young—expect sharp edges.

---
"""def get_tags(chunk: str) -> list[str]:."""Determines tags based on chunk content."""

    tags = ["iac_strategy", "docker"]
    content_lower = chunk.lower()
    if "local docker" in content_lower:
        tags.append("local_docker")
    if "cloud docker" in content_lower:
        tags.append("cloud_docker")
    if "pulumi" in content_lower:
        tags.append("pulumi")
    if "vercel" in content_lower:
        tags.append("vercel")
    if "lambda labs" in content_lower:
        tags.append("lambda_labs")
    if "mcp" in content_lower:
        tags.append("mcp")
    return list(set(tags))


async def seed_docker_strategy():
    """Chunks and ingests the Docker strategy document directly."""
    chunker = SophiaChunkingPipeline(max_chunk_size=1024, overlap=100)
    knowledge_server = KnowledgeMCPServer()

    try:
        await knowledge_server.initialize_integration()
        logger.info("--- Seeding Docker & Cloud Strategy Document (In-Process) ---")

        chunks = await chunker.chunk_content(STRATEGY_DOCUMENT, "text")

        for i, chunk_data in enumerate(chunks):
            content = chunk_data["content"]
            tags = get_tags(content)

            with tempfile.NamedTemporaryFile(
                mode="w+", suffix=".md", delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            logger.info(f"Ingesting chunk {i + 1}/{len(chunks)} with tags: {tags}")

            ingest_args = {
                "file_path": str(temp_file_path),
                "document_type": "iac_strategy",
                "tags": tags,
            }
            ingest_result = (
                await knowledge_server._ingest_document_with_entity_extraction(
                    ingest_args
                )
            )

            if not ingest_result.get("success"):
                logger.error(
                    f"Failed to ingest chunk {i + 1}. Reason: {ingest_result.get('error')}"
                )
            else:
                logger.info(f"Successfully ingested chunk {i + 1}.")

            Path(temp_file_path).unlink()
            await asyncio.sleep(1)

        logger.info("--- Docker Strategy Seeding Complete ---")

    except Exception as e:
        logger.error(f"An error occurred during seeding: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(seed_docker_strategy())
