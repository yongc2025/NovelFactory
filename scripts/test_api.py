import requests
import json

BASE_URL = "http://localhost:8000/api"
PROJECT_ID = "20260601_172217_9a0afb"

def test_project_detail():
    print(f"Testing GET /projects/{PROJECT_ID}")
    resp = requests.get(f"{BASE_URL}/projects/{PROJECT_ID}")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

def test_pipeline_status():
    print(f"Testing GET /projects/{PROJECT_ID}/pipeline/status")
    resp = requests.get(f"{BASE_URL}/projects/{PROJECT_ID}/pipeline/status")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    test_project_detail()
    test_pipeline_status()
