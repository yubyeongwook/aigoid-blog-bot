import os
import requests
import json
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    env_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\.env"
    load_dotenv(env_path, override=True)
    
    blog_id = os.getenv("BLOG_ID")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    
    print("BLOG_ID:", blog_id)
    print("GOOGLE_CLIENT_ID:", client_id[:10] if client_id else None)
    print("GOOGLE_CLIENT_SECRET:", client_secret[:5] if client_secret else None)
    print("GOOGLE_REFRESH_TOKEN:", refresh_token[:15] if refresh_token else None)
    
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    try:
        res = requests.post(url, data=data, timeout=10)
        print("Status Code:", res.status_code)
        resp_json = res.json()
        print("Response JSON:")
        # mask access_token
        if "access_token" in resp_json:
            masked = resp_json.copy()
            masked["access_token"] = masked["access_token"][:15] + "..."
            print(json.dumps(masked, indent=2))
        else:
            print(json.dumps(resp_json, indent=2))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
