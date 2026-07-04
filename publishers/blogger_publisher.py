"""
blogger_publisher.py — Blogger 자동 발행
Google OAuth2 + Blogger API v3
"""
import os, json, datetime, requests
from dotenv import load_dotenv
load_dotenv()

BLOG_ID = os.getenv("BLOG_ID")
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

# ────────────────────────────────
# 액세스 토큰 발급
# ────────────────────────────────
def get_access_token() -> str:
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    try:
        res = requests.post(url, data=data, timeout=10)
        return res.json().get("access_token", "")
    except Exception as e:
        print(f"토큰 발급 오류: {e}")
        return ""

# ────────────────────────────────
# 블로그 발행
# ────────────────────────────────
def publish_post(title: str, html_content: str,
                 labels: list = None, draft: bool = False) -> dict:
    token = get_access_token()
    if not token:
        return {"error": "토큰 발급 실패"}

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if labels is None:
        labels = ["멋쟁이인사이트", "코스피", "주식분석"]

    body = {
        "kind": "blogger#post",
        "title": title,
        "content": html_content,
        "labels": labels
    }

    params = {"isDraft": "true" if draft else "false"}

    try:
        res = requests.post(url, headers=headers,
                           json=body, params=params, timeout=30)
        result = res.json()
        if "url" in result:
            print(f"✅ 발행 완료: {result['url']}")
        else:
            print(f"⚠️ 발행 결과: {result}")
        return result
    except Exception as e:
        return {"error": str(e)}

# ────────────────────────────────
# SEO 제목 자동 설계
# ────────────────────────────────
def build_seo_title(base_title: str, report_type: str) -> str:
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")

    prefixes = {
        "daily": f"{date_str} 코스피 분석 —",
        "weekly": f"코스피 주간 결산 {today.strftime('%m월 %d일')} —",
        "special": ""
    }

    prefix = prefixes.get(report_type, "")
    return f"{prefix} {base_title}" if prefix else base_title

# ────────────────────────────────
# 라벨 자동 설정
# ────────────────────────────────
def auto_labels(content: str) -> list:
    labels = ["멋쟁이인사이트", "코스피", "주식분석"]
    keywords = {
        "SK하이닉스": "반도체",
        "삼성전자": "반도체",
        "HBM": "반도체",
        "MSCI": "MSCI",
        "외국인": "수급분석",
        "FOMC": "금리",
        "마이크론": "반도체",
        "조선": "조선방산",
        "방산": "조선방산"
    }
    for keyword, label in keywords.items():
        if keyword in content and label not in labels:
            labels.append(label)
    return labels[:10]

if __name__ == "__main__":
    print("blogger_publisher.py 로드 완료")
    token = get_access_token()
    print(f"토큰 발급: {'성공' if token else '실패'}")
