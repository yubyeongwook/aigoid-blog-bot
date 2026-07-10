"""
main_premarket.py — 개장 직전 동시호가 속보 자동 실행 메인
매일 오전 8시 45분 깃허브 액션이 자동 실행
"""
import sys, os, json, datetime
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.dirname(__file__))

from collectors.market_collector import collect_premarket_data
from generators.report_generator import generate_premarket_report
from publishers.blogger_publisher import publish_post, build_seo_title, auto_labels, get_latest_morning_brief

def is_market_holiday() -> bool:
    import requests
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    kst_today = (utc_now + datetime.timedelta(hours=9)).date()
    
    # 1. 주말 체크
    if kst_today.weekday() >= 5:
        return True
        
    # 2. 연말 휴장일 (12월 31일)
    if kst_today.month == 12 and kst_today.day == 31:
        return True
        
    # 3. 공공 휴일 API 체크
    try:
        url = f"https://date.nager.at/api/v3/publicholidays/{kst_today.year}/KR"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            holidays = [h.get("date") for h in res.json()]
            today_str = kst_today.strftime("%Y-%m-%d")
            if today_str in holidays:
                return True
    except Exception as e:
        print(f"⚠️ 휴일 API 조회 실패, 기본 작동 처리: {e}")
        
    return False

def main():
    if is_market_holiday():
        print("📢 오늘은 한국 거래소 휴장일(또는 주말)입니다. 작업을 건너뜁니다.")
        return

    print("=" * 60)
    print(f"  멋쟁이 인사이트 — 개장 직전 동시호가 속보")
    print(f"  실행 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 1. 데이터 수집
    print("\n[1/4] 장전 동시호가 데이터 수집...")
    premarket_data = collect_premarket_data()

    # 2. 오전 브리핑 정보 조회
    print("\n오전 발행된 매크로 브리핑 조회 중...")
    morning_brief_data = get_latest_morning_brief()
    if morning_brief_data:
        print(f"오전 브리핑 발견: {morning_brief_data.get('title')}")
    else:
        print("오전 브리핑 조회 결과가 없습니다.")

    # 3. 리포트 생성
    print("\n[2/4] AI 개장 속보 리포트 생성...")
    html_content = generate_premarket_report(premarket_data, morning_brief_data)

    # 4. 제목·라벨 설정
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    
    seo_title = None
    import re
    
    # 1. JSON-LD "headline" 추출 시도
    headline_match = re.search(r'"headline"\s*:\s*"([^"]+)"', html_content)
    if headline_match:
        temp_title = headline_match.group(1).strip()
        if temp_title and temp_title not in ["멋쟁이 인사이트", "멋쟁이인사이트"]:
            seo_title = temp_title

    # 2. <h1> 태그들 중 "멋쟁이 인사이트"가 아닌 진짜 제목 추출 시도
    if not seo_title:
        h1_tags = re.findall(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
        for tag in h1_tags:
            title_text = re.sub(r'<[^>]+>', '', tag).strip()
            title_text = " ".join(title_text.split())
            if title_text and title_text not in ["멋쟁이 인사이트", "멋쟁이인사이트"]:
                seo_title = title_text
                break

    if not seo_title:
        base_title = f"[개장 10분 전] 코스피 동시호가 분석 — 오늘 상승 테마와 주목할 종목"
        seo_title = build_seo_title(base_title, "special")
        
    labels = auto_labels(html_content)

    # 5. 발행
    print("\n[3/4] Blogger 자동 발행...")
    # 정각 08:50:00 KST 발행 타겟팅 (일정/소급)
    kst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    target_kst = datetime.datetime(kst_now.year, kst_now.month, kst_now.day, 8, 50, 0)
    published_time = target_kst.isoformat() + "+09:00"

    result = publish_post(seo_title, html_content, labels, published_time=published_time)

    print("\n" + "=" * 60)
    if "url" in result:
        print(f"  ✅ 발행 완료!")
        print(f"  URL: {result['url']}")
    else:
        print(f"  ⚠️ 발행 결과: {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
