import sys, os, datetime
sys.path.append(os.path.dirname(__file__) + '/..')
import agents.patch_anthropic

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.macro_agent import analyze as macro_analyze
from agents.supply_agent import analyze as supply_analyze
from agents.technical_agent import analyze as technical_analyze
from agents.foreign_tracker_agent import analyze as foreign_analyze
from agents.sentiment_agent import analyze as sentiment_analyze
from agents.earnings_agent import analyze as earnings_analyze
from agents.dart_nlp_agent import analyze as dart_nlp_analyze
from backtesting.backtest_agent import analyze as backtest_analyze
from agents.synthesis_agent_v3 import synthesize_and_write
from trackers.pick_tracker import generate_performance_html, calculate_stats
from utils.fact_validator import validate_and_correct
from publishers.blogger_publisher import get_latest_afternoon_report

def main():
    kst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    today = kst_now.date()
    weekday = ["월", "화", "수", "목", "금", "토", "일"][today.weekday()]

    print("="*60)
    print("   멋쟁이 인사이트 v4 — 오전 7시 브리핑 로컬 테스트")
    print(f"   {today.strftime('%Y년 %m월 %d일')} {weekday}요일 KST")
    print("="*60)

    print("\n[1/10] 시장 데이터 수집...")
    market_data = collect_market()

    print("\n[2/10] 뉴스·공시 수집...")
    news_data = collect_news()

    print("\n[3/10] 글로벌 매크로 분석...")
    macro_result = macro_analyze(market_data, news_data)

    print("\n[4/10] 수급 + 외국인 종목 추적...")
    supply_result = supply_analyze(market_data, news_data)
    foreign_result = foreign_analyze(market_data)

    print("\n[5/10] 실적 + 공시 NLP 분석...")
    earnings_result = earnings_analyze(market_data, news_data)
    dart_result = dart_nlp_analyze(market_data)

    print("\n[6/10] 기술적 분석 + 감성 지수...")
    technical_result = technical_analyze(market_data, news_data)
    sentiment_result = sentiment_analyze(market_data, news_data)

    print("\n[7/10] 백테스팅 검증...")
    backtest_result = backtest_analyze(technical_result, supply_result, macro_result, market_data)
    reliability = backtest_result.get("signal_reliability", {})
    print(f"   신호 신뢰도: {reliability.get('score',0)}점 ({reliability.get('grade','-')}등급)")

    performance_html = generate_performance_html()
    stats = calculate_stats()

    print("\n[8/10] 통합 판단 + 블로그 생성...")
    afternoon_report = get_latest_afternoon_report()
    if afternoon_report:
        print(f"   전일 마감 브리핑 로드 완료: {afternoon_report.get('title')}")
    else:
        print("   전일 마감 브리핑을 찾을 수 없습니다.")

    html_content = synthesize_and_write(
        macro=macro_result, supply=supply_result,
        earnings=earnings_result, technical=technical_result,
        dart_nlp=dart_result, foreign_tracker=foreign_result,
        sentiment=sentiment_result,
        market_data={**market_data, "backtest": backtest_result, "prev_afternoon_report": afternoon_report},
        performance_html=performance_html,
        report_type="daily_v4"
    )

    html_content, validation_logs = validate_and_correct(html_content, market_data)
    if validation_logs:
        print("\n🚨 [수치 오기 및 환각 자동 교정 시스템 작동]")
        for log in validation_logs:
            print(f"  {log}")
        print("  ✅ 모든 수치 오류 교정 완료 후 저장합니다.\n")

    with open("scratch/test_daily_brief_result.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved result to scratch/test_daily_brief_result.html (length: {len(html_content)})")

if __name__ == "__main__":
    main()
