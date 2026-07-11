import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from publishers.blogger_publisher import get_access_token, BLOG_ID
import requests

def main():
    token = get_access_token()
    if not token:
        print("토큰 발급 실패")
        return
        
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?status=draft"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("Blogger API 오류:", res.status_code, res.text)
        return
        
    posts = res.json().get("items", [])
    for p in posts:
        if p.get('id') == "25442025647055990":
            print("=" * 60)
            print(f"Title: {p.get('title')}")
            print("=" * 60)
            content = p.get("content", "")
            print("--- HTML CONTENT ---")
            print(content)
            print("=" * 60)
            break

if __name__ == "__main__":
    main()
