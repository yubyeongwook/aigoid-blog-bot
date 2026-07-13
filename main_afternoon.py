"""
main_afternoon.py — 오후 마감 자동 실행 메인
매일 오후 4시 실행 (깃허브 액션)
오전 픽 적중률 검증 및 3,000자 이상 마감 브리핑 발행
"""
import sys, os, json, datetime
from dotenv import load_dotenv
load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.dirname(__file__))

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.afternoon_synthesis_agent import generate_afternoon_report
from publishers.blogger_publisher import publish_post, build_seo_title, auto_labels, get_latest_morning_brief
from pykrx import stock
import yfinance as yf
import pandas as pd

def is_market_holiday() -> bool:
    import datetime, requests
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    kst_today = (utc_now + datetime.timedelta(hours=9)).date()
    
    if kst_today.weekday() >= 5:
        return True
        
    if kst_today.month == 12 and kst_today.day == 31:
        return True
        
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

def evaluate_morning_picks() -> list:
    print("🧹 오전 픽(Picks) 실시간 성적 평가 중...")
    picks_path = "scratch/morning_picks.json"
    if not os.path.exists(picks_path):
        print("📢 scratch/morning_picks.json 파일이 없습니다. 공백 리스트 반환.")
        return []
        
    try:
        with open(picks_path, "r", encoding="utf-8") as f:
            picks = json.load(f)
    except Exception as e:
        print(f"⚠️ 픽 파일 로딩 실패: {e}")
        return []

    # 최근 거래일 날짜 구하기 (pykrx 조회용)
    today = datetime.datetime.now()
    d = today
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    today_str = d.strftime("%Y%m%d")

    try:
        print(f"pykrx를 통한 {today_str} 전 종목 마감 시세 조회...")
        df = stock.get_market_ohlcv_by_ticker(today_str, market="ALL")
    except Exception as e:
        print(f"⚠️ pykrx 지수 조회 실패: {e}")
        df = pd.DataFrame()

    evaluated = []
    for pick in picks:
        ticker = pick.get("ticker", "").strip()
        name = pick.get("name", "").strip()
        entry = pick.get("entry", 0)
        target = pick.get("target", 0)
        stop = pick.get("stop", 0)
        
        # 숫자 정제
        def clean_num(val):
            try:
                return float(str(val).replace(",","").replace("원","").replace("$","").strip())
            except:
                return 0.0

        entry_val = clean_num(entry)
        target_val = clean_num(target)
        stop_val = clean_num(stop)

        high = 0
        close = 0
        rate = 0.0
        status = "평가 대기"

        # 1. 한국 시장 종목 여부 판단
        if df is not None and not df.empty and ticker in df.index:
            row = df.loc[ticker]
            high = int(row["고가"])
            close = int(row["종가"])
            rate = float(row["등락률"])
            
            if high >= target_val and target_val > 0:
                status = "목표가 달성 (성공)"
            elif close <= stop_val and stop_val > 0:
                status = "손절선 이탈 (실패)"
            elif close > entry_val and entry_val > 0:
                status = "수익 마감 (성공)"
            else:
                status = "보합/약세 (실패)"
        else:
            # 2. 미국 시장 종목 또는 기타 종목 (yfinance 조회)
            try:
                sym = ticker
                # 한국 종목인데 pykrx 인덱스에 없었을 가능성 체크 (ex: 코드가 숫자인 경우)
                if ticker.isdigit():
                    # 한국 종목 코드인 경우 yfinance 조회 시 suffix(.KS / .KQ) 처리
                    sym = f"{ticker}.KS"
                    t = yf.Ticker(sym)
                    hist = t.history(period="1d")
                    if hist.empty:
                        sym = f"{ticker}.KQ"
                        t = yf.Ticker(sym)
                        hist = t.history(period="1d")
                else:
                    # 미국 또는 해외 주식
                    t = yf.Ticker(sym)
                    hist = t.history(period="1d")

                if not hist.empty:
                    high = round(float(hist["High"].iloc[-1]), 2)
                    close = round(float(hist["Close"].iloc[-1]), 2)
                    prev_close = t.info.get("previousClose", close)
                    
                    if ticker.isdigit():
                        high = round(high / 10, 2)
                        close = round(close / 10, 2)
                        prev_close = round(prev_close / 10, 2)

                    rate = round((close - prev_close) / prev_close * 100, 2)
                    
                    if high >= target_val and target_val > 0:
                        status = "목표가 달성 (성공)"
                    elif close <= stop_val and stop_val > 0:
                        status = "손절선 이탈 (실패)"
                    elif close > entry_val and entry_val > 0:
                        status = "수익 마감 (성공)"
                    else:
                        status = "보합/약세 (실패)"
            except Exception as ex:
                print(f"yfinance 조회 오류 ({ticker}): {ex}")
                status = "데이터 조회 실패"

        evaluated.append({
            "ticker": ticker,
            "name": name,
            "entry": entry,
            "target": target,
            "stop": stop,
            "actual_high": high,
            "actual_close": close,
            "actual_rate": rate,
            "status": status
        })
        
    print(f"✅ 총 {len(evaluated)}개 종목 평가 완료")
    return evaluated

