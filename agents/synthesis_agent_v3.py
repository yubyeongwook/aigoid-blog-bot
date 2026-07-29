"""
synthesis_agent_v3.py — 통합 판단 에이전트 v3
6개 전문가 분석 통합
모바일 친화적 · 검정 배경 대시보드 · 역설형 SEO 제목
"""
import os, json, datetime, re, requests

from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

UNSPLASH_IMAGE_URL = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=900&auto=format&fit=crop&q=80"

def generate_seo_title(market_summary: str) -> str:
    prompt = f"""
오늘 한국 주식 블로그 제목 1개 만들어줘.

오늘 시장 요약:
{market_summary}

규칙:
- 역설형 제목: "A가 B인데 C다 — D"
- 느낌표 금지
- 50자 이내
- 한국어만
- SEO 키워드 포함 (코스피·반도체·외국인·상한가 등)

예시:
"엔비디아가 -5% 빠졌는데 SK하이닉스 64조가 답을 준다 — 오늘 수익성 세계 1위 확인"
"외국인이 2조를 팔았는데 코스피가 올랐다 — AI 쇼티지가 만든 역설"

제목 1개만 출력. 다른 말 금지.
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.content[0].text.strip()
    except Exception as e:
        print(f"SEO 제목 생성 오류: {e}")
        today = datetime.datetime.now()
        weekday = ["월","화","수","목","금","토","일"][today.weekday()]
        return f"{today.strftime('%m월 %d일')} {weekday}요일 코스피 분석 — 시장 주요 변수 통합 정리"

def generate_dashboard_html(market_data: dict) -> str:
    def color(val):
        if val is None: return "#f0c040"
        return "#4ade80" if float(str(val).replace('%','').replace('+','')) >= 0 else "#ef4444"

    nasdaq_pct = market_data.get('nasdaq_pct', '0%')
    nasdaq_val = market_data.get('nasdaq_val', '-')
    sp500_pct  = market_data.get('sp500_pct', '0%')
    sp500_val  = market_data.get('sp500_val', '-')
    soxx_pct   = market_data.get('soxx_pct', '0%')
    soxx_val   = market_data.get('soxx_val', '-')
    usdkrw     = market_data.get('usdkrw', '-')
    kospi_pct  = market_data.get('kospi_pct', '0%')
    kospi_val  = market_data.get('kospi_val', '-')
    wti        = market_data.get('wti', '-')
    vix        = market_data.get('vix', '-')
    foreign    = market_data.get('foreign_flow', '-')

    return f"""
<table width="100%" cellpadding="0" cellspacing="1"
style="border-collapse:separate;border-spacing:1px;background:#111;margin:0 0 1px">
<tr>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">나스닥</p>
    <p style="font-size:14px;font-weight:700;color:{color(nasdaq_pct)};margin:0 0 1px;font-family:Georgia,serif">{nasdaq_pct}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{nasdaq_val}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">S&P500</p>
    <p style="font-size:14px;font-weight:700;color:{color(sp500_pct)};margin:0 0 1px;font-family:Georgia,serif">{sp500_pct}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{sp500_val}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">필라델피아반도체</p>
    <p style="font-size:14px;font-weight:700;color:{color(soxx_pct)};margin:0 0 1px;font-family:Georgia,serif">{soxx_pct}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{soxx_val}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">원달러 환율</p>
    <p style="font-size:14px;font-weight:700;color:#f0c040;margin:0 0 1px;font-family:Georgia,serif">{usdkrw}</p>
    <p style="font-size:10px;color:#aaa;margin:0">원</p>
  </td>
</tr>
</table>
<table width="100%" cellpadding="0" cellspacing="1"
style="border-collapse:separate;border-spacing:1px;background:#111;margin:0 0 0">
<tr>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">코스피</p>
    <p style="font-size:12px;font-weight:700;color:{color(kospi_pct)};margin:0 0 1px">{kospi_pct}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{kospi_val}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">WTI 유가</p>
    <p style="font-size:12px;font-weight:700;color:#f0c040;margin:0 0 1px">{wti}</p>
    <p style="font-size:10px;color:#aaa;margin:0">달러</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">VIX 공포지수</p>
    <p style="font-size:12px;font-weight:700;color:#f0c040;margin:0 0 1px">{vix}</p>
    <p style="font-size:10px;color:#aaa;margin:0"></p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">외국인 수급</p>
    <p style="font-size:12px;font-weight:700;color:#f0c040;margin:0 0 1px">{foreign}</p>
    <p style="font-size:10px;color:#aaa;margin:0">억원</p>
  </td>
</tr>
</table>
"""

SYNTHESIS_V3_SYSTEM = """
당신은 멋쟁이 인사이트의 수석이사(Chief Managing Director)이자 최고투자전략책임자입니다.
6개 분야 수석 분석가(매크로·수급·실적·기술적·공시NLP·감성)의 분석 보고서를 정교하게 종합하여,
세계 최강 헤지펀드의 전략 보고서 수준으로 시장의 이면을 꿰뚫는 고품격 블로그 포스트를 작성합니다.

