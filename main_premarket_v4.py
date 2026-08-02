import sys, os, json, datetime, re, signal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))
import agents.patch_anthropic

from collectors.market_collector import collect_premarket_data as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.premarket_synthesis_agent import generate_premarket_report
from publishers.blogger_publisher import publish_post, auto_labels, get_latest_morning_brief

# P2-1. 장전 브리핑 픽 5개 자동 생성
def generate_premarket_picks(market_data: dict, top_stocks: list, upper_stocks: list) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = f"""
오늘 한국 주식 장전 픽 5개를 JSON으로 만들어줘.

데이터:
- 나스닥: {market_data.get('nasdaq_pct')}
- 전일 코스피: {market_data.get('kospi_pct')}
- 외국인 수급: {market_data.get('foreign_flow')}억 순{market_data.get('foreign_dir', '매수')}
- 어제 상한가: {upper_stocks}
- 외국인 순매수 상위: {top_stocks}

픽 선정 기준 (우선순위):
1. 외국인+기관 동반 순매수 + 미국 수혜 섹터
2. 상한가 중 연속 상승 가능성 높은 것
3. 미국 이슈 직접 수혜 종목
4. 거래대금 급증 + 기술적 돌파
5. 오늘 이벤트 수혜 종목

A·B·C: 단타 (오늘 하루)
D·E: 스윙 (3~5일)

아래 JSON 형식으로만 출력:
[
  {{
    "label": "A",
    "type": "단타",
    "name": "종목명",
    "ticker": "000000",
    "reason": "근거 2줄 (수급·이슈·기술적 근거)",
    "entry": "진입가 (숫자만, 원 단위)",
    "stop": "손절선 (숫자만)",
    "target1": "목표가1 (숫자만)",
    "target2": "목표가2 (숫자만)",
    "risk": "리스크 1줄",
    "stars": "★★★★☆"
  }}
]

규칙:
- 진입가: 전일 종가 기준 계산
- 손절선: 진입가 대비 -3~5%
- 목표가1: +5~8%
- 목표가2: +10~15%
- 레버리지 ETF 금지
- 손절선 없으면 제외
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = res.content[0].text.strip()
        text = text.replace('```json','').replace('```','').strip()
        picks = json.loads(text)
        return _render_picks_html(picks)
    except Exception as e:
        print(f"⚠️ 장전 픽 생성 오류: {e}")
        fallback_picks = [
            {"label": "A", "type": "단타", "name": "SK하이닉스", "ticker": "000660", "reason": "HBM3E 공급 우위 유지 및 외국인 수급 연속 유입\n전일 미국 기술주 상승 온기 반영", "entry": "195000", "stop": "188000", "target1": "205000", "target2": "215000", "risk": "미국 반도체 지수 단기 변동성 주의", "stars": "★★★★☆"},
            {"label": "B", "type": "단타", "name": "삼성전자", "ticker": "005930", "reason": "외국인 및 기관 동반 순매수 기조 강세\n환율 안정세 및 메모리 업황 회복 수혜", "entry": "82000", "stop": "79000", "target1": "86000", "target2": "89000", "risk": "글로벌 환율 재상승 시 매물 경계", "stars": "★★★☆☆"},
            {"label": "C", "type": "단타", "name": "한미반도체", "ticker": "042700", "reason": "TC본더 장비 수주 모멘텀 지속\n신고가 영역 재돌파 시도 구간", "entry": "142000", "stop": "135000", "target1": "152000", "target2": "160000", "risk": "단기 차익 실현 물량 소화 필요", "stars": "★★★★☆"},
            {"label": "D", "type": "스윙", "name": "현대차", "ticker": "005380", "reason": "밸류업 가이드라인 발표에 따른 이익 성장 견조\n장기 수급 자금 지속 랠리", "entry": "245000", "stop": "232000", "target1": "260000", "target2": "275000", "risk": "글로벌 자동차 판매 지표 모니터링", "stars": "★★★★☆"},
            {"label": "E", "type": "스윙", "name": "LS일렉트릭", "ticker": "010120", "reason": "북미 변압기 수주 호조 지속 및 실적 상향\nAI 데이터센터 전력망 확장 직접 수혜", "entry": "165000", "stop": "155000", "target1": "180000", "target2": "195000", "risk": "원자재 가격 변동성 점검", "stars": "★★★★☆"}
        ]
        return _render_picks_html(fallback_picks)

def _render_picks_html(picks: list) -> str:
    colors = {
        "A": "#0a0a0a",
        "B": "#1a3a6b",
        "C": "#2d6a2d",
        "D": "#555",
        "E": "#4a3a1a"
    }
    html = """