def main():
    if is_market_holiday() and os.getenv("FORCE_RUN") != "true":
        print("📢 오늘은 한국 거래소 휴장일(또는 주말)입니다. 작업을 건너뜁니다.")
        return

    print("=" * 60)
    print(f"  멋쟁이 인사이트 — 오후 마감 리포트 (v2.1)")
    print(f"  실행 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 1. 데이터 수집
    print("\n[1/4] 시장 데이터 수집...")
    market_data = collect_market()

    print("\n[2/4] 뉴스·공시 수집...")
    surging_stocks = market_data.get("surging_stocks", [])
    news_data = collect_news(surging_stocks=surging_stocks)

    # 2. 오전 픽 성적 평가
    evaluated_picks = evaluate_morning_picks()

    # 3. 리포트 생성
    print("\n[3/4] AI 리포트 생성...")
    print("오전 발행된 브리핑 조회 중...")
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
    
    # <h1> 태그들 중 "멋쟁이 인사이트"가 아닌 진짜 제목 추출 시도
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

    # 5. 발행
    print("\n[4/4] Blogger 자동 발행...")
    # 정각 17:00:00 KST 발행 타겟팅 (일정/소급)
    kst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    target_kst = datetime.datetime(kst_now.year, kst_now.month, kst_now.day, 17, 0, 0)
    published_time = target_kst.isoformat() + "+09:00"

    result = publish_post(seo_title, html_content, labels, published_time=published_time)

    print("\n" + "=" * 60)
    if "url" in result:
        print(f"  ✅ 발행 완료!")
        print(f"  URL: {result['url']}")
        
        # 6. 인스타그램 자동 업로드 연동
        blog_url = result["url"]
        print("\n[추가] 인스타그램 마감 카드뉴스 업로드...")
        try:
            from social.card_news_generator import generate as generate_social, save_social_content
            from instagram_post import post_to_instagram
            
            social_content = generate_social(html_content, [], seo_title, blog_url)
            save_social_content(social_content, today.strftime("%Y%m%d") + "_afternoon")
            
            if isinstance(social_content, dict) and "instagram_card" in social_content:
                card = social_content["instagram_card"]
                card_title = card.get("title", f"{today.strftime('%m/%d')} 장마감 브리핑")
                
                # 슬라이드 텍스트 포맷팅
                slides = card.get("slides", [])
                slides_text = ""
                for s in slides:
                    slide_num = s.get("slide_num", "")
                    headline = s.get("headline", "")
                    sub_text = s.get("sub_text", "")
                    slides_text += f"{slide_num}. {headline}\n   - {sub_text}\n"
                
                # 해시태그 합치기
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
        print(f"  ⚠️ 발행 결과: {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
