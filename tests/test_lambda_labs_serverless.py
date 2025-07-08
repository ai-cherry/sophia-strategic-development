"""Tests for Lambda Labs serverless service."""

import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch

import pytest  # type: ignore[import-not-found]

from infrastructure.services.lambda_labs_serverless_service import (
    LambdaLabsServerlessService,
)


@pytest.fixture
def mock_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_usage.db"
    return str(db_path)


@pytest.fixture
def service(mock_db):
    """Create service instance with mocked API key."""
    with patch(
        "infrastructure.services.lambda_labs_serverless_service.get_config_value"
    ) as mock_config:
        mock_config.return_value = "test-api-key"
        return LambdaLabsServerlessService(db_path=mock_db)


@pytest.mark.asyncio
async def test_generate_success(service):
    """Test successful generation with cost tracking."""
    # Mock the API response
    mock_response = {
        "choices": [{"message": {"content": "Test response"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
        "model": "llama3.1-70b-instruct-fp8",
    }

    with patch("aiohttp.ClientSession") as mock_session:
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_resp.raise_for_status = MagicMock()

        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
            mock_resp
        )

        result = await service.generate(
            messages=[{"role": "user", "content": "Hello"}],
            user_id="test-user",
            session_id="test-session",
        )

    assert result["choices"][0]["message"]["content"] == "Test response"
    assert result["usage"]["total_tokens"] == 150

    # Verify usage was tracked
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usage")
    assert cursor.fetchone()[0] == 1

    cursor.execute("SELECT model, tokens, cost FROM usage")
    row = cursor.fetchone()
    assert row[0] == "llama3.1-70b-instruct-fp8"
    assert row[1] == 150
    assert row[2] == pytest.approx(0.0000525, rel=1e-4)  # 150/1M * 0.35
    conn.close()


@pytest.mark.asyncio
async def test_generate_retry_on_failure(service):
    """Test retry logic on API failure."""
    call_count = 0

    async def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("API Error")

        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(
            return_value={
                "choices": [{"message": {"content": "Success after retry"}}],
                "usage": {"total_tokens": 100},
            }
        )
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.post = mock_post

        result = await service.generate(messages=[{"role": "user", "content": "Test"}])

    assert call_count == 3
    assert result["choices"][0]["message"]["content"] == "Success after retry"


@pytest.mark.asyncio
async def test_generate_invalid_model(service):
    """Test error handling for invalid model."""
    with pytest.raises(ValueError, match="Unknown model"):
        await service.generate(
            messages=[{"role": "user", "content": "Test"}], model="invalid-model"
        )


def test_get_usage_stats(service):
    """Test usage statistics retrieval."""
    # Insert test data
    conn = sqlite3.connect(service.db_path)
    test_data = [
        (1234567890, "llama3.1-8b-instruct", 1000, 0.00007, 150, "user1", "session1"),
        (1234567891, "llama3.1-8b-instruct", 2000, 0.00014, 200, "user1", "session2"),
        (
            1234567892,
            "llama3.1-70b-instruct-fp8",
            3000,
            0.00105,
            300,
            "user2",
            "session3",
        ),
    ]

    for data in test_data:
        conn.execute(
            "INSERT INTO usage (timestamp, model, tokens, cost, latency_ms, user_id, session_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            data,
        )
    conn.commit()
    conn.close()

    # Get stats
    stats = service.get_usage_stats(days=30)

    assert "llama3.1-8b-instruct" in stats["model_stats"]
    assert stats["model_stats"]["llama3.1-8b-instruct"]["requests"] == 2
    assert stats["model_stats"]["llama3.1-8b-instruct"]["tokens"] == 3000
    assert stats["model_stats"]["llama3.1-8b-instruct"]["cost"] == pytest.approx(
        0.00021
    )
    assert stats["model_stats"]["llama3.1-8b-instruct"]["unique_users"] == 1

    assert "llama3.1-70b-instruct-fp8" in stats["model_stats"]
    assert stats["model_stats"]["llama3.1-70b-instruct-fp8"]["requests"] == 1
