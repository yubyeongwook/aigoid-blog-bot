import sys, os, json, datetime, re
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
from backtesting.backtest_agent import analyze as backtest_analyze
from social.card_news_generator import generate as generate_social, save_social_content
from notifications.kakao_notify import send_kakao_message, send_telegram_message
from trackers.pick_tracker import update_performance, generate_performance_html, save_picks, calculate_stats
from publishers.blogger_publisher import publish_post, auto_labels

# 쇼츠 에이전트 및 유튜브 퍼블리셔 연동 임포트
from agents.shorts_director_agent import generate_shorts_script
from agents.shorts_video_agent import collect_shorts_assets
from agents.shorts_editor_agent import build_shorts_video
from publishers.youtube_publisher import upload_shorts_to_youtube

def extract_picks_from_html(html):
    picks = []
    matches = re.findall(r'([가-힣a-zA-Z·]+)\s*\((\d{6})\)', html)
    for name, ticker in matches[:8]:
        picks.append({"name":name,"ticker":ticker,"type":"단타","entry_price":0,"stop_loss":0,"target_1":0,"status":"진행중"})
    return picks[:8]

def main():
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    print("="*60)
    print(f"  멋쟁이 인사이트 v4 — 완전 고도화 (유튜브 쇼츠 에디션)")
    print(f"  {today.strftime('%Y년 %m월 %d일')} {weekday}요일 KST")
    print("="*60)

    print("\n[0/10] 전일 픽 성과 업데이트...")
    try:
        update_performance()
        performance_html = generate_performance_html()
        stats = calculate_stats()
    except Exception as e:
        print(f"픽 추적 오류: {e}")
        performance_html = ""
        stats = {}

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

    print("\n[8/10] 통합 판단 + 블로그 생성...")
    html_content = synthesize_and_write(
        macro=macro_result, supply=supply_result,
        earnings=earnings_result, technical=technical_result,
        dart_nlp=dart_result, foreign_tracker=foreign_result,
        sentiment=sentiment_result,
        market_data={**market_data, "backtest": backtest_result},
        performance_html=performance_html,
        report_type="daily_v4"
    )

    picks = extract_picks_from_html(html_content)
    if picks:
        save_picks(picks, today.strftime("%Y-%m-%d"))

    seo_title = f"{today.strftime('%m월 %d일')} {weekday}요일 멋쟁이 인사이트 — 9개 전문가 통합 분석·백테스팅 검증"
    labels = auto_labels(html_content)
    labels.extend(["멋쟁이픽","단타픽","수급분석","공시분석","백테스팅"])
    result = publish_post(seo_title, html_content, labels)
    blog_url = result.get("url", "https://aigoid.blogspot.com")

    print("\n[9/10] 소셜 콘텐츠 + 알림...")
    key_insight = macro_result.get("key_insight", "오늘의 핵심 인사이트")
    try:
        social_content = generate_social(html_content, picks, key_insight, blog_url)
        save_social_content(social_content, today.strftime("%Y%m%d"))
        
        # 인스타그램 자동 업로드 연동
        if isinstance(social_content, dict) and "instagram_card" in social_content:
            print("📸 인스타그램 카드뉴스 자동 업로드 시작...")
            try:
                from instagram_post import post_to_instagram
                card = social_content["instagram_card"]
                card_title = card.get("title", "오늘의 주식 시장 요약")
                
                # 슬라이드 텍스트 포맷팅
                slides = card.get("slides", [])
                slides_text = ""
                for s in slides:
                    slide_num = s.get("slide_num", "")
                    headline = s.get("headline", "")
                    sub_text = s.get("sub_text", "")
                    slides_text += f"{slide_num}. {headline}\n   - {sub_text}\n"
                
                # 해시태그 합치기
                hashtags_list = card.get("hashtags", ["#주식", "#투자", "#멋쟁이인사이트"])
                hashtags = " ".join(hashtags_list)
                
                # 피드 캡션 생성
                caption = f"📊 {card_title}\n\n{slides_text}\n자세한 리포트는 프로필 링크의 블로그에서 확인하세요!\n\n{hashtags}"
                
                # 백테스트 신뢰도 점수를 별표로 표기
                score = reliability.get("score", 5) if isinstance(reliability.get("score"), int) else 5
                stars_str = "★" * score
                
                insta_res = post_to_instagram(
                    title=card_title,
                    content=slides_text,
                    caption=caption,
                    stars=stars_str
                )
                print(f"인스타그램 업로드 결과: {insta_res}")
            except Exception as ie:
                print(f"인스타그램 업로드 중 오류 발생: {ie}")
    except Exception as e:
        print(f"소셜 생성 오류: {e}")
    try:
        send_kakao_message(picks, blog_url, stats)
        send_telegram_message(picks, blog_url, stats)
    except Exception as e:
        print(f"알림 오류: {e}")

    print("\n[10/10] 유튜브 쇼츠 자동 제작 및 발행...")
    try:
        # 1) 편집장 기획서(script.json) 빌드
        shorts_script = generate_shorts_script(html_content, picks)
        
        # 2) 비디오 에셋 이미지 수집 및 차트 캡처
        ready_script = collect_shorts_assets(shorts_script, picks)
        
        # 3) 오디오 및 자막 결합 렌더링
        video_output = "temp_shorts/final_shorts.mp4"
        success = build_shorts_video(ready_script, video_output)
        
        # 4) 유튜브 업로드
        if success:
            upload_success = upload_shorts_to_youtube(
                video_path=video_output,
                title=ready_script.get("title", f"{today.strftime('%m월 %d일')} 오늘의 특징 종목"),
                description=f"오늘의 주식 시장 급등 특징주 분석 브리핑!\n상세 분석 리포트 보기 👉 {blog_url}\n#Shorts #주식 #멋쟁이인사이트"
            )
            # 임시 동영상 파일 정리
            if os.path.exists(video_output):
                try:
                    os.remove(video_output)
                except Exception:
                    pass
    except Exception as e:
        print(f"유튜브 쇼츠 생성 파이프라인 에러: {e}")

    print("\n"+"="*60)
    if "url" in result:
        print(f"  ✅ 발행 완료: {blog_url}")
        print(f"  📊 누적 승률: {stats.get('win_rate',0)}%")
    else:
        print(f"  ⚠️ 결과: {result}")
    print("="*60)

if __name__ == "__main__":
    main()
