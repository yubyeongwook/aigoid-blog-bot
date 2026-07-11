import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from publishers.blogger_publisher import get_access_token, BLOG_ID
import requests
from bs4 import BeautifulSoup

def check_posts():
    token = get_access_token()
    if not token:
        print("토큰 발급 실패")
        return
        
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?maxResults=5&status=live"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("Blogger API 오류:", res.status_code, res.text)
        return
        
    posts = res.json().get("items", [])
    print(f"최근 발행된 글 {len(posts)}개 조회 완료\n")
    for i, post in enumerate(posts):
        print(f"[{i+1}] {post.get('title')}")
        print(f"    ID: {post.get('id')}")
        print(f"    Published: {post.get('published')}")
        print(f"    URL: {post.get('url')}")
        
        content = post.get("content", "")
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        
        print(f"    Preview: {text[:150].strip()}...")
        
        indicators = []
        if "Gemini" in text or "gemini" in text:
            indicators.append("Gemini")
        if "Claude" in text or "claude" in text:
            indicators.append("Claude")
        if "Sonnet" in text or "sonnet" in text:
            indicators.append("Sonnet")
            
        print(f"    Model Indicators in Text: {indicators}")
        print("-" * 60)

if __name__ == "__main__":
    check_posts()
