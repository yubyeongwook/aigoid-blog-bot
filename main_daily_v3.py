"""
main_daily_v3.py — 오전 7시 자동 실행 v3
6개 전문가 에이전트 + 픽 성과 추적 + 감성 지수
"""
import sys, os, json, datetime
sys.path.append(os.path.dirname(__file__))

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.macro_agent import analyze as macro_analyze
from agents.supply_agent import analyze as supply_analyze
from agents.earnings_agent import analyze as earnings_analyze
from agents.technical_agent import analyze as technical_analyze
from agents.dart_nlp_agent import analyze as dart_nlp_analyze
from agents.foreign_tracker_agent import analyze as foreign_analyze
from agents.sentiment_agent import analyze as sentiment_analyze
from agents.synthesis_agent_v3 import synthesize_and_write
from trackers.pick_tracker import (
    update_performance,
    generate_performance_html,
    save_picks
)
from publishers.blogger_publisher import publish_post, auto_labels

def extract_picks_from_html(html: str) -> list:
    """HTML에서 픽 정보 추출 (간단 파싱)"""
    import re
    picks = []
    # 종목명과 진입가 패턴 탐지
    patterns = [
        r'([가-힣a-zA-Z]+)\s*\((\d{6})\)',  # 종목명 (코드)
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for name, ticker in matches[:8]:
            picks.append({
                "name": name,
                "ticker": ticker,
                "type": "단타",
                "entry_price": 0,
                "stop_loss": 0,
                "target_1": 0,
                "status": "진행중"
            })
    return picks[:8]

def main():
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    print("=" * 60)
    print(f"  멋쟁이 인사이트 v3 — 오전 자동 브리핑")
    print(f"  {today.strftime('%Y년 %m월 %d일')} {weekday}요일 KST")
    print(f"  6개 에이전트 + 픽 추적 + 감성 지수")
    print("=" * 60)

    # 1. 전일 픽 성과 업데이트
    print("\n[0/7] 전일 픽 성과 업데이트...")
    try:
        update_performance()
        performance_html = generate_performance_html()
    except Exception as e:
        print(f"픽 추적 오류: {e}")
        performance_html = ""

    # 2. 데이터 수집
    print("\n[1/7] 시장 데이터 수집...")
    market_data = collect_market()

    print("\n[2/7] 뉴스·공시 수집...")
    news_data = collect_news()

    # 3. 6개 에이전트 분석
    print("\n[3/7] 글로벌 매크로 분석...")
    macro_result = macro_analyze(market_data, news_data)

    print("\n[4/7] 수급 + 외국인 종목 추적...")
    supply_result = supply_analyze(market_data, news_data)
    foreign_result = foreign_analyze(market_data)

    print("\n[5/7] 실적·공시 NLP 분석...")
    earnings_result = earnings_analyze(market_data, news_data)
    dart_result = dart_nlp_analyze(market_data)

    print("\n[6/7] 기술적 분석 + 감성 지수...")
    technical_result = technical_analyze(market_data, news_data)
    sentiment_result = sentiment_analyze(market_data, news_data)

    # 4. 통합 판단 + 블로그 생성
    print("\n[7/7] 6개 에이전트 통합 판단 + 블로그 생성...")
    html_content = synthesize_and_write(
        macro=macro_result,
        supply=supply_result,
        earnings=earnings_result,
        technical=technical_result,
        dart_nlp=dart_result,
        foreign_tracker=foreign_result,
        sentiment=sentiment_result,
        market_data=market_data,
        performance_html=performance_html,
        report_type="daily_morning_v3"
    )

    # 5. 픽 저장 (다음날 성과 추적용)
    picks = extract_picks_from_html(html_content)
    if picks:
        save_picks(picks, today.strftime("%Y-%m-%d"))

    # 6. 발행
    seo_title = (
        f"{today.strftime('%m월 %d일')} {weekday}요일 멋쟁이 인사이트 — "
        f"6개 전문가 통합 분석 · 단타·스윙·중기 픽"
    )
    labels = auto_labels(html_content)
    labels.extend(["멋쟁이픽", "단타픽", "수급분석", "공시분석"])

    result = publish_post(seo_title, html_content, labels)

    print("\n" + "=" * 60)
    if "url" in result:
        print(f"  ✅ 발행 완료: {result['url']}")
    else:
        print(f"  ⚠️ 결과: {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
