import sys, os, json, datetime, re
sys.path.append(os.path.dirname(__file__))
import agents.patch_anthropic

from collectors.market_collector import collect_premarket_data as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.premarket_synthesis_agent import generate_premarket_report
from publishers.blogger_publisher import publish_post, auto_labels, get_latest_morning_brief

def main():
    kst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    today = kst_now
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    print("="*60)
    print(f"  멋쟁이 인사이트 — 오전 8시 50분 동시호가 브리핑")
    print(f"  {today.strftime('%Y년 %m월 %d일')} {weekday}요일 KST")
    print("="*60)

    print("\n[1/5] 실시간 시장 데이터 수집 (장전 동시호가)...")
    market_data = collect_market()

    print("\n[2/5] 뉴스·공시 수집...")
    news_data = collect_news()

    print("\n[3/5] 동시호가 브리핑 생성 (속도 최적화)...")
    # 오늘 오전 7시 종합 브리핑 조회 및 연계
    morning_brief = get_latest_morning_brief()
    if morning_brief:
        print(f"   오늘 오전 브리핑 로드 완료: {morning_brief.get('title')}")
    else:
        print("   오늘 오전 브리핑을 찾을 수 없습니다.")

    html_content = generate_premarket_report(
        premarket_data={**market_data, "morning_brief": morning_brief},
        news_data=news_data
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
    blog_url = result.get("url", "https://aigoid.blogspot.com")

    print("\n"+"="*60)
    if "url" in result:
        print(f"  ✅ 동시호가 브리핑 발행 완료: {result['url']}")
        
        # 텔레그램 채널 알림 자동 발송
        print("\n[추가] 텔레그램 채널 알림 발송...")
        try:
            from notifications.kakao_notify import send_telegram_message
            send_telegram_message(
                picks=[],
                blog_url=blog_url,
                performance=None,
                news_data=news_data,
                macro_result={"key_insight": "9시 개장 직전 동시호가 브리핑입니다. 미 증시 여파 및 국내 개장 수급 흐름을 확인하십시오."}
            )
        except Exception as e:
            print(f"텔레그램 알림 발송 중 오류 발생: {e}")
    else:
        print(f"  ⚠️ 결과: {result}")
    print("="*60)

    # 인스타그램 자동 업로드 연동
    print("\n[추가] 인스타그램 카드뉴스 업로드...")
    try:
        from social.card_news_generator import generate as generate_social, save_social_content
        from instagram_post import post_to_instagram
        
        key_insight = "9시 개장 직전 동시호가 브리핑입니다. 미 증시 여파 및 국내 개장 수급 흐름을 확인하십시오."
        social_content = generate_social(html_content, [], key_insight, blog_url)
        save_social_content(social_content, today.strftime("%Y%m%d") + "_premarket")

        
        if isinstance(social_content, dict) and "instagram_card" in social_content:
            card = social_content["instagram_card"]
            card_title = card.get("title", f"{today.strftime('%m/%d')} 장전 동시호가 브리핑")
            
            # 슬라이드 텍스트 포맷팅
            slides = card.get("slides", [])
            slides_text = ""
            for s in slides:
                slide_num = s.get("slide_num", "")
                headline = s.get("headline", "")
                sub_text = s.get("sub_text", "")
                slides_text += f"{slide_num}. {headline}\n   - {sub_text}\n"
            
            # 해시태그 합치기
            hashtags_list = card.get("hashtags", ["#주식", "#동시호가", "#멋쟁이인사이트"])
            hashtags = " ".join(hashtags_list)
            
            caption = f"📊 {card_title}\n\n{slides_text}\n자세한 리포트는 프로필 링크의 블로그에서 확인하세요!\n\n{hashtags}"
            
            print("📸 인스타그램 동시호가 카드뉴스 자동 업로드 시작...")
            inst_result = post_to_instagram(
                title=card_title,
                content=card.get("content_summary", card_title),
                caption=caption,
                stars=""
            )
            if inst_result.get("success"):
                print(f"  ✅ 인스타그램 업로드 완료: {inst_result.get('post_url')}")
            else:
                print(f"  ⚠️ 인스타그램 업로드 실패: {inst_result.get('error')}")
    except Exception as e:
        print(f"인스타그램 업로드 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