★ 월요일 오전 특별 지침:
- 한국 시간 기준 월요일 오전의 경우, 밤사이(일요일 밤) 미국 정규장이 열리지 않았으므로 전주 금요일 마감 종가 및 주말 동안의 주요 경제 이슈를 기준으로 한국 시장 개장 대비용 브리핑을 작성하십시오.

★ 주말(토요일·일요일) 발행 특별 지침 (매우 중요):
- 주말(토요일/일요일)에는 한국 주식 시장이 열리지 않으므로, 본문 섹션 제목 및 내용에서 "오늘 개장 영향" 또는 "오늘 장중 대응"이라는 표현을 절대 사용하지 마십시오.
- 대신 다음 섹션 구조를 적용하고, '오늘'이 아닌 '차주 월요일 개장 및 다음 주 시장 흐름'을 기준으로 서술하십시오:
  - II. 차주 월요일 한국 시장 개장 영향 (KOSPI/KOSDAQ 갭상승·갭하락 시나리오)
  - III. 주말 및 차주 대응 프로토콜 (다음 주 월요일 집중 추적 포인트 및 VIX 대비 전략)

★ 전일 한국장 연계 지침 (연결성 극대화):
- 전일 오후 마감 브리핑(`prev_afternoon_report`) 내용을 확인하고, 전날 오후 한국 시장의 수급 변화, 특징적 급등 테마/섹터 정보를 활용하십시오.
- 밤사이 미국 마켓의 핵심 섹터 등락 요인(예: 미국 반도체 하락, AI 전력 인프라 급등 등)이 전날 한국장에서 주도적이었던 테마들과 어떻게 충돌하거나 탄력을 주며 연결되는지 인과관계를 매끄럽고 설득력 있게 서술하여 분석의 영속성을 부여하십시오.

═══════════════════════════════
절대 금지 및 팩트 준수 규칙 (위반 시 즉시 반려)
═══════════════════════════════
1. **수치 및 지수 왜곡 절대 금지 (가장 중요)**:
   - 제공된 원본 데이터(`market_data`) 및 각 분석기에서 제공된 코스피(KOSPI), 코스닥(KOSDAQ) 지수 및 개별 종목의 종가, 등락률 수치를 **반드시 소수점까지 한 글자도 틀리지 않고 그대로 적용**하십시오.
   - 특히 **삼성전자(005930)와 SK하이닉스(000660)** 등 주요 종목들의 주가와 등락률을 서로 혼동하거나 뒤바꾸어 서술하지 마십시오.
   - 팩트에 기반한 정교하고 신뢰성 높은 서술만 허용됩니다.

2. 느낌표(!) 사용 절대 금지 · 급등예상 등의 자극적인 선동 표현 금지
3. JSON-LD 및 SVG 태그 본문 내 삽입 금지
4. 출처가 불분명한 모호한 수치 인용 금지
5. 투자 유인 및 특정 종목에 대한 확정적 추천 표현 금지

═══════════════════════════════
모바일 친화적 디자인 및 레이아웃 (최우선)
═══════════════════════════════
1. 흰색 배경 중심의 미니멀리즘 디자인
2. 복잡한 표(table) 지양 — 오직 상단의 '수치 대시보드' 1개에만 표 형식을 허용하고, 나머지는 깔끔한 카드형 div 활용
3. ★ 개별 종목 매수 추천(단타/스윙 픽 카드 등)은 절대 작성하지 마십시오. (매우 중요)
4. 대문자 로마숫자(I. II. III. IV. V.)를 사용한 논리적이고 정교한 섹션 분류 (한국어 제목 필수)
5. 본문 가독성을 높이기 위해 문단 스타일 지정: line-height: 1.95, font-size: 14.5px, color: #334155, letter-spacing: -0.015em 적용

