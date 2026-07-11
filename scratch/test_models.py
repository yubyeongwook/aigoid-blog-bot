import os, sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_models():
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        print("No ANTHROPIC_API_KEY found.")
        return
        
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01"
    }
    
    # 1. Test Listing Models
    try:
        print("Fetching available models list...")
        res = requests.get("https://api.anthropic.com/v1/models", headers=headers, timeout=10)
        print("Status Code:", res.status_code)
        if res.status_code == 200:
            data = res.json()
            print("Available models:")
            for m in data.get("data", []):
                print(f"- {m.get('id')} ({m.get('display_name')})")
        else:
            print("Failed to list models:", res.text)
    except Exception as e:
        print("Error listing models:", e)

if __name__ == "__main__":
    test_models()
