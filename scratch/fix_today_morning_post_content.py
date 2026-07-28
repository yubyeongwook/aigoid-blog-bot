import sys, os, requests, json
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from dotenv import load_dotenv
load_dotenv()

from publishers.blogger_publisher import get_access_token, BLOG_ID, auto_labels

def main():
    post_id = "4573389971293353781"
    html_path = "scratch/test_daily_brief_result.html"
    
    if not os.path.exists(html_path):
        print(f"Error: {html_path} does not exist. Run test_daily_brief_only.py first.")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    token = get_access_token()
    if not token:
        print("Error: Failed to get access token.")
        return
        
    # Find title
    import re
    seo_title = "07월 20일 월요일 멋쟁이 인사이트 — 9개 전문가 통합 분석·백테스팅 검증"
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
    if h1_match:
        title_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        title_text = " ".join(title_text.split())
        if title_text:
            seo_title = f"07월 20일 월요일 멋쟁이 인사이트 — {title_text}"
            
    labels = auto_labels(html_content)
    labels.extend(["멋쟁이픽", "단타픽", "수급분석", "공시분석", "백테스팅"])
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
            print(f"✅ 오전 브리핑 글 수정 완료: {result['url']}")
        else:
            print(f"⚠️ 오전 브리핑 글 수정 결과: {result}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
