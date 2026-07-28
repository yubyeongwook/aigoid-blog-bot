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
    
    # 1. Fetch latest post
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?maxResults=1&status=live"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        posts = res.json().get("items", [])
        if not posts:
            print("No live posts found.")
            return
        
        post = posts[0]
        post_id = post.get("id")
        content = post.get("content")
        title = post.get("title")
        
        # Replace margin: 0 auto; with margin: 0;
        old_str = 'margin: 0 auto;'
        new_str = 'margin: 0;'
        
        if old_str in content:
            new_content = content.replace(old_str, new_str)
            print("Successfully replaced margin style in HTML.")
        else:
            new_content = content
            print("margin: 0 auto; not found in HTML.")
            
        # 3. Update the post back to Blogger
        update_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{post_id}"
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": new_content
        }
        
        update_res = requests.put(update_url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }, json=body)
        
        if update_res.status_code == 200:
            print("Successfully patched Blogger post margin!")
        else:
            print("Failed to update post:", update_res.text)
    else:
        print("Failed to get latest post:", res.text)

if __name__ == "__main__":
    main()
