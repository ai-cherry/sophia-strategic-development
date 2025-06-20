from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_v1_health_check():
    """Test the /api/v1/health endpoint to ensure it's operational."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert json_response["version"] == "v1"
