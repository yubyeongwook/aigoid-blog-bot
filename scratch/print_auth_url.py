import os
import urllib.parse
from dotenv import load_dotenv

def main():
    env_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\.env"
    load_dotenv(env_path, override=True)
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        print("GOOGLE_CLIENT_ID not found in .env")
        return
        
    redirect_uri = "http://localhost"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/blogger https://www.googleapis.com/auth/youtube.upload",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    print("--- AUTH URL ---")
    print(auth_url)
    print("----------------")

if __name__ == "__main__":
    main()
