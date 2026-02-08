from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_task_mode():
    print("\n--- Testing TASK Mode (Simple) ---")
    response = client.post("/ai", json={"text": "Buy milk tomorrow at 5pm"})
    print(f"Status: {response.status_code}")
    # ... check response ...

    print("\n--- Testing TASK Mode (Inference) ---")
    response = client.post("/ai", json={"text": "i have to study cybersecurity course"})
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print("Response:", json.dumps(data, indent=2))
        assert "title" in data
        # Check if inference worked (priority or duration shouldn't be null if smart)
        if data.get("priority") or data.get("estimated_duration"):
             print("✅ Smart Inference Verified")
        else:
             print("⚠️ Smart Inference Weak (fields still null)")
    except Exception as e:
        print(f"❌ TASK Inference Failed: {e}")

def test_planner_mode():
    print("\n--- Testing PLANNER Mode ---")
    response = client.post("/ai", json={"text": "Plan my day, I have gym and study"})
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print("Response:", json.dumps(data, indent=2))
        # Planner mode returns either direct JSON with 'summary' or a fallback dict
        if "summary" in data:
             print("✅ PLANNER Mode Verified")
        elif "role" in data and data["role"] == "coach": # Fallback might happen if classification is fuzzy
             print("⚠️ Classified as COACH instead of PLANNER")
        else:
             print("⚠️ Unexpected Structure")
    except Exception as e:
        print(f"❌ PLANNER Mode Failed: {e}")
        print("Raw Response:", response.text)

def test_coach_mode():
    print("\n--- Testing COACH Mode ---")
    response = client.post("/ai", json={"text": "I feel so stressed and overwhelmed"})
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print("Response:", json.dumps(data, indent=2))
        assert "role" in data
        assert data["role"] == "coach"
        print("✅ COACH Mode Verified")
    except Exception as e:
        print(f"❌ COACH Mode Failed: {e}")
        print("Raw Response:", response.text)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    test_task_mode()
    test_planner_mode()
    test_coach_mode()
