import sys, os, json, datetime, requests
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

# Import the monkeypatch first to force Gemini fallback
import agents.patch_anthropic

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.afternoon_synthesis_agent import generate_afternoon_report
from publishers.blogger_publisher import get_access_token, BLOG_ID, build_seo_title, auto_labels, get_latest_morning_brief
from main_afternoon import evaluate_morning_picks
from utils.fact_validator import validate_and_correct

def overwrite_blogger_post(post_id: str, title: str, html_content: str, labels: list) -> dict:
    token = get_access_token()
    if not token:
        return {"error": "토큰 발급 실패"}

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "kind": "blogger#post",
        "title": title,
        "content": html_content,
        "labels": labels
    }

    try:
        res = requests.put(url, headers=headers, json=body, timeout=30)
        result = res.json()
        if "url" in result:
            print(f"✅ 블로그 글 수정 완료: {result['url']}")
        else:
            print(f"⚠️ 블로그 글 수정 결과: {result}")
        return result
    except Exception as e:
        return {"error": str(e)}

def main():
    post_id = "9099326698861714150" # 오늘 오후 마감 브리핑 글 ID
    print(f"오늘 오후 마감 브리핑 글(ID: {post_id}) 복구 작업을 시작합니다.")

    # 1. 데이터 수집
    print("\n[1/4] 시장 데이터 수집...")
    market_data = collect_market()

    print("\n[2/4] 뉴스·공시 수집...")
    surging_stocks = market_data.get("surging_stocks", [])
    news_data = collect_news(surging_stocks=surging_stocks)

    # 2. 오전 픽 성적 평가
    evaluated_picks = evaluate_morning_picks()

    # 3. 리포트 생성
    print("\n[3/4] AI 리포트 생성 (Gemini 폴백 활성화)...")
    morning_brief_data = get_latest_morning_brief()
    if morning_brief_data:
        print(f"오전 브리핑 발견: {morning_brief_data.get('title')}")
    else:
        print("오전 브리핑 조회 결과가 없습니다.")
        
    html_content = generate_afternoon_report(
        market_data=market_data,
        news_data=news_data,
        morning_brief_data=morning_brief_data,
        evaluated_picks=evaluated_picks
    )

    # 4. 제목·라벨 설정
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    
    seo_title = None
    import re
    h1_tags = re.findall(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
    for tag in h1_tags:
        title_text = re.sub(r'<[^>]+>', '', tag).strip()
        title_text = " ".join(title_text.split())
        if title_text and title_text not in ["멋쟁이 인사이트", "멋쟁이인사이트"]:
            seo_title = title_text
            break

    if not seo_title:
        base_title = f"코스피 오늘 마감 — {today.strftime('%m월 %d일')} {weekday}요일 마감 브리핑"
        seo_title = build_seo_title(base_title, "daily")
        
    labels = auto_labels(html_content)
    labels.extend(["멋쟁이인사이트", "마감분석", "수급분석", "검증리포트"])
    labels = list(set(labels))

    # 수치 오기 및 환각 자동 교정
    html_content, validation_logs = validate_and_correct(html_content, market_data)
    if validation_logs:
        print("\n🚨 [수치 오기 및 환각 자동 교정 시스템 작동]")
        for log in validation_logs:
            print(f"  {log}")
        print("  ✅ 모든 수치 오류 교정 완료.\n")

    # 5. 블로그 글 덮어쓰기 (수정)
    print("\n[4/4] Blogger 기존 글 덮어쓰기 수정 시작...")
    result = overwrite_blogger_post(post_id, seo_title, html_content, labels)

    if "url" in result:
        print(f"  ✅ 블로그 복구 완료!")
        print(f"  URL: {result['url']}")
        
        # 6. 인스타그램 자동 업로드 연동
        blog_url = result["url"]
        print("\n[추가] 인스타그램 마감 카드뉴스 업로드 시도...")
        try:
            from social.card_news_generator import generate as generate_social, save_social_content
            from instagram_post import post_to_instagram
            
            social_content = generate_social(html_content, [], seo_title, blog_url)
            save_social_content(social_content, today.strftime("%Y%m%d") + "_afternoon")
            
            if isinstance(social_content, dict) and "instagram_card" in social_content:
                card = social_content["instagram_card"]
                card_title = card.get("title", f"{today.strftime('%m/%d')} 장마감 브리핑")
                
                slides = card.get("slides", [])
                slides_text = ""
                for s in slides:
                    slide_num = s.get("slide_num", "")
                    headline = s.get("headline", "")
                    sub_text = s.get("sub_text", "")
                    slides_text += f"{slide_num}. {headline}\n   - {sub_text}\n"
                
                hashtags_list = card.get("hashtags", ["#주식", "#코스피", "#마감시황", "#멋쟁이인사이트"])
                hashtags = " ".join(hashtags_list)
                caption = f"📊 {card_title}\n\n{slides_text}\n자세한 리포트는 프로필 링크의 블로그에서 확인하세요!\n\n{hashtags}"
                
                print("📸 인스타그램 마감 카드뉴스 자동 업로드 시작...")
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
    else:
        print(f"  ⚠️ 블로그 복구 실패: {result}")

if __name__ == "__main__":
    main()