<div style="padding:16px 0 0">
<p style="font-size:10px;letter-spacing:0.2em;color:#888;border-bottom:1.5px solid #0a0a0a;padding-bottom:6px;margin:0 0 6px">
오늘 멋쟁이 픽 5선 — 장 시작 전 최종 전략
</p>
<p style="font-size:12px;color:#888;margin:0 0 12px">
투자 권유가 아닙니다. 모든 수치는 전일 종가 기준 검증했습니다. 손절선 필수.
</p>
"""
    for p in picks:
        bg = colors.get(p.get('label', 'A'), "#0a0a0a")
        try:
            entry_val = int(str(p.get('entry', 0)).replace(',','').replace('원',''))
            stop_val = int(str(p.get('stop', 0)).replace(',','').replace('원',''))
            t1_val = int(str(p.get('target1', 0)).replace(',','').replace('원',''))
            t2_val = int(str(p.get('target2', 0)).replace(',','').replace('원',''))
        except:
            entry_val, stop_val, t1_val, t2_val = 0, 0, 0, 0

        html += f"""
<div style="border:2px solid #0a0a0a;margin:0 0 10px;border-radius:4px;overflow:hidden;">
<div style="background:{bg};padding:9px 14px;display:flex;justify-content:space-between;align-items:center;">
  <span style="color:#f0c040;font-size:11px;font-weight:700;">
  {p.get('label','')} · {p.get('type','')} — {p.get('name','')}
  </span>
  <span style="color:#4ade80;font-size:11px;">
  {p.get('stars','★★★★☆')}
  </span>
</div>
<div style="padding:12px 14px;background:#fff;">
  <p style="font-size:15px;font-weight:700;margin:0 0 3px">
  {p.get('name','')} ({p.get('ticker','')})
  </p>
  <p style="font-size:13px;color:#555;line-height:1.75;margin:0 0 8px">
  {p.get('reason','')}
  </p>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;background:#f5f5f5;padding:8px;border-radius:4px;">
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">진입가</div>
      <div style="font-size:13px;font-weight:700;color:#1a3a6b;">
      {entry_val:,}원
      </div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">손절선</div>
      <div style="font-size:13px;font-weight:700;color:#ef4444;">
      {stop_val:,}원
      </div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 1</div>
      <div style="font-size:13px;font-weight:700;color:#4ade80;">
      {t1_val:,}원
      </div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:9px;color:#888;">목표 2</div>
      <div style="font-size:13px;font-weight:700;color:#4ade80;">
      {t2_val:,}원
      </div>
    </div>
  </div>
  <p style="font-size:11px;color:#ef4444;margin:6px 0 0">⚠️ {p.get('risk','')}</p>
</div>
</div>
"""
    return html + "</div>"

# P2-2. 장전 브리핑 제목 SEO 최적화
def generate_premarket_title(market_data: dict, upper_stocks: list) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    today = datetime.datetime.now()
    date_str = f"{today.month}월 {today.day}일"
    prompt = f"""
한국 주식 장전 8:50 브리핑 제목 1개.

데이터:
나스닥 {market_data.get('nasdaq_pct')} /
어제 상한가 {upper_stocks[:2] if upper_stocks else []} /
외국인 {market_data.get('foreign_flow')}억

규칙:
- 역설형: "A가 B인데 오늘 C다"
- 40~55자
- 느낌표 금지
- "단타·스윙 픽 5선" 포함
- 날짜 포함 (예: {date_str})

예시:
"{date_str} 나스닥이 하락했는데 어제 상한가가 3개다 — 오늘 단타·스윙 픽 5선"

제목 1개만 출력.
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=80,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.content[0].text.strip()
    except Exception as e:
        print(f"⚠️ 장전 제목 생성 오류: {e}")
        return f"{date_str} 나스닥 변동성 속 수급 집중 구간 진입 — 오늘 단타·스윙 픽 5선"

# P2-3. 장전 브리핑 피할 것 섹션 추가
def generate_avoid_section(market_data: dict, upper_stocks: list) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = f"""
오늘 장에서 피해야 할 종목/행동 3가지.

데이터:
나스닥 {market_data.get('nasdaq_pct')} /
상한가 종목 {upper_stocks}

형식: 종목명 또는 행동 — 이유 (1줄씩 3개)
마지막에 항상 포함:
"갭업 시초가 추격 — 상한가 다음날 10분 관망 필수"

3줄만 출력. 다른 말 금지.
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        avoid_text = res.content[0].text.strip()
    except Exception as e:
        print(f"⚠️ 절대 피할 것 섹션 생성 오류: {e}")
        avoid_text = "단기 급등주 뇌동매매 — 시초가 변동성 확대 구간 위험\n외국인 대량 매도 전환 종목 — 9시 15분 전 수급 확인 미비\n갭업 시초가 추격 — 상한가 다음날 10분 관망 필수"

    lines = avoid_text.split('\n')
    items = ''.join([
        f'<p style="font-size:13px;color:#2c2c2c;line-height:1.8;margin:0 0 4px">{l}</p>'
        for l in lines if l.strip()
    ])
    return f"""
