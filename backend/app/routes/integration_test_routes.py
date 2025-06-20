"""Integration Test Routes
Provides endpoints to test all external service connections
"""

import os
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends

# Import integration modules
try:
    from backend.integrations.gong.gong_integration import GongIntegration
    from backend.integrations.linear_integration import LinearIntegration
    from backend.integrations.openai_integration import OpenAIIntegration
    from backend.integrations.pinecone_integration import PineconeIntegration
    from backend.integrations.slack.slack_integration import SlackIntegration
    from backend.integrations.snowflake_integration import SnowflakeIntegration
except ImportError:
    # Fallback imports if module structure is different
    pass

from backend.app.dependencies import get_admin_key

router = APIRouter(
    prefix="/api/integrations",
    tags=["integrations"],
    dependencies=[Depends(get_admin_key)],
)


@router.get("/test-all")
async def test_all_integrations() -> Dict[str, Any]:
    """Test all integrations and return status"""
    results = {}

    # Test each integration
    results["snowflake"] = await test_snowflake_internal()
    results["gong"] = await test_gong_internal()
    results["slack"] = await test_slack_internal()
    results["pinecone"] = await test_pinecone_internal()
    results["linear"] = await test_linear_internal()
    results["openai"] = await test_openai_internal()

    # Overall status
    all_connected = all(r.get("connected", False) for r in results.values())

    return {
        "status": "healthy" if all_connected else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "integrations": results,
    }


@router.get("/snowflake/test")
async def test_snowflake() -> Dict[str, Any]:
    """Test Snowflake connection"""
    return await test_snowflake_internal()


async def test_snowflake_internal() -> Dict[str, Any]:
    """Internal Snowflake test logic"""
    try:
        # Check if credentials exist
        if not all(
            [
                os.getenv("SNOWFLAKE_ACCOUNT"),
                os.getenv("SNOWFLAKE_USER"),
                os.getenv("SNOWFLAKE_PASSWORD"),
            ]
        ):
            return {"connected": False, "error": "Missing Snowflake credentials"}

        # Try to initialize and test connection
        snowflake = SnowflakeIntegration()

        # Simple query to test connection
        result = await snowflake.execute_query("SELECT CURRENT_VERSION()")

        return {
            "connected": True,
            "database": os.getenv("SNOWFLAKE_DATABASE", "SOPHIA_AI"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            "version": result[0][0] if result else "Unknown",
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/gong/test")
async def test_gong() -> Dict[str, Any]:
    """Test Gong connection"""
    return await test_gong_internal()


async def test_gong_internal() -> Dict[str, Any]:
    """Internal Gong test logic"""
    try:
        # Check if credentials exist
        if not all([os.getenv("GONG_ACCESS_KEY"), os.getenv("GONG_ACCESS_KEY_SECRET")]):
            return {"connected": False, "error": "Missing Gong credentials"}

        # Try to initialize and test connection
        gong = GongIntegration()

        # Get recent calls to test connection
        calls = await gong.get_recent_calls(limit=1)

        return {
            "connected": True,
            "call_count": len(calls) if calls else 0,
            "api_version": "v2",
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/slack/test")
async def test_slack() -> Dict[str, Any]:
    """Test Slack connection"""
    return await test_slack_internal()


async def test_slack_internal() -> Dict[str, Any]:
    """Internal Slack test logic"""
    try:
        # Check if credentials exist
        if not os.getenv("SLACK_BOT_TOKEN"):
            return {"connected": False, "error": "Missing Slack bot token"}

        # Try to initialize and test connection
        slack = SlackIntegration()

        # Test auth
        auth_test = await slack.test_auth()

        return {
            "connected": True,
            "workspace": auth_test.get("team", "Unknown"),
            "bot_name": auth_test.get("bot", {}).get("name", "sophia-ai"),
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/pinecone/test")
async def test_pinecone() -> Dict[str, Any]:
    """Test Pinecone connection"""
    return await test_pinecone_internal()


async def test_pinecone_internal() -> Dict[str, Any]:
    """Internal Pinecone test logic"""
    try:
        # Check if credentials exist
        if not os.getenv("PINECONE_API_KEY"):
            return {"connected": False, "error": "Missing Pinecone API key"}

        # Try to initialize and test connection
        pinecone = PineconeIntegration()

        # Get index stats
        stats = await pinecone.get_index_stats()

        return {
            "connected": True,
            "index": os.getenv("PINECONE_INDEX", "sophia-knowledge"),
            "environment": os.getenv("PINECONE_ENVIRONMENT", "us-east-1"),
            "vectors": stats.get("total_vector_count", 0),
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/linear/test")
async def test_linear() -> Dict[str, Any]:
    """Test Linear connection"""
    return await test_linear_internal()


async def test_linear_internal() -> Dict[str, Any]:
    """Internal Linear test logic"""
    try:
        # Check if credentials exist
        if not os.getenv("LINEAR_API_KEY"):
            return {"connected": False, "error": "Missing Linear API key"}

        # Try to initialize and test connection
        linear = LinearIntegration()

        # Get workspace info
        workspace = await linear.get_workspace()

        return {
            "connected": True,
            "workspace": workspace.get("name", "Unknown"),
            "organization": workspace.get("organization", {}).get("name", "Unknown"),
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/openai/test")
async def test_openai() -> Dict[str, Any]:
    """Test OpenAI connection"""
    return await test_openai_internal()


async def test_openai_internal() -> Dict[str, Any]:
    """Internal OpenAI test logic"""
    try:
        # Check if credentials exist
        if not os.getenv("OPENAI_API_KEY"):
            return {"connected": False, "error": "Missing OpenAI API key"}

        # Try to initialize and test connection
        openai = OpenAIIntegration()

        # Simple completion test
        response = await openai.create_completion(
            prompt="Say 'connection successful'", max_tokens=10
        )

        return {"connected": True, "model": "gpt-4", "response": response}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/health")
async def integration_health() -> Dict[str, Any]:
    """Quick health check for all integrations"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Use /test-all for detailed integration status",
    }
