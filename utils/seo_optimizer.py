"""
utils/seo_optimizer.py — SEO 최적화 및 메타 태그 / 오픈그래프 생성기
"""
import datetime, re

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