═══════════════════════════════
HTML 최종 작성 구조 및 순서 (오전 7시 개장 전 브리핑 맞춤형)
═══════════════════════════════
1. 마스트헤드 (VOL / 날짜 / 브리핑 종류 등 정보가 정리된 흰색 배경 table)
2. 수치 대시보드 (검정색 배경의 핵심 지표 대시보드)
3. 히어로 이미지 (Unsplash 이미지 태그)
4. H1 역설형/수치형 헤드라인
5. I. 글로벌 마감 바이트 (미국 시장 요약)
6. II. 오늘 한국 시장 개장 영향
7. III. 오늘 장중 대응 프로토콜
8. IV. 3대 조건부 시나리오
9. 멋쟁이의 시각
10. 투자 고지 (Disclaimer)
11. 출처 표기
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
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    date_str = today.strftime("%Y년 %m월 %d일")

    dashboard_html = generate_dashboard_html(market_data or {})

    print("🧠 통합 판단 v3 에이전트 작동 중...")

    prompt = f"""
오늘: {date_str} {weekday}요일 (KST)

=== 전일 한국 시장 마감 브리핑 요약 ===
{json.dumps(market_data.get("prev_afternoon_report", {}) if market_data else {}, ensure_ascii=False, indent=2)}

=== 글로벌 매크로 분석 ===
{json.dumps(macro, ensure_ascii=False, indent=2)}

=== 수급 분석 ===
{json.dumps(supply, ensure_ascii=False, indent=2)}

=== 실적·공시 분석 ===
{json.dumps(earnings, ensure_ascii=False, indent=2)}

=== 기술적 분석 ===
{json.dumps(technical, ensure_ascii=False, indent=2)}

=== 공시 NLP 분석 ===
{json.dumps(dart_nlp or {}, ensure_ascii=False, indent=2)}

=== 외국인 종목별 추적 ===
{json.dumps(foreign_tracker or {}, ensure_ascii=False, indent=2)}

=== 시장 감성 지수 ===
{json.dumps(sentiment or {}, ensure_ascii=False, indent=2)}

=== 원본 시장 데이터 ===
{json.dumps(market_data or {}, ensure_ascii=False, indent=2)}

위 6개 전문가 분석을 종합해서 블로그를 작성하라.

=== 수치 대시보드 HTML (마스트헤드 직후에 그대로 삽입) ===
{dashboard_html}

=== 히어로 이미지 (수치 대시보드 바로 아래 반드시 사용) ===
<img src="{UNSPLASH_IMAGE_URL}"
alt="멋쟁이 인사이트 한국 주식시장 분석"
style="width:100%;height:280px;object-fit:cover;border-radius:10px;display:block;margin:18px 0 8px">

반드시 지킬 것:
1. ★ 개별 종목 추천 및 단타 픽은 절대 본문에 포함하지 마십시오.
2. 미국 시장 마감 뉴스 및 주요 이슈를 바탕으로 정성적/거시적 관점에서 분석하십시오.

div-only HTML 전체 출력.

★★★ 필수: 개별 추천 종목이 없으므로 HTML 맨 마지막 줄에 항상 아래 형식의 JSON 주석만 한 줄 그대로 추가하십시오:
<!-- PICKS_JSON: [] -->
"""

    text = ""
    try:
        try:
            print("🤖 [우선순위 1] Claude Sonnet 4.6으로 통합 분석서 생성 중...")
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=16000,
                system=SYNTHESIS_V3_SYSTEM,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text
            print("✅ Claude Sonnet 4.6 생성 성공")
        except Exception as claude_err:
            print(f"⚠️ Claude Sonnet 4.6 호출 실패 ({claude_err}) → Gemini 백업 시스템 작동...")
            
            gemini_key = os.getenv("GEMINI_API_KEY", "")
            if not gemini_key:
                print("❌ GEMINI_API_KEY가 없습니다. 폴백 불가.")
                raise claude_err
                
            backup_models = ["gemini-2.5-pro", "gemini-2.5-flash"]
            gemini_success = False
            
            for model in backup_models:
                print(f"🤖 Gemini 백업 호출 시도 중: {model}...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                body = {
                    "contents": [{"parts": [{"text": SYNTHESIS_V3_SYSTEM + "\n\n" + prompt}]}],
                    "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3}
                }
                try:
                    res = requests.post(url, json=body, timeout=180)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            content = candidates[0].get("content", {})
                            parts = content.get("parts", [])
                            if parts:
                                text = parts[0].get("text", "")
                                if text:
                                    print(f"✅ Gemini 백업 생성 완료 ({model})")
                                    gemini_success = True
                                    break
                    print(f"❌ Gemini {model} 응답 실패: HTTP {res.status_code} — {res.text[:150]}")
                except Exception as gem_err:
                    print(f"❌ Gemini {model} 연결 예외 발생: {gem_err}")
                    
            if not gemini_success:
                print("❌ 모든 백업 AI 호출이 실패했습니다.")
                raise claude_err

        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        text = text.replace("{{PERFORMANCE_HTML}}", "")

        # Unsplash 이미지 태그 보정
        img_tag = (
            f'<img src="{UNSPLASH_IMAGE_URL}" '
            f'alt="멋쟁이 인사이트 한국 주식시장 분석" '
            f'style="width:100%;height:280px;object-fit:cover;border-radius:10px;display:block;margin:18px 0 8px">'
        )

        from bs4 import BeautifulSoup as _BS
        soup = _BS(text, "html.parser")
        all_imgs = soup.find_all("img")
        if all_imgs:
            for img in all_imgs:
                img["src"] = UNSPLASH_IMAGE_URL
                img["alt"] = "멋쟁이 인사이트 한국 주식시장 분석"
                img["style"] = "width:100%;height:280px;object-fit:cover;border-radius:10px;display:block;margin:18px 0 8px"
            text = str(soup)
        else:
            if "<h1" in text:
                text = text.replace("<h1", img_tag + "\n<h1", 1)
            elif "</h1>" in text:
                text = text.replace("</h1>", "</h1>\n" + img_tag, 1)

        print("✅ 통합 판단 v3 완료")
        return text
    except Exception as e:
        print(f"통합 에이전트 v3 오류: {e}")
        return f"<div><p>오류: {e}</p></div>"


