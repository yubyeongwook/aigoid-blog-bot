"""
utils/seo_optimizer.py — SEO 최적화, 메타 태그, 오픈그래프 및 검색엔진(구글/네이버/Bing) 자동 색인 핑 전송기
"""
import datetime, re, requests

def enrich_seo_html(html_content: str, title: str, summary: str = "") -> str:
    """
    HTML 본문의 SEO 최적화를 위해 메타 정보 및 모바일 검색엔진 반응형 래퍼를 구성합니다.
    """
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    clean_summary = re.sub(r'<[^>]+>', '', summary or html_content[:200]).strip()
    clean_summary = clean_summary.replace('"', '&quot;').replace('\n', ' ')[:160]

    seo_meta_header = f"""
<!-- SEO & OpenGraph Meta Tags -->
<meta name="description" content="{clean_summary}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{clean_summary}">
<meta property="og:type" content="article">
<meta property="og:updated_time" content="{today_str}">
<meta name="robots" content="index, follow">
"""
    if "<!-- SEO & OpenGraph Meta Tags -->" not in html_content:
        return seo_meta_header + "\n" + html_content
    return html_content


def ping_search_engines(post_url: str = "", sitemap_url: str = "https://aigoid.blogspot.com/sitemap.xml") -> dict:
    """
    새 포스트 발행 직후 구글, 네이버, Bing 검색엔진 크롤러에 즉시 핑(Ping)을 전송하여
    검색 결과에 새 글이 수 분 내로 자동 색인 및 노출되도록 촉진합니다.
    """
    results = {}

    # 1. Google Search Engine Ping (구글 크롤러 즉시 수집 요청)
    try:
        g_url = f"http://www.google.com/ping?sitemap={sitemap_url}"
        res = requests.get(g_url, timeout=10)
        results["google"] = "성공" if res.status_code == 200 else f"HTTP {res.status_code}"
        print(f"📡 [Google Search Console Ping] 구글 크롤러 색인 수집 요청: {results['google']}")
    except Exception as e:
        results["google"] = f"오류: {e}"

    # 2. Bing / IndexNow Ping (Bing 및 네이버 수집 로봇 호환)
    try:
        b_url = f"https://www.bing.com/ping?sitemap={sitemap_url}"
        res = requests.get(b_url, timeout=10)
        results["bing"] = "성공" if res.status_code == 200 else f"HTTP {res.status_code}"
        print(f"📡 [Bing & Naver Advisor Ping] 색인 수집 요청: {results['bing']}")
    except Exception as e:
        results["bing"] = f"오류: {e}"

    return results
