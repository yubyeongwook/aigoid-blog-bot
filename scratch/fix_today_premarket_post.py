import sys, os, requests, json
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from dotenv import load_dotenv
load_dotenv()

from publishers.blogger_publisher import get_access_token, BLOG_ID, auto_labels

def main():
    post_id = "3256743942301402216"
    html_path = "scratch/test_premarket_result.html"
    
    if not os.path.exists(html_path):
        print(f"Error: {html_path} does not exist. Run test_premarket_only.py first.")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    token = get_access_token()
    if not token:
        print("Error: Failed to get access token.")
        return
        
    # Find title
    import re
    seo_title = "07월 20일 월요일 오전 8시 50분 동시호가 — 오늘 주목 종목과 장 시작 전략"
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
    if h1_match:
        title_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        title_text = " ".join(title_text.split())
        if title_text:
            seo_title = f"07월 20일 월요일 오전 8시 50분 동시호가 — {title_text}"
            
    labels = auto_labels(html_content)
    labels.extend(["동시호가", "멋쟁이픽", "장전브리핑"])
    labels = list(set(labels))
    
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "kind": "blogger#post",
        "title": seo_title,
        "content": html_content,
        "labels": labels
    }

    try:
        res = requests.put(url, headers=headers, json=body, timeout=30)
        result = res.json()
        if "url" in result:
            print(f"✅ 블로그 글 수정 완료: {result['url']}")
        else:
            print(f"⚠️ 블로그 글 수정 결과: {result}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
