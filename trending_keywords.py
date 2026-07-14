"""
멋쟁이 인사이트 — 실시간 트렌드 키워드 블로그 자동 발행
네이버 DataLab API로 실시간 트렌드 수집 → Claude로 블로그 글 작성 → Blogger 발행
"""

import os
import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone, timedelta


NAVER_DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def get_trending_keywords(client_id: str, client_secret: str) -> list[str]:
    """네이버 DataLab에서 실시간 트렌드 키워드 수집"""
    # 인기 검색어 카테고리들
    keywords = [
        ["주식", "코스피", "코스닥"],
        ["반도체", "SK하이닉스", "삼성전자"],
        ["환율", "달러", "금리"],
        ["에코프로", "2차전지", "배터리"],
        ["부동산", "아파트", "금리인하"],
    ]

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json",
    }

    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [{"groupName": k[0], "keywords": k} for k in keywords],
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(NAVER_DATALAB_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        # 최근 트렌드 상위 키워드 추출
        results = result.get("results", [])
        sorted_results = sorted(
            results,
            key=lambda x: sum(d.get("ratio", 0) for d in x.get("data", [])),
            reverse=True
        )
        return [r["title"] for r in sorted_results[:5]]
    except Exception as e:
        print(f"트렌드 키워드 수집 실패: {e}")
        return ["주식", "코스피", "달러", "반도체", "금리"]


TREND_BLOG_PROMPT = """당신은 '멋쟁이 인사이트 SMART MONEY INTELLIGENCE'의 트렌드 분석 전문 에디터입니다.
실시간 인기 키워드를 바탕으로 투자자들이 궁금해할 핵심 정보를 블로그 글로 작성합니다.

# 작성 규칙
- 키워드와 관련된 최신 정보를 검색해서 작성
- 제목에 키워드를 자연스럽게 포함
- 투자자 관점에서 "왜 지금 이게 뜨고 있나"를 설명
- 800~1200자 분량
- HTML 형식으로 출력

# 출력 형식 (JSON)
{"title": "글 제목", "content_html": "<h2>...</h2><p>...</p>..."}
"""


def generate_trend_blog(api_key: str, keyword: str) -> tuple[str, str] | None:
    primary_ai = os.getenv("PRIMARY_AI", "claude").lower()
    
    def run_gemini():
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            raise RuntimeError("GEMINI_API_KEY not found in environment")
        
        gemini_model = "gemini-3.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
        
        combined_text = f"{TREND_BLOG_PROMPT}\n\n오늘 실시간 트렌드 키워드 '{keyword}'에 대한 블로그 글을 작성해줘."
        body = {
            "contents": [{"parts": [{"text": combined_text}]}],
            "tools": [{"googleSearch": {}}],
            "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3}
        }
        
        print(f"[Gemini] 트렌드 블로그 생성 시도 ({keyword})...")
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            
        candidates = res_data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini content empty")
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise RuntimeError("Gemini content parts empty")
        text = parts[0].get("text", "").strip()
        
        # JSON parsing
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            parsed = json.loads(text[start:end+1])
            print(f"[Gemini] 트렌드 블로그 생성 성공 ({keyword})")
            return parsed["title"], parsed["content_html"]
        raise RuntimeError("Failed to parse JSON from Gemini response")

    if primary_ai == "gemini":
        try:
            return run_gemini()
        except Exception as e:
            print(f"⚠️ [Gemini] 트렌드 블로그 생성 실패 ({keyword}): {e}. Claude로 백업 시도...")

    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 3000,
        "system": TREND_BLOG_PROMPT,
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}],
        "messages": [{"role": "user", "content": f"오늘 실시간 트렌드 키워드 '{keyword}'에 대한 블로그 글을 작성해줘."}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(ANTHROPIC_API_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        text = "\n".join(
            b["text"] for b in result.get("content", []) if b.get("type") == "text"
        ).strip()

        # JSON 파싱
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            data = json.loads(text[start:end+1])
            return data["title"], data["content_html"]
    except Exception as e:
        print(f"⚠️ [Claude] 트렌드 블로그 생성 실패 ({keyword}): {e}")
        if primary_ai != "gemini":
            print("🔄 Gemini 백업 호출 시도...")
            try:
                return run_gemini()
            except Exception as ge:
                print(f"⚠️ [Gemini 백업] 트렌드 블로그 생성 실패 ({keyword}): {ge}")
    return None


def refresh_google_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    payload = {
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_token, "grant_type": "refresh_token",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["access_token"]


def post_to_blogger(blog_id: str, access_token: str, title: str, content: str) -> str | None:
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/?isDraft=false"
    payload = {"title": title, "content": content}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("url")
    except Exception as e:
        print(f"Blogger 발행 실패: {e}")
        return None


def main():
    api_key = os.environ["ANTHROPIC_API_KEY"]
    naver_id = os.environ.get("NAVER_CLIENT_ID", "")
    naver_secret = os.environ.get("NAVER_CLIENT_SECRET", "")
    blog_id = os.environ["BLOG_ID"]
    google_token = refresh_google_token(
        os.environ["GOOGLE_CLIENT_ID"],
        os.environ["GOOGLE_CLIENT_SECRET"],
        os.environ["GOOGLE_REFRESH_TOKEN"]
    )

    # 트렌드 키워드 수집
    keywords = get_trending_keywords(naver_id, naver_secret)
    print(f"오늘의 트렌드 키워드: {keywords}")

    results = []
    for keyword in keywords[:3]:  # 상위 3개 키워드만 (비용 절약)
        result = generate_trend_blog(api_key, keyword)
        if result:
            title, content = result
            url = post_to_blogger(blog_id, google_token, title, content)
            results.append({"keyword": keyword, "title": title, "url": url})
            print(f"✅ 발행 완료: {title}")

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
