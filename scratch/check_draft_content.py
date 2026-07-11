import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from publishers.blogger_publisher import get_access_token, BLOG_ID
import requests

def main():
    post_id = "25442025647055990"
    token = get_access_token()
    if not token:
        print("토큰 발급 실패")
        return
        
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("Blogger API 오류:", res.status_code, res.text)
        return
        
    post = res.json()
    print("=" * 60)
    print(f"Title: {post.get('title')}")
    print(f"Published Status: {post.get('status')}")
    print("=" * 60)
    
    content = post.get("content", "")
    print("HTML Content Length:", len(content))
    print("\n--- HTML Content Preview (First 2000 chars) ---")
    print(content[:2000])
    print("\n--- HTML Content Preview (Last 1000 chars) ---")
    print(content[-1000:])
    print("=" * 60)

if __name__ == "__main__":
    main()
