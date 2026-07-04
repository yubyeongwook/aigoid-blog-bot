"""
news_collector.py — 뉴스·공시 수집
네이버 뉴스 + DART API
"""
import requests, os, json, datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

DART_KEY = os.getenv("DART_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ────────────────────────────────
# 네이버 뉴스 검색
# ────────────────────────────────
def get_naver_news(query: str, display: int = 5) -> list:
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {"query": query, "display": display, "sort": "date"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        items = res.json().get("items", [])
        return [{"title": i["title"].replace("<b>","").replace("</b>",""),
                 "link": i["link"],
                 "description": i["description"].replace("<b>","").replace("</b>",""),
                 "pubDate": i["pubDate"]} for i in items]
    except Exception as e:
        return [{"error": str(e)}]

# ────────────────────────────────
# DART 당일 공시 수집
# ────────────────────────────────
def get_dart_disclosures() -> list:
    today = datetime.datetime.now().strftime("%Y%m%d")
    url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        "crtfc_key": DART_KEY,
        "bgn_de": today,
        "end_de": today,
        "sort": "date",
        "sort_mth": "desc",
        "page_no": 1,
        "page_count": 20
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if data.get("status") == "000":
            return [{"corp_name": i["corp_name"],
                     "report_nm": i["report_nm"],
                     "rcept_dt": i["rcept_dt"],
                     "corp_cls": i["corp_cls"]}
                    for i in data.get("list", [])]
        return []
    except Exception as e:
        return [{"error": str(e)}]

# ────────────────────────────────
# 글로벌 매크로 뉴스
# ────────────────────────────────
def get_macro_news() -> dict:
    queries = {
        "미국증시_마감": "미국 증시 나스닥 마감 반도체 엔비디아 테슬라",
        "연준_금리": "연준 금리 FOMC",
        "이란_호르무즈": "이란 호르무즈 유가",
        "반도체_HBM": "SK하이닉스 삼성전자 HBM",
        "MSCI": "MSCI 한국 선진국",
        "코스피_외국인": "코스피 외국인 수급"
    }
    result = {}
    for key, query in queries.items():
        result[key] = get_naver_news(query, display=3)
    return result

# ────────────────────────────────
# 전체 수집
# ────────────────────────────────
def collect_all() -> dict:
    print("📰 뉴스·공시 수집 시작...")
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "macro_news": get_macro_news(),
        "dart_disclosures": get_dart_disclosures()
    }
    print("✅ 뉴스·공시 수집 완료")
    return data

if __name__ == "__main__":
    print(json.dumps(collect_all(), ensure_ascii=False, indent=2))
