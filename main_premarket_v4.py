import sys, os, json, datetime, re
sys.path.append(os.path.dirname(__file__))

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.macro_agent import analyze as macro_analyze
from agents.supply_agent import analyze as supply_analyze
from agents.technical_agent import analyze as technical_analyze
from agents.foreign_tracker_agent import analyze as foreign_analyze
from agents.sentiment_agent import analyze as sentiment_analyze
from agents.synthesis_agent_v3 import synthesize_and_write
from trackers.pick_tracker import generate_performance_html, calculate_stats
from publishers.blogger_publisher import publish_post, auto_labels

def main():
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    print("="*60)
    print(f"  멋쟁이 인사이트 — 오전 8시 50분 동시호가 브리핑")
    print(f"  {today.strftime('%Y년 %m월 %d일')} {weekday}요일 KST")
    print("="*60)

    print("\n[1/5] 실시간 시장 데이터 수집...")
    market_data = collect_market()

    print("\n[2/5] 뉴스·공시 수집...")
    news_data = collect_news()

    print("\n[3/5] 수급 + 외국인 + 감성 분석...")
    supply_result = supply_analyze(market_data, news_data)
    technical_result = technical_analyze(market_data, news_data)
    foreign_result = foreign_analyze(market_data)
    sentiment_result = sentiment_analyze(market_data, news_data)
    macro_result = macro_analyze(market_data, news_data) if hasattr(__import__('agents.macro_agent', fromlist=['analyze']), 'analyze') else {}

    performance_html = generate_performance_html()
    stats = calculate_stats()

    print("\n[4/5] 동시호가 브리핑 생성...")
    html_content = synthesize_and_write(
        macro=macro_result,
        supply=supply_result,
        earnings={},
        technical=technical_result,
        dart_nlp={},
        foreign_tracker=foreign_result,
        sentiment=sentiment_result,
        market_data=market_data,
        performance_html=performance_html,
        report_type="premarket_850"
    )

    print("\n[5/5] 발행...")
    seo_title = (
        f"{today.strftime('%m월 %d일')} {weekday}요일 "
        f"오전 8시 50분 동시호가 — "
        f"오늘 주목 종목과 장 시작 전략"
    )
    labels = auto_labels(html_content)
    labels.extend(["동시호가", "멋쟁이픽", "장전브리핑"])
    result = publish_post(seo_title, html_content, labels)

    print("\n"+"="*60)
    if "url" in result:
        print(f"  ✅ 동시호가 브리핑 발행 완료: {result['url']}")
    else:
        print(f"  ⚠️ 결과: {result}")
    print("="*60)

if __name__ == "__main__":
    main()
