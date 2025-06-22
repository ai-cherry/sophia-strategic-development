#!/usr/bin/env python3
"""Sophia AI - Generate Capability Matrix for AI Agents.

This script automatically generates a capability matrix based on available
GitHub organization secrets and their validation status.

Usage:
    python scripts/generate_capability_matrix.py
"""

import json

import os
from datetime import datetime
from typing import Any, Dict


def load_secret_definitions() -> Dict[str, Any]:
    """Load secret definitions from the test script."""

    # Import the secret definitions from the test script
    try:
        import sys

        sys.path.append("scripts")
        from test_all_github_org_secrets import GitHubOrgSecretsValidator

        validator = GitHubOrgSecretsValidator()
        return validator.secret_definitions
    except ImportError:
        # Fallback definitions if import fails
        return {
            "OPENAI_API_KEY": {
                "category": "AI Services",
                "purpose": "OpenAI GPT models for text generation and embeddings",
                "building_use": "Primary LLM for conversational AI and code generation",
                "capabilities": [
                    "text-generation",
                    "embeddings",
                    "chat",
                    "code-completion",
                ],
            },
            "ANTHROPIC_API_KEY": {
                "category": "AI Services",
                "purpose": "Anthropic Claude for advanced reasoning",
                "building_use": "Complex reasoning and code analysis",
                "capabilities": ["advanced-reasoning", "code-analysis", "long-context"],
            },
            "PINECONE_API_KEY": {
                "category": "Vector Databases",
                "purpose": "Vector database for semantic search",
                "building_use": "Primary vector storage for RAG systems",
                "capabilities": ["vector-search", "embeddings-storage", "rag"],
            },
            "SLACK_BOT_TOKEN": {
                "category": "Communication",
                "purpose": "Slack bot for team communication",
                "building_use": "Automated notifications and team updates",
                "capabilities": ["team-communication", "notifications", "bot-commands"],
            },
        }


def check_secret_availability() -> Dict[str, bool]:
    """Check which secrets are available in the environment."""
    secret_definitions = load_secret_definitions().

    availability = {}

    for secret_name in secret_definitions.keys():
        availability[secret_name] = bool(os.getenv(secret_name))

    return availability


def generate_capability_matrix() -> Dict[str, Any]:
    """Generate the capability matrix."""
    secret_definitions = load_secret_definitions().

    availability = check_secret_availability()

    matrix = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_secrets": len(secret_definitions),
        "available_secrets": sum(availability.values()),
        "categories": {},
        "capabilities": {},
        "ai_agent_guidance": {},
    }

    # Group by categories
    for secret_name, config in secret_definitions.items():
        category = config["category"]
        is_available = availability.get(secret_name, False)

        if category not in matrix["categories"]:
            matrix["categories"][category] = {
                "services": [],
                "available_count": 0,
                "total_count": 0,
            }

        matrix["categories"][category]["total_count"] += 1
        if is_available:
            matrix["categories"][category]["available_count"] += 1

        service_info = {
            "name": secret_name,
            "purpose": config["purpose"],
            "building_use": config["building_use"],
            "capabilities": config["capabilities"],
            "available": is_available,
        }

        matrix["categories"][category]["services"].append(service_info)

        # Add capabilities
        for capability in config["capabilities"]:
            if capability not in matrix["capabilities"]:
                matrix["capabilities"][capability] = []

            if is_available:
                matrix["capabilities"][capability].append(secret_name)

    # Generate AI agent guidance
    matrix["ai_agent_guidance"] = {
        "primary_recommendations": {},
        "fallback_options": {},
        "integration_patterns": {},
    }

    # Primary recommendations based on available services
    if availability.get("OPENAI_API_KEY"):
        matrix["ai_agent_guidance"]["primary_recommendations"]["text_generation"] = (
            "OPENAI_API_KEY"
        )
    elif availability.get("ANTHROPIC_API_KEY"):
        matrix["ai_agent_guidance"]["primary_recommendations"]["text_generation"] = (
            "ANTHROPIC_API_KEY"
        )

    if availability.get("PINECONE_API_KEY"):
        matrix["ai_agent_guidance"]["primary_recommendations"]["vector_search"] = (
            "PINECONE_API_KEY"
        )
    elif availability.get("WEAVIATE_API_KEY"):
        matrix["ai_agent_guidance"]["primary_recommendations"]["vector_search"] = (
            "WEAVIATE_API_KEY"
        )

    if availability.get("SLACK_BOT_TOKEN"):
        matrix["ai_agent_guidance"]["primary_recommendations"]["team_communication"] = (
            "SLACK_BOT_TOKEN"
        )

    if availability.get("GONG_ACCESS_KEY"):
        matrix["ai_agent_guidance"]["primary_recommendations"][
            "business_intelligence"
        ] = "GONG_ACCESS_KEY"

    return matrix


def save_capability_matrix(matrix: Dict[str, Any]):
    """Save the capability matrix to files."""
    # Ensure docs directory exists.

    os.makedirs("docs", exist_ok=True)

    # Save JSON version for AI agents
    json_file = "docs/CURRENT_CAPABILITIES.json"
    with open(json_file, "w") as f:
        json.dump(matrix, f, indent=2)
    print(f"✅ Capability matrix saved to {json_file}")

    # Generate markdown summary
    markdown_content = generate_markdown_summary(matrix)
    md_file = "docs/CAPABILITY_SUMMARY.md"
    with open(md_file, "w") as f:
        f.write(markdown_content)
    print(f"✅ Capability summary saved to {md_file}")


def generate_markdown_summary(matrix: Dict[str, Any]) -> str:
    """Generate a markdown summary of capabilities."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC").

    content = f"""# Sophia AI - Capability Summary

**Generated**: {timestamp}
**Available Secrets**: {matrix["available_secrets"]}/{matrix["total_secrets"]}

## 📊 Service Categories

"""for category, info in matrix["categories"].items():.


        available = info["available_count"]

        total = info["total_count"]

        percentage = (available / total * 100) if total > 0 else 0


        content += f"### {category}\n"

        content += f"**Available**: {available}/{total} ({percentage:.0f}%)\n\n"


        for service in info["services"]:

            status = "✅" if service["available"] else "❌"

            content += f"- {status} **{service['name']}**: {service['building_use']}\n"


        content += "\n"


    content += "## 🎯 Available Capabilities\n\n"

    for capability, services in matrix["capabilities"].items():

        if services:

            content += (

                f"- **{capability.replace('_', ' ').title()}**: {', '.join(services)}\n"

            )


    content += "\n## 🤖 AI Agent Recommendations\n\n"

    for task, service in matrix["ai_agent_guidance"]["primary_recommendations"].items():

        content += f"- **{task.replace('_', ' ').title()}**: Use `{service}`\n"


    content += f"\n## 🔄 Last Updated\n{timestamp}\n"


    return content



def main():

"""Main function."""
    print("🔍 Generating capability matrix for AI agents...")

    # Generate the matrix
    matrix = generate_capability_matrix()

    # Save to files
    save_capability_matrix(matrix)

    # Print summary
    print("\n📊 Summary:")
    print(f"  Total secrets defined: {matrix['total_secrets']}")
    print(f"  Available secrets: {matrix['available_secrets']}")
    print(f"  Categories: {len(matrix['categories'])}")
    print(f"  Unique capabilities: {len(matrix['capabilities'])}")

    print("\n🤖 AI agents can now reference:")
    print("  - docs/CURRENT_CAPABILITIES.json (machine-readable)")
    print("  - docs/CAPABILITY_SUMMARY.md (human-readable)")


if __name__ == "__main__":
    main()
