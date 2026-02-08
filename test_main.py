from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys

# Mock transformers if it's still imported anywhere (though we removed it)
sys.modules["transformers"] = MagicMock()

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Plex ToDo AI"}

@patch("main.query_hf_api", new_callable=AsyncMock)
def test_parse_task_success(mock_query):
    # Mock the API response
    mock_query.return_value = {
        "choices": [
            {"message": {"content": '{"title": "Buy milk", "time": "17:00", "priority": "medium"}'}}
        ]
    }
    
    response = client.post("/parse-task", json={"text": "Buy milk at 5pm"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["time"] == "17:00"
    assert data["priority"] == "medium"

@patch("main.query_hf_api", new_callable=AsyncMock)
def test_parse_task_api_error(mock_query):
    # Mock API error
    mock_query.side_effect = Exception("Timeout")
    
    response = client.post("/parse-task", json={"text": "Buy milk"})
    assert response.status_code == 503
    assert "API Connection Error" in response.json()["detail"]
