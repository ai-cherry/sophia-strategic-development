from fastapi.testclient import TestClient
from simple_backend_api import app

client = TestClient(app)

def test_health_endpoint():
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json()['status'] == 'healthy'

def test_create_agent():
    resp = client.post('/api/v1/agents/create', json={'agent_type':'test','task':'t'})
    data = resp.json()
    assert resp.status_code == 200
    assert data['success']
    assert 'agent_id' in data