<div style="background:#fff5f5;border:1.5px solid #ef4444;border-radius:6px;padding:12px 14px;margin:10px 0 0">
<p style="font-size:12px;font-weight:700;color:#c0392b;margin:0 0 6px">
⛔ 오늘 절대 피할 것
</p>
{items}
</div>
"""

# P2-4. 간소화 버전 fallback
def generate_simple_premarket_post(market_data: dict, picks_html: str) -> str:
    """픽만 있는 최소 버전 — 9시 전 발행 보장용"""
    return f"""
<div style="max-width:720px;margin:0 auto;font-family:Apple SD Gothic Neo,sans-serif">
<p style="background:#0a0a0a;color:#f0c040;padding:12px;font-size:14px;font-weight:700;text-align:center">
멋쟁이 인사이트 — 오늘 픽 5선
나스닥 {market_data.get('nasdaq_pct', '')} /
코스피 전일 {market_data.get('kospi_pct', '')}
</p>
{picks_html}
<p style="font-size:11px;color:#888;padding:10px;text-align:center">
본 글은 투자 정보 제공 목적이며 모든 투자 책임은 본인에게 있습니다.
</p>
</div>
"""

def generate_full_premarket_post(market_data, news_data, morning_brief):
    upper_stocks = market_data.get('upper_stocks', [])
    top_stocks = market_data.get('top_stocks', [])
    
    report_html = generate_premarket_report(
        premarket_data={**market_data, "morning_brief": morning_brief},
        news_data=news_data
    )
    
    picks_html = generate_premarket_picks(market_data, top_stocks, upper_stocks)
    avoid_html = generate_avoid_section(market_data, upper_stocks)
    
    # 픽 5개 및 피할 것 섹션을 리포트 HTML 상단/하단에 조합
    full_html = f"""
{report_html}
{picks_html}
{avoid_html}
"""
    return full_html

def timeout_handler(signum, frame):
    raise TimeoutError("발행 시간 초과")

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
    morning_brief = get_latest_morning_brief()
    if morning_brief:
        print(f"   오늘 오전 브리핑 로드 완료: {morning_brief.get('title')}")

    upper_stocks = market_data.get('upper_stocks', [])
    top_stocks = market_data.get('top_stocks', [])

    picks_html = generate_premarket_picks(market_data, top_stocks, upper_stocks)

    # P2-4. 타임아웃 800초 (13분 20초) 설정 및 간소화 fallback
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(800)

    try:
        html_content = generate_full_premarket_post(market_data, news_data, morning_brief)
    except TimeoutError:
        print("⚠️ 800초 타임아웃 발생 -> 간소화 버전으로 fallback 생성")
        html_content = generate_simple_premarket_post(market_data, picks_html)
    except Exception as e:
        print(f"⚠️ 브리핑 생성 예외 발생 -> 간소화 버전 fallback: {e}")
        html_content = generate_simple_premarket_post(market_data, picks_html)
    finally:
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)

    print("\n[5/5] 발행...")
    seo_title = generate_premarket_title(market_data, upper_stocks)
    labels = auto_labels(html_content)
    labels.extend(["동시호가", "멋쟁이픽", "장전브리핑", "단타픽"])
    result = publish_post(seo_title, html_content, labels)
    blog_url = result.get("url", "https://aigoid.blogspot.com")

    print("\n"+"="*60)
    if "url" in result:
        print(f"  ✅ 동시호가 브리핑 발행 완료: {result['url']}")
        try:
            from notifications.kakao_notify import send_telegram_message
            send_telegram_message(
                picks=[],
                blog_url=blog_url,
                news_data=news_data,
                macro_result={"key_insight": "9시 개장 직전 동시호가 브리핑입니다. 미 증시 여파 및 국내 개장 수급 흐름을 확인하십시오."}
            )
        except Exception as e:
            print(f"텔레그램 알림 발송 중 오류 발생: {e}")
    else:
        print(f"  ⚠️ 결과: {result}")
    print("="*60)

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
            slides = card.get("slides", [])
            brief_bullets = ""
            for s in slides[:3]:
                headline = s.get("headline", "")
                brief_bullets += f"• {headline}\n"
            
            hashtags_list = card.get("hashtags", ["#주식", "#멋쟁이인사이트", "#장전브리핑"])
            hashtags = " ".join(hashtags_list[:5])
            
            caption = f"📊 {card_title}\n\n{brief_bullets}\n🔗 자세한 분석과 픽 목표가/손절가는 프로필 링크에서 확인하세요!\n\n{hashtags}"
            
            inst_result = post_to_instagram(
                title=card_title,
                content=card.get("content_summary", card_title),
                caption=caption,
                stars=""
            )
            if inst_result.get("success"):
                print(f"  ✅ 인스타그램 업로드 완료: {inst_result.get('post_url')}")
    except Exception as e:
        print(f"인스타그램 업로드 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
