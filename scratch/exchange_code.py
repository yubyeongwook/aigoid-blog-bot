import os
import requests
import json
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    if len(sys.argv) < 2:
        print("Usage: python exchange_code.py <code>")
        sys.exit(1)
        
    code_input = sys.argv[1].strip()
    code = code_input
    if "code=" in code_input:
        import urllib.parse
        parsed = urllib.parse.urlparse(code_input)
        queries = urllib.parse.parse_qs(parsed.query)
        if "code" in queries:
            code = queries["code"][0]
            
    env_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\.env"
    load_dotenv(env_path, override=True)
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = "http://localhost"
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    print(f"Exchanging code ({code[:15]}...) for tokens...")
    res = requests.post(token_url, data=data)
    print("Status Code:", res.status_code)
    if res.status_code == 200:
        tokens = res.json()
        refresh_token = tokens.get("refresh_token")
        access_token = tokens.get("access_token")
        
        print("SUCCESS! Tokens received.")
        if refresh_token:
            print("Refresh Token received:", refresh_token[:15] + "...")
        else:
            print("WARNING: No refresh_token in response. Ensure prompt=consent was used.")
            
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        new_lines = []
        updated_refresh = False
        updated_access = False
        
        for line in lines:
            if line.startswith("GOOGLE_REFRESH_TOKEN=") and refresh_token:
                new_lines.append(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")
                updated_refresh = True
            elif line.startswith("GOOGLE_ACCESS_TOKEN=") and access_token:
                new_lines.append(f"GOOGLE_ACCESS_TOKEN={access_token}\n")
                updated_access = True
            else:
                new_lines.append(line)
                
        if not updated_refresh and refresh_token:
            new_lines.append(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")
        if not updated_access and access_token:
            new_lines.append(f"GOOGLE_ACCESS_TOKEN={access_token}\n")
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        print("SUCCESS: Updated .env file!")
        
        # Test Blogger API immediately
        test_res = requests.get(
            "https://www.googleapis.com/blogger/v3/blogs/917644037266798407/posts?maxResults=1",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print("Blogger API Test Status:", test_res.status_code)
        if test_res.status_code == 200:
            print("SUCCESS: Blogger API Access Verified!")
    else:
        print("Error details:", res.text)

if __name__ == "__main__":
    main()
