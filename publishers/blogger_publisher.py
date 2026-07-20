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
                 labels: list = None, draft: bool = False,
                 published_time: str = None) -> dict:
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

    if published_time:
        body["published"] = published_time

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
    today = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
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

# ────────────────────────────────
# 최신 오전 브리핑 내용 조회
# ────────────────────────────────
def get_latest_morning_brief() -> dict:
    token = get_access_token()
    if not token:
        return {}

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?maxResults=5&status=live"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        posts = res.json().get("items", [])
        for post in posts:
            title = post.get("title", "")
            content = post.get("content", "")
            if "멋쟁이 인사이트" in title or "오전" in title or "글로벌 매크로 브리핑" in title or "통합 분석" in title or "오전 글로벌 매크로 브리핑" in content:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator=' ').strip()
                # 불필요한 줄바꿈 및 다중 공백 정리
                text = " ".join(text.split())
                return {
                    "title": title,
                    "published": post.get("published"),
                    "text_summary": text[:2500]
                }
    except Exception as e:
        print(f"오전 브리핑 조회 실패: {e}")
    return {}

# ────────────────────────────────
# 최신 오후 마감 브리핑 내용 조회
# ────────────────────────────────
def get_latest_afternoon_report() -> dict:
    token = get_access_token()
    if not token:
        return {}

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts?maxResults=10&status=live"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        posts = res.json().get("items", [])
        for post in posts:
            title = post.get("title", "")
            content = post.get("content", "")
            labels = post.get("labels", [])
            if "마감분석" in labels or "마감" in title or "마감 브리핑" in title:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator=' ').strip()
                text = " ".join(text.split())
                return {
                    "title": title,
                    "published": post.get("published"),
                    "text_summary": text[:2500]
                }
    except Exception as e:
        print(f"오후 마감 브리핑 조회 실패: {e}")
    return {}


if __name__ == "__main__":
    print("blogger_publisher.py 로드 완료")
    token = get_access_token()
    print(f"토큰 발급: {'성공' if token else '실패'}")
