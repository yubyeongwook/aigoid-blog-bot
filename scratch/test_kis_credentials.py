import os
import requests
import json
import sys
from dotenv import load_dotenv

# Set console encoding to UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_kis():
    load_dotenv()
    app_key = os.getenv("KIS_APP_KEY", "")
    app_secret = os.getenv("KIS_APP_SECRET", "")
    
    if not app_key or not app_secret:
        print("[ERROR] KIS_APP_KEY or KIS_APP_SECRET is not set in .env")
        return

    print(f"Testing KIS API with key starting with: {app_key[:5]}...")
    
    # 1. Test Real Investment URL
    real_url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }
    
    print("\n--- Testing Real Investment API (openapi.koreainvestment.com) ---")
    try:
        res = requests.post(real_url, json=body, timeout=10)
        print("Status Code:", res.status_code)
        res_json = res.json()
        if "access_token" in res_json:
            print("[SUCCESS] Real KIS API Authentication successful!")
        else:
            print("[FAILED] Real KIS API Authentication failed:")
            print(json.dumps(res_json, indent=2, ensure_ascii=False))
    except Exception as e:
        print("[ERROR] Real KIS API Exception occurred:", str(e))
        
    # 2. Test Virtual Investment URL
    virtual_url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"
    print("\n--- Testing Virtual Investment API (openapivts.koreainvestment.com) ---")
    try:
        res = requests.post(virtual_url, json=body, timeout=10)
        print("Status Code:", res.status_code)
        res_json = res.json()
        if "access_token" in res_json:
            print("[SUCCESS] Virtual KIS API Authentication successful!")
        else:
            print("[FAILED] Virtual KIS API Authentication failed:")
            print(json.dumps(res_json, indent=2, ensure_ascii=False))
    except Exception as e:
        print("[ERROR] Virtual KIS API Exception occurred:", str(e))

if __name__ == "__main__":
    test_kis()
