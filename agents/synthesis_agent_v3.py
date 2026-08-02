"""
synthesis_agent_v3.py — 통합 판단 에이전트 v3
6개 전문가 분석 통합
모바일 친화적 · 검정 배경 대시보드 · 역설형 SEO 제목 · 마스트헤드 · 멋쟁이의 시각
"""
import os, json, datetime, re, requests
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

UNSPLASH_IMAGE_URL = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=900&auto=format&fit=crop&q=80"

# P1-1. 역설형 SEO 제목 자동 생성
def generate_seo_title(market_data: dict, news_items: list = None) -> str:
    import anthropic, os
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    nasdaq = market_data.get('nasdaq_pct', '')
    kospi  = market_data.get('kospi_pct', '')
    flow   = market_data.get('foreign_flow', '')
    news   = news_items[0] if (news_items and isinstance(news_items, list) and len(news_items) > 0) else ''
    if isinstance(news, dict):
        news = news.get("title", str(news))

    prompt = f"""
한국 주식 블로그 제목 1개 만들어줘.

데이터:
나스닥 {nasdaq} / 코스피 {kospi} /
외국인 {flow}억 / 핵심이슈: {news}

규칙:
- 역설형: "A가 B인데 C다 — D"
- 느낌표 절대 금지
- 40~55자
- 한국어만
- 코스피·나스닥·반도체·외국인·상한가 중 1개 이상

좋은 예:
"나스닥이 -5% 빠졌는데 외국인이 2조를 샀다 — 오늘 코스피 역설의 구조"
"필라델피아반도체 -5% 폭락인데 SK하이닉스 64조가 이걸 뒤집는다"

나쁜 예 (절대 금지):
"07월 30일 목요일 코스피 분석 — 시장 주요 변수 통합 정리"

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
        print(f"SEO 제목 생성 오류: {e}")
        today = datetime.datetime.now()
        weekday = ["월","화","수","목","금","토","일"][today.weekday()]
        return f"나스닥이 흔들렸는데 외국인은 샀다 — {today.strftime('%m월 %d일')} {weekday}요일 코스피 역설의 구조"


# P1-2. 멋쟁이 시각 Claude API 강화
def generate_meotjaengi_view(market_data: dict, analysis: str) -> str:
    import anthropic, os
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    prompt = f"""
멋쟁이 인사이트 블로그 핵심 분석 3단락 써줘.

시장 데이터: {market_data}
분석 내용: {analysis}

형식:
1단락: 반직관적 사실 1가지
       (대부분이 모르는 오늘 시장의 핵심)
2단락: 투자 거장 인용 1명
       (달리오·하워드막스·드러켄밀러 중 택1)
       인용 적용 + 오늘 시장에 연결
3단락: 오전 9시 10분 외국인 수급이
       오늘 모든 것을 결정한다는 결론

규칙:
- 각 단락 3~4줄
- 느낌표 금지
- "~다" 어체 (존댓말 금지)
- 구체적 수치 반드시 포함
- "신중하게" "보수적으로" 같은 뻔한 결론 금지
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.content[0].text.strip()
    except Exception as e:
        print(f"멋쟁이 시각 생성 오류: {e}")
        return "글로벌 시장의 동조성이 강해진 상황에서 환율 및 외국인 선물 수급 이동이 시장의 향방을 가르고 있다.\n하워드 막스는 시장의 극단에서 반대편 위험에 대비할 것을 강조했다.\n오전 9시 10분 외국인 순매수 전환 여부가 장중 주도 섹터를 확정할 것이다."


# P1-3. 마스트헤드 추가
def generate_masthead(date_str, weekday, vol_no, brief_type, keyword) -> str:
    return f"""
<div style="max-width:720px;margin:0 auto;font-family:Apple SD Gothic Neo,Malgun Gothic,sans-serif;color:#1a1a1a;line-height:1.9;padding:0 4px">
<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-top:5px solid #0a0a0a;border-bottom:2px solid #0a0a0a">
<tr>
  <td width="30%" style="padding:14px 0 12px;vertical-align:middle">
    <span style="font-size:10px;color:#888;line-height:1.7">
    VOL.2026 · NO.{vol_no}<br>
    {brief_type}<br>
    {date_str}
    </span>
  </td>
  <td width="40%" style="padding:14px 0 12px;vertical-align:middle;text-align:center">
    <p style="font-family:Georgia,serif;font-size:22px;font-weight:700;margin:0 0 2px">
    멋쟁이 인사이트</p>
    <p style="font-size:9px;letter-spacing:0.16em;color:#888;margin:0">SMART MONEY INTELLIGENCE</p>
  </td>
  <td width="30%" style="padding:14px 0 12px;vertical-align:middle;text-align:right">
    <span style="font-size:10px;color:#888;line-height:1.7">
    {date_str} {weekday}요일<br>
    {keyword}
    </span>
  </td>
</tr>
</table>
"""


