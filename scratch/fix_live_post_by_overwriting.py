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
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Post IDs
    good_post_id = "1599011708205373818"    # The good one with table fix
    broken_post_id = "3008002070880346916"  # The one with error page link
    duplicate_post_id = "6114527521342395013" # The duplicate without table fix
    
    # 1. Fetch content of good post
    print("Fetching good post content...")
    good_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{good_post_id}"
    res = requests.get(good_url, headers=headers)
    if res.status_code != 200:
        print("Failed to fetch good post:", res.text)
        return
    
    good_data = res.json()
    good_title = good_data.get("title")
    good_content = good_data.get("content")
    
    # 2. Overwrite the broken post with the good content
    print(f"Overwriting broken post ID {broken_post_id} with good content...")
    overwrite_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{broken_post_id}"
    body = {
        "kind": "blogger#post",
        "title": good_title,
        "content": good_content
    }
    res_overwrite = requests.put(overwrite_url, headers=headers, json=body)
    if res_overwrite.status_code == 200:
        print("Successfully overwrote the broken post!")
        print("Updated URL:", res_overwrite.json().get("url"))
    else:
        print("Failed to overwrite:", res_overwrite.text)
        return
        
    # 3. Delete the duplicate posts
    print(f"Deleting duplicate post ID {good_post_id}...")
    res_del1 = requests.delete(f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{good_post_id}", headers=headers)
    if res_del1.status_code in [200, 204]:
        print("Deleted good duplicate post successfully.")
    else:
        print("Failed to delete good duplicate:", res_del1.text)
        
    print(f"Deleting duplicate post ID {duplicate_post_id}...")
    res_del2 = requests.delete(f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{duplicate_post_id}", headers=headers)
    if res_del2.status_code in [200, 204]:
        print("Deleted duplicate post successfully.")
    else:
        print("Failed to delete duplicate:", res_del2.text)

if __name__ == "__main__":
    main()
