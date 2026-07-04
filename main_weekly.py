"""
main_weekly.py — 주간 자동 실행 메인
매주 일요일 오전 9시 자동 실행
"""
import sys, os, datetime
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.dirname(__file__))

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from generators.report_generator import generate_weekly_report
from publishers.blogger_publisher import publish_post, auto_labels

def main():
    print("=" * 60)
    print(f"  멋쟁이 인사이트 — 주간 결산 자동 리포트")
    print(f"  실행 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    today = datetime.datetime.now()

    print("\n[1/4] 주간 시장 데이터 수집...")
    market_data = collect_market()

    print("\n[2/4] 주간 뉴스 수집...")
    news_data = collect_news()

    print("\n[3/4] 주간 결산 AI 리포트 생성...")
    html_content = generate_weekly_report(market_data, news_data)

    # 주간 결산 제목
    seo_title = None
    import re
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
    if h1_match:
        seo_title = h1_match.group(1).strip()
        seo_title = re.sub(r'<[^>]+>', '', seo_title) # HTML 태그 제거
        
    if not seo_title:
        headline_match = re.search(r'"headline"\s*:\s*"([^"]+)"', html_content)
        if headline_match:
            seo_title = headline_match.group(1).strip()
            
    if not seo_title:
        seo_title = (f"코스피 주간 결산 {today.strftime('%m월 %d일')} — "
                     f"이번 주 핵심 분석과 다음 주 전망")
                     
    labels = auto_labels(html_content)
    labels.append("주간결산")

    print("\n[4/4] Blogger 자동 발행...")
    result = publish_post(seo_title, html_content, labels)

    print("\n" + "=" * 60)
    if "url" in result:
        print(f"  ✅ 주간 결산 발행 완료!")
        print(f"  URL: {result['url']}")
    else:
        print(f"  ⚠️ {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
