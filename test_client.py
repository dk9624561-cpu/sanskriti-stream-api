import json
import os
import requests

def test_api(api_url="http://localhost:5000/codex", vdc_id=""):
    # Load session.json
    if not os.path.exists("session.json"):
        print("Error: 'session.json' not found. Please run 'login_helper.py' first to authenticate.")
        return

    with open("session.json", "r") as f:
        session = json.load(f)

    # Check required fields
    token = session.get("token") or session.get("jwt")
    user_id = session.get("user_id")
    mobile = session.get("mobile")

    if not token or not user_id:
        print("Error: Invalid session.json content. Re-run 'login_helper.py'.")
        return

    if not vdc_id:
        vdc_id = input("Enter a valid Video ID (vdc_id) to test: ").strip()
        if not vdc_id:
            print("Error: Video ID (vdc_id) is required.")
            return

    # Payload matching our Vercel API contract
    payload = {
        "vdc_id": vdc_id,
        "user_id": user_id,
        "token": token,
        "mobile": mobile,
        "tile_id": 0,
        "quality": "720"
    }

    print(f"\nSending POST request to {api_url}...")
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        print(f"Server Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error connecting to server: {str(e)}")

if __name__ == "__main__":
    import sys
    url = "http://localhost:5000/codex"
    v_id = ""
    
    if len(sys.argv) >= 2:
        v_id = sys.argv[1]
    if len(sys.argv) >= 3:
        url = sys.argv[2]
        
    test_api(url, v_id)
