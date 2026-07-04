"""
main_daily.py — 일일 자동 실행 메인
매일 오전 7시 깃허브 액션이 자동 실행
"""
import sys, os, json, datetime
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.dirname(__file__))

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from generators.report_generator import generate_daily_report
from publishers.blogger_publisher import publish_post, build_seo_title, auto_labels

def main():
    print("=" * 60)
    print(f"  멋쟁이 인사이트 — 일일 자동 리포트")
    print(f"  실행 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 1. 데이터 수집
    print("\n[1/4] 시장 데이터 수집...")
    market_data = collect_market()

    print("\n[2/4] 뉴스·공시 수집...")
    news_data = collect_news()

    # 2. 리포트 생성
    print("\n[3/4] AI 리포트 생성...")
    html_content = generate_daily_report(market_data, news_data)

    # 3. 제목·라벨 설정
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    
    # AI가 생성한 HTML에서 h1 태그나 JSON-LD의 headline 추출 시도
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
        base_title = f"코스피 오늘 분석 — {today.strftime('%m월 %d일')} {weekday}요일 브리핑"
        seo_title = build_seo_title(base_title, "daily")
        
    labels = auto_labels(html_content)

    # 4. 발행
    print("\n[4/4] Blogger 자동 발행...")
    result = publish_post(seo_title, html_content, labels)

    print("\n" + "=" * 60)
    if "url" in result:
        print(f"  ✅ 발행 완료!")
        print(f"  URL: {result['url']}")
    else:
        print(f"  ⚠️ 발행 결과: {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