# P1-4. 수치 대시보드 검정 배경으로 교체
def generate_dashboard(market_data: dict) -> str:
    def c(v):
        try:
            return "#4ade80" if float(
                str(v).replace('%','').replace('+','')
            ) >= 0 else "#ef4444"
        except:
            return "#f0c040"

    n_p = market_data.get('nasdaq_pct','')
    n_v = market_data.get('nasdaq_val','')
    s_p = market_data.get('sp500_pct','')
    s_v = market_data.get('sp500_val','')
    x_p = market_data.get('soxx_pct','')
    usd = market_data.get('usdkrw','')
    k_p = market_data.get('kospi_pct','')
    k_v = market_data.get('kospi_val','')
    d_p = market_data.get('kosdaq_pct','')
    wti = market_data.get('wti','')
    vix = market_data.get('vix','')
    ff  = market_data.get('foreign_flow','')
    fd  = market_data.get('foreign_dir','매수')

    return f"""
<table width="100%" cellpadding="0" cellspacing="1" style="border-collapse:separate;border-spacing:1px;background:#111">
<tr>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">나스닥</p>
    <p style="font-size:14px;font-weight:700;color:{c(n_p)};margin:0 0 1px;font-family:Georgia,serif">{n_p}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{n_v}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">S&P500</p>
    <p style="font-size:14px;font-weight:700;color:{c(s_p)};margin:0 0 1px;font-family:Georgia,serif">{s_p}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{s_v}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">필라델피아반도체</p>
    <p style="font-size:14px;font-weight:700;color:{c(x_p)};margin:0 0 1px;font-family:Georgia,serif">{x_p}</p>
    <p style="font-size:10px;color:#aaa;margin:0"></p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">원달러 환율</p>
    <p style="font-size:14px;font-weight:700;color:#f0c040;margin:0 0 1px;font-family:Georgia,serif">{usd}</p>
    <p style="font-size:10px;color:#aaa;margin:0">원</p>
  </td>
</tr>
</table>
<table width="100%" cellpadding="0" cellspacing="1" style="border-collapse:separate;border-spacing:1px;background:#111;margin:1px 0 0">
<tr>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">코스피 전일</p>
    <p style="font-size:12px;font-weight:700;color:{c(k_p)};margin:0 0 1px">{k_p}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{k_v}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">코스닥 전일</p>
    <p style="font-size:12px;font-weight:700;color:{c(d_p)};margin:0 0 1px">{d_p}</p>
    <p style="font-size:10px;color:#aaa;margin:0"></p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">WTI 유가</p>
    <p style="font-size:12px;font-weight:700;color:#f0c040;margin:0 0 1px">{wti}</p>
    <p style="font-size:10px;color:#aaa;margin:0">달러</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">외국인 수급</p>
    <p style="font-size:12px;font-weight:700;color:{c(ff if fd=='매수' else '-'+str(ff))};margin:0 0 1px">{ff}억</p>
    <p style="font-size:10px;color:#aaa;margin:0">순{fd}</p>
  </td>
</tr>
</table>
"""

# 이전 명칭 호환성 유지
generate_dashboard_html = generate_dashboard


# P1-5. 출처 푸터 개선
def generate_footer(market_data: dict, sources: list = None) -> str:
    import datetime
    t = datetime.datetime.now().strftime("%H:%M KST")
    src = ' / '.join(sources) if sources else 'KRX·한국경제·뉴스핌·TradingKey·Yahoo Finance'
    return f"""
<p style="background:#f5f4f0;border-radius:8px;padding:10px 14px;font-size:10px;color:#999;line-height:1.8;margin:8px 0 0">
확정 수치 ({t} 기준):
나스닥 {market_data.get('nasdaq_pct','')} /
S&P500 {market_data.get('sp500_pct','')} /
필라반도체 {market_data.get('soxx_pct','')} /
코스피 {market_data.get('kospi_pct','')} /
코스닥 {market_data.get('kosdaq_pct','')} /
외국인 {market_data.get('foreign_flow','')}억
순{market_data.get('foreign_dir','')} /
원달러 {market_data.get('usdkrw','')}원 /
WTI {market_data.get('wti','')}달러
({src}) / 본 글은 참고용입니다.
</p>
"""


# P1-6. 픽 성과 섹션 완전 제거 (리턴 빈 문자열)
def generate_performance_html(picks=None):
    return ""


# P1-7. 투자 고지 강화
DISCLAIMER_HTML = """
<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border:2px solid #c0392b;margin:14px 0 0">
<tr><td style="background:#c0392b;padding:10px 16px">
<p style="font-size:11px;font-weight:700;color:#fff;margin:0">투자 위험 고지</p>
</td></tr>
<tr><td style="background:#fff8f7;padding:12px 16px">
<p style="font-size:12.5px;color:#5a1a1a;line-height:1.8;margin:0 0 8px">
<strong style="color:#c0392b">본 글은 투자 정보 제공 목적이며 특정 종목의 매수·매도를 권유하지 않습니다.</strong>
시장 상황은 실시간으로 변하며 본 분석과 다를 수 있습니다.
</p>
<p style="font-size:12.5px;color:#5a1a1a;margin:0">
<strong style="color:#c0392b">모든 투자의 최종 판단과 책임은 전적으로 투자자 본인에게 있습니다.</strong>
</p>
</td></tr>
</table>
"""

