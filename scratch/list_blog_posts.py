import os
import requests
import json
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_access_token(client_id, client_secret, refresh_token):
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    res = requests.post(url, data=data)
    return res.json().get("access_token")

def main():
    env_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\.env"
    load_dotenv(env_path, override=True)
    
    blog_id = os.getenv("BLOG_ID")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    
    token = get_access_token(client_id, client_secret, refresh_token)
    
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?maxResults=10&status=live"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        posts = res.json().get("items", [])
        print(f"Found {len(posts)} live posts:")
        for idx, post in enumerate(posts):
            content = post.get("content", "")
            has_error = "invalid_request_error" in content
            print(f"[{idx}] ID: {post.get('id')}")
            print(f"    Title: {post.get('title')}")
            print(f"    URL: {post.get('url')}")
            print(f"    Has Error: {has_error}")
            print(f"    Published: {post.get('published')}")
    else:
        print("Failed to get posts:", res.text)

if __name__ == "__main__":
    main()
