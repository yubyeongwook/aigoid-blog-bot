"""
main_daily.py — 오전 7시 자동 실행
6개 전문가 에이전트 → 통합 판단 (Part 1 & 2 순차 합성) → 발행
"""
import sys, os, json, datetime
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(__file__))

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.macro_agent import analyze as macro_analyze
from agents.global_us_agent import analyze_us_market
from agents.supply_agent import analyze as supply_analyze
from agents.earnings_agent import analyze as earnings_analyze
from agents.premarket_volume_agent import analyze_premarket_momentum
from agents.technical_agent import analyze as technical_analyze
from agents.synthesis_agent import synthesize_and_write, extract_and_save_picks
from publishers.blogger_publisher import publish_post, auto_labels

def main():
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    print("=" * 60)
    print(f"  멋쟁이 인사이트 — 오전 자동 브리핑 (v2.1)")
    print(f"  {today.strftime('%Y년 %m월 %d일')} {weekday}요일 KST")
    print("=" * 60)

    print("\n[1/7] 시장 데이터 수집...")
    market_data = collect_market()

    print("\n[2/7] 뉴스·공시 수집...")
    news_data = collect_news()

    print("\n[3/7] 글로벌 매크로 및 미국 시황 분석...")
    macro_result = macro_analyze(market_data, news_data)
    global_us_result = analyze_us_market(market_data, news_data)

    print("\n[4/7] 수급 분석...")
    supply_result = supply_analyze(market_data, news_data)

    print("\n[5/7] 실적·공시 및 장전 모멘텀 분석...")
    earnings_result = earnings_analyze(market_data, news_data)
    premarket_volume_result = analyze_premarket_momentum(market_data, news_data)

    print("\n[6/7] 기술적 지표 분석...")
    technical_result = technical_analyze(market_data, news_data)

    print("\n[7/7] 통합 판단 + 블로그 생성 (2단계 병합)...")
    html_content = synthesize_and_write(
        macro=macro_result,
        supply=supply_result,
        earnings=earnings_result,
        technical=technical_result,
        global_us=global_us_result,
        premarket_volume=premarket_volume_result,
        market_data=market_data,
        report_type="daily_morning"
    )

    # 픽 목록을 파싱하여 저장
    extract_and_save_picks(html_content)

    seo_title = (
        f"{today.strftime('%m월 %d일')} {weekday}요일 "
        f"멋쟁이 인사이트 — "
        f"글로벌 매크로·수급·실적·기술적 통합 분석"
    )
    labels = auto_labels(html_content)
    labels.extend(["멋쟁이인사이트", "멋쟁이픽", "단타픽", "수급분석"])

    # 중복 라벨 제거
    labels = list(set(labels))

    result = publish_post(seo_title, html_content, labels)

    print("\n" + "=" * 60)
    if "url" in result:
        print(f"  ✅ 발행 완료: {result['url']}")
    else:
        print(f"  ⚠️ 발행 결과: {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