SYNTHESIS_V3_SYSTEM = """
당신은 멋쟁이 인사이트의 수석이사(Chief Managing Director)이자 최고투자전략책임자입니다.
6개 분야 수석 분석가(매크로·수급·실적·기술적·공시NLP·감성)의 분석 보고서를 정교하게 종합하여,
세계 최강 헤지펀드의 전략 보고서 수준으로 시장의 이면을 꿰뚫는 고품격 블로그 포스트를 작성합니다.

규칙:
1. 느낌표(!) 사용 절대 금지 · 급등예상 등의 자극적인 선동 표현 금지
2. 개별 종목 매수 추천 및 단타 픽은 절대 본문에 작성하지 마십시오.
3. 본문 가독성을 위해 문단 스타일: line-height: 1.95, font-size: 14.5px, color: #334155 적용.
4. 로마숫자(I. II. III. IV.)를 사용한 논리적 섹션 구분.
"""

def synthesize_and_write(
    macro: dict,
    supply: dict,
    earnings: dict,
    technical: dict,
    dart_nlp: dict = None,
    foreign_tracker: dict = None,
    sentiment: dict = None,
    market_data: dict = None,
    report_type: str = "daily"
) -> str:
    market_data = market_data or {}
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    date_str = today.strftime("%Y년 %m월 %d일")
    vol_no = today.strftime("%j") # 일년 중 몇 번째 날

    masthead_html = generate_masthead(date_str, weekday, vol_no, "오전 개장 전 브리핑", "SMART MONEY")
    dashboard_html = generate_dashboard(market_data)
    footer_html = generate_footer(market_data)

    print("🧠 통합 판단 v3 에이전트 작동 중...")

    prompt = f"""
오늘: {date_str} {weekday}요일 (KST)

=== 글로벌 매크로 분석 ===
{json.dumps(macro, ensure_ascii=False, indent=2)}

=== 수급 분석 ===
{json.dumps(supply, ensure_ascii=False, indent=2)}

=== 실적·공시 분석 ===
{json.dumps(earnings, ensure_ascii=False, indent=2)}

=== 기술적 분석 ===
{json.dumps(technical, ensure_ascii=False, indent=2)}

=== 원본 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

위 6개 전문가 분석을 종합해서 핵심 섹션 I. II. III. IV. 를 구성하여 작성하라.
개별 종목 추천이나 단타 픽은 절대 본문에 작성하지 마시오.

div-only HTML (H1 헤드라인 및 본문 섹션들만) 출력.
"""

    text = ""
    try:
        try:
            print("🤖 [우선순위 1] Claude Sonnet 4.6으로 통합 분석서 생성 중...")
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=12000,
                system=SYNTHESIS_V3_SYSTEM,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text
            print("✅ Claude Sonnet 4.6 생성 성공")
        except Exception as claude_err:
            print(f"⚠️ Claude Sonnet 4.6 호출 실패 ({claude_err}) → Gemini 백업 시스템 작동...")
            gemini_key = os.getenv("GEMINI_API_KEY", "")
            if not gemini_key:
                raise claude_err
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            body = {
                "contents": [{"parts": [{"text": SYNTHESIS_V3_SYSTEM + "\n\n" + prompt}]}],
                "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3}
            }
            res = requests.post(url, json=body, timeout=180)
            if res.status_code == 200:
                text = res.json()["candidates"][0]["content"]["parts"][0]["text"]

        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # 멋쟁이의 시각 생성
        view_text = generate_meotjaengi_view(market_data, text[:1000])
        view_html = f"""
<div style="background:#0a0a0a;padding:20px 22px;margin:18px 0 4px">
<p style="font-size:9px;letter-spacing:0.18em;color:#f0c040;margin:0 0 10px">멋쟁이의 시각</p>
<p style="color:#e2e2e2;font-size:14px;line-height:1.95;margin:0">{view_text}</p>
</div>
"""

        img_tag = f'<img src="{UNSPLASH_IMAGE_URL}" alt="멋쟁이 인사이트 한국 주식시장 분석" style="width:100%;height:280px;object-fit:cover;border-radius:10px;display:block;margin:18px 0 8px">'

        final_html = f"""
{masthead_html}
{dashboard_html}
{img_tag}
{text}
{view_html}
{DISCLAIMER_HTML}
{footer_html}
<!-- PICKS_JSON: [] -->
</div>
"""
        print("✅ 통합 판단 v3 완료")
        return final_html
    except Exception as e:
        print(f"통합 에이전트 v3 오류: {e}")
        return f"<div><p>오류: {e}</p></div>"
