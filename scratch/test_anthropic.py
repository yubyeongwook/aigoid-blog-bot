import os
from dotenv import load_dotenv
load_dotenv()

# from publishers.blogger_publisher import get_access_token

def test_anthropic():
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        print("No ANTHROPIC_API_KEY found.")
        return
    
    import requests
    models = ["claude-sonnet-5", "claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001"]
    for model in models:
        try:
            print(f"Testing model: {model}...")
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
            res = requests.post("https://api.anthropic.com/v1/messages", json=body, headers=headers, timeout=10)
            print(f"Result for {model}: Status {res.status_code}")
            if res.status_code == 200:
                print(f"-> SUCCESS for {model}!")
                print(res.json()["content"][0]["text"])
            else:
                print(f"-> FAILED: {res.text}")
        except Exception as e:
            print(f"Error testing {model}: {e}")

if __name__ == "__main__":
    test_anthropic()
