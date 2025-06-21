from fastapi.testclient import TestClient
from backend.main import app
from backend.core import security

client = TestClient(app)

VALID_KEY = next(iter(security.VALID_API_KEYS))


def test_dashboard_metrics_with_key():
    resp = client.get('/api/v1/dashboard/metrics', headers={security.API_KEY_NAME: VALID_KEY})
    assert resp.status_code == 200
    data = resp.json()
    assert 'revenue_growth' in data


def test_dashboard_metrics_missing_key():
    resp = client.get('/api/v1/dashboard/metrics')
    assert resp.status_code == 403
