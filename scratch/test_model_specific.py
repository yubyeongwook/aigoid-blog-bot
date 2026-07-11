import os, requests
from dotenv import load_dotenv
load_dotenv()

def test_model():
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        print("No ANTHROPIC_API_KEY found.")
        return
        
    model = "claude-sonnet-4-6"
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = {
        "model": model,
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hello"}]
    }
    try:
        res = requests.post("https://api.anthropic.com/v1/messages", json=body, headers=headers, timeout=10)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
