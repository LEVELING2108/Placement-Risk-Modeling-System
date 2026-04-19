import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def check_perf_api():
    try:
        response = requests.get(f"{BASE_URL}/analytics/model-performance")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("API Response Data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    check_perf_api()
