import sys, os, json, datetime, re
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

# Force using gemini to test the replaced Gemini system prompt
os.environ["PRIMARY_AI"] = "gemini"

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from generators.report_generator import generate_daily_report
from publishers.blogger_publisher import publish_post, build_seo_title, auto_labels

def main():
    print("=" * 60)
    print(" 테스트 발행 시작 (모델: Gemini, 저장: Blogger 임시저장)")
    print("=" * 60)
    
    # 1. 데이터 수집
    print("\n[1/3] 시장 및 뉴스 데이터 수집...")
    market_data = collect_market()
    news_data = collect_news()
    
    # 2. 리포트 생성
    print("\n[2/3] AI 리포트 생성 (Claude API 호출)...")
    html_content = generate_daily_report(market_data, news_data)
    
    # 3. 제목 및 라벨 추출
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    
    seo_title = None
    # JSON-LD "headline" 추출 시도
    headline_match = re.search(r'"headline"\s*:\s*"([^"]+)"', html_content)
    if headline_match:
        temp_title = headline_match.group(1).strip()
        if temp_title and temp_title not in ["멋쟁이 인사이트", "멋쟁이인사이트"]:
            seo_title = temp_title

    # <h1> 태그들 중 "멋쟁이 인사이트"가 아닌 진짜 제목 추출 시도
    if not seo_title:
        h1_tags = re.findall(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
        for tag in h1_tags:
            title_text = re.sub(r'<[^>]+>', '', tag).strip()
            title_text = " ".join(title_text.split())
            if title_text and title_text not in ["멋쟁이 인사이트", "멋쟁이인사이트"]:
                seo_title = title_text
                break

    if not seo_title:
        base_title = f"코스피 오늘 분석 — {today.strftime('%m월 %d일')} {weekday}요일 브리핑"
        seo_title = build_seo_title(base_title, "daily")
        
    labels = auto_labels(html_content)
    
    print(f"추출된 제목: {seo_title}")
    print(f"추출된 라벨: {labels}")
    
    # 4. 임시저장 발행
    print("\n[3/3] Blogger 임시저장(Draft)으로 발행 중...")
    result = publish_post(seo_title, html_content, labels, draft=True)
    
    print("\n" + "=" * 60)
    if "url" in result:
        print("  ✅ 테스트 임시저장 성공!")
        print(f"  URL: {result['url']}")
        print(f"  Post ID: {result.get('id')}")
    else:
        print(f"  ❌ 발행 실패: {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
