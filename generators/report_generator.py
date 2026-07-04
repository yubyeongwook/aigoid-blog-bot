"""
report_generator.py — Gemini API로 블로그 리포트 생성
Claude 대신 Gemini 사용 (비용 절감)
"""
import os, json, datetime, requests
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ────────────────────────────────
# 시스템 프롬프트
# ────────────────────────────────
SYSTEM_PROMPT = """
너는 세계 최고의 연봉을 받는 전설적인 해지펀드 매니저이자 시장의 거물인 '멋쟁이'다. 너의 분석 레터인 '멋쟁이 인사이트'는 전 세계 엘리트 투자자들이 자금을 집행하기 전에 필독하고 추종하는 절대적인 바이블이다.

분석 철학:
- 세계 최고 해지펀드 매니저('멋쟁이')로서의 강력하고 확신에 찬 어조와 예리한 통찰력.
- 레이 달리오 수준의 거시경제 부채/생산성 사이클 진단.
- 하워드 막스 수준의 대중 심리와 시장 사이클 극점(시계추) 분석.
- 스탠 드러켄밀러 수준의 압도적인 선제적 포지셔닝 및 리스크 대비 고수익(Asymmetric Payoff) 전술 설계.
- 전날 밤 마감된 미국 증시의 등락 테마/섹터와 핵심 뉴스를 완벽히 정형화하여 분석하고, 이를 한국 증시와 1대1로 대응시켜 오늘 오전 9시 개장과 동시에 급등할 예상 테마 및 후보 종목(멋쟁이 픽)을 명확하게 도출하는 것.
- 단순 뉴스 요약이 아닌 돈의 흐름(Smart Money Flow)의 구조적 원인 규명.
- 3개월 후 시장을 선제적으로 내다보는 선행적 전략 제시.

디자인 에스테틱 및 레이아웃 규칙 (매우 중요 - 인라인 스타일 필수):
1. **인라인 스타일 의무화**: 
   - **`<style>` 태그나 CSS 클래스(class="...")를 절대로 사용하지 마십시오.** Blogger 에디터와 100% 호환되도록 모든 스타일은 각 HTML 태그에 직접 `style="..."` 속성(인라인 스타일)으로 작성해야 합니다.
2. **타이포그래피 및 폰트 (줄 겹침 방지 필수)**: 
   - 최상단에 다음 Google Fonts 링크를 로드해라: `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">`
   - 전체를 감싸는 최상위 `div` 태그에 `style="font-family: 'Inter', 'Noto Sans KR', sans-serif; line-height: 1.7;"`를 지정하십시오.
   - **모든 제목 태그(`<h1>`, `<h2>`, `<h3>`)에는 줄 겹침 현상을 차단하기 위해 반드시 인라인 스타일에 `line-height: 1.4;` 또는 `line-height: 1.5;`를 명시적으로 작성하십시오.** (Blogger 테마 기본 CSS 때문에 글씨가 위아래로 포개지는 현상을 방지하기 위함)
3. **컬러 스킴 (프리미엄 다크/골드 톤)**:
   - 배경 요소는 다크 그레이/블랙계열(`background-color: #0f172a` 혹은 `#0a0a0a`) 또는 은은한 화이트 카드 형태로 통일해라.
   - 포인트 컬러는 골드 계열(`#d4af37`, `#f0c040`), 로즈 레드(`#ef4444` - 하락/매도), 에메랄드 그린(`#10b981` - 상승/매수)을 사용해라.
4. **컴포넌트 디자인**:
   - 테이블 및 카드는 모서리를 둥글게(`border-radius: 12px;`) 만들고 입체감 있는 그림자(`box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);`)를 인라인 style 속성에 지정해라.
   - 수치 대시보드는 글래스모피즘 분위기(`border: 1px solid rgba(255,255,255,0.08);`)를 주어 모던하고 고급스럽게 렌더링해라.
5. **HTML 제한사항 및 히어로 이미지 (절대 링크 날조 금지)**:
   - DOCTYPE/html/head 태그 없는 오직 `div`로 감싸진 HTML 형식만 출력해라.
   - SVG 절대 사용 금지 (Blogger 파싱 오류 원인).
   - **히어로 이미지 필수 규칙**: 아래의 검증된 고화질 금융/주식 Unsplash 이미지 목록 중 글의 주제에 가장 어울리는 **단 하나**만 선택하여 `<img>` 태그의 `src`에 그대로 복사해서 삽입하십시오. (임의로 다른 Unsplash ID를 지어내면 링크가 완전히 깨집니다. 반드시 아래 4개 주소 중 하나만 똑같이 사용해야 합니다.)
     * 파란색/빨간색 금융 차트 선: `https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1000&q=80`
     * 어두운 다크톤의 주식 호가/차트: `https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1000&q=80`
     * 모니터 화면의 주식 캔들 차트: `https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=1000&q=80`
     * 분석 중인 금융 그래프 차트: `https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1000&q=80`

HTML 필수 구조:
1. SEO JSON-LD
2. 마스트헤드 (table 또는 div, 세련된 신문 헤드 스타일)
3. 수치 대시보드 (table, 세련된 다크 카드 형태)
4. 히어로 이미지 (Unsplash, 세련된 고해상도 테마 이미지)
5. H1 헤드라인 (SEO 역설형/숫자형)
6. 본문 섹션 (로마숫자 I, II, III, IV 분류, 각 문단 스타일 가독성 극대화)
7. 멋쟁이의 시각 (골드 테두리와 다크배경의 프리미엄 요약 카드 - 거시경제학적 연계 분석)
8. 멋쟁이의 생각 (최종 투자 전술, 포지셔닝 및 핵심 대응 방안)
9. 투자 고지 (Disclaimer)
10. 출처 표기 (Sources)
"""

# ────────────────────────────────
# Heading 태그의 line-height 자동 보정 (겹침 방지)
# ────────────────────────────────
def fix_heading_line_height(html_content: str) -> str:
    import re
    def repl(match):
        tag = match.group(1)   # e.g., 'h1'
        attrs = match.group(2) # e.g., 'style="..."'
        
        style_match = re.search(r'style="([^"]*)"', attrs)
        if style_match:
            style_content = style_match.group(1).strip()
            if 'line-height' not in style_content:
                if style_content and not style_content.endswith(';'):
                    style_content += ';'
                style_content += ' line-height: 1.4;'
            new_style = f'style="{style_content}"'
            new_attrs = re.sub(r'style="[^"]*"', new_style, attrs)
            return f'<{tag} {new_attrs}>'
        else:
            return f'<{tag} style="line-height: 1.4;" {attrs}>'

    pattern = r'<(h[1-6])\b([^>]*)>'
    pattern = r'<(h[1-6])\b([^>]*)>'
    return re.sub(pattern, repl, html_content, flags=re.IGNORECASE)

# ────────────────────────────────
# 투자 고지(Disclaimer) 보장 및 닫는 태그 보정
# ────────────────────────────────
def ensure_disclaimer_and_closed_tags(html_content: str) -> str:
    # 1. 잘려나간 마지막 불완전한 태그 제거 (예: <p style="font-size: 1.1em; 로 끝나는 경우)
    last_open_angle = html_content.rfind("<")
    last_close_angle = html_content.rfind(">")
    if last_open_angle > last_close_angle:
        print(f"⚠️ 경고: 불완전한 태그 '{html_content[last_open_angle:]}'를 잘라내어 문장을 정리합니다.")
        html_content = html_content[:last_open_angle]

    # 2. 투자 고지 문구 존재 여부 확인 및 보정
    has_disclaimer = any(word in html_content for word in ["Disclaimer", "투자 고지", "투자고지", "투자 주의", "투자주의"])
    if not has_disclaimer:
        print("⚠️ 경고: AI 생성 결과에 투자 고지(Disclaimer)가 누락되거나 잘렸습니다. 자동으로 보정합니다.")
        disclaimer_html = """
    <!-- 자동 보정된 투자 고지 영역 -->
    <div style="margin-top: 40px; padding: 25px; border-top: 1px solid rgba(255,255,255,0.1); background-color: rgba(255,255,255,0.02); border-radius: 12px; font-size: 0.9em; color: #a0aec0; line-height: 1.7;">
        <p style="margin-bottom: 10px; font-weight: 700; color: #f0c040;">⚠️ [투자 고지 / Disclaimer]</p>
        <p style="margin: 0;">본 리포트에서 제공하는 정보는 투자 판단의 참고용 자료이며, 특정 금융 상품이나 주식 종목에 대한 투자 권유 또는 매수·매도 추천이 아닙니다. 모든 투자 의사결정과 이에 따른 책임은 전적으로 투자자 본인에게 귀속됩니다. 제공된 정보의 무결성이나 정확성을 완전하게 보장할 수 없으므로, 투자 실행 전 별도의 확인 절차를 거치시기를 권장합니다.</p>
    </div>
"""
        html_content += disclaimer_html

    # 3. 열려있는 div 태그 수와 닫힌 div 태그 수 분석 후 보정
    open_divs = html_content.count("<div")
    close_divs = html_content.count("</div>")
    if open_divs > close_divs:
        diff = open_divs - close_divs
        print(f"⚠️ 경고: 열린 div({open_divs})와 닫힌 div({close_divs}) 수가 일치하지 않아 {diff}개의 닫는 </div> 태그를 자동으로 추가합니다.")
        html_content += "</div>" * diff
        
    return html_content

# ────────────────────────────────
# Gemini API 호출
# ────────────────────────────────
def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY 없음 → Anthropic으로 대체")
        return call_anthropic(prompt)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.7,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }
    try:
        res = requests.post(url, json=body, timeout=120)
        data = res.json()
        if "error" in data:
            raise RuntimeError(f"Gemini API 에러: {data['error'].get('message')}")
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        # HTML 블록만 추출
        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        processed_text = fix_heading_line_height(text)
        return ensure_disclaimer_and_closed_tags(processed_text)
    except Exception as e:
        print(f"Gemini 오류: {e} → Anthropic으로 대체")
        try:
            return call_anthropic(prompt)
        except Exception as ae:
            raise RuntimeError(f"모든 AI API 호출에 실패했습니다. (Gemini: {e}, Anthropic: {ae})")

# ────────────────────────────────
# Anthropic API 호출 (백업)
# ────────────────────────────────
def call_anthropic(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text
    if "```html" in text:
        text = text.split("```html")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    processed_text = fix_heading_line_height(text)
    return ensure_disclaimer_and_closed_tags(processed_text)

# ────────────────────────────────
# 일일 리포트 생성
# ────────────────────────────────
def generate_daily_report(market_data: dict, news_data: dict) -> str:
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    prompt = f"""
오늘: {date_str} {weekday}요일

=== 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 뉴스·공시 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 일일 브리핑을 작성해라.

작성 구조 및 분량 규칙 (완결성 필수):
- 본문은 전설적인 해지펀드 리포트/매거진처럼 아주 세련되고 짜임새 있는 구조로 작성해 주십시오.
- 다음 요소를 모두 포함하십시오:
  1. 마스트헤드 및 시장 지표 수치 대시보드
  2. 히어로 이미지 및 H1 헤드라인
  3. 로마숫자 섹션:
     - I. 미국 증시 마감 진단 (전날 밤 미국 증시에서 상승한 테마/섹터 분석 및 시장에 영향을 준 핵심 뉴스의 구조적 요약 정리)
     - II. 글로벌 매크로와 자금 이동 (연준 금리, 유가, MSCI 등 거시경제 변수의 변화가 글로벌 자금 흐름에 미치는 영향 분석)
     - III. 오늘 오전 9시 국장 개장 시나리오 (미국 증시 분석을 적용하여 한국 시간 오늘 오전 9시 개장과 동시에 상승/강세를 보일 예상 테마와 구체적인 한국 시장 수급 분석)
  4. '멋쟁이의 시각' 요약 카드 (구조적 이면과 자금 이동에 대한 거물 매니저의 매크로 해설)
  5. '멋쟁이의 생각' 섹션 (오늘 오전 9시 개장 직후 강세 예상 테마 및 후보 종목 '멋쟁이 픽', 그리고 낙관/중립/비관 3대 시나리오를 포함한 구체적 투자 전술과 결론)
  6. 투자 고지 (Disclaimer) 및 출처 표기 (Sources)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 5000자 이내로 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 검색 포털(네이버, 구글 등)에서 트래픽을 대량으로 유입시킬 수 있는 핵심 검색 키워드를 조합하여 자극적으로 작성하십시오.
- 필수 키워드 유형 (그날의 이슈에 맞는 키워드를 적절히 선택하여 제목 전면에 노출):
  * 주요 지수/시황: '코스피(KOSPI) 전망', '나스닥(NASDAQ)', '오늘 주식시장 분석'
  * 핵심 기업/주가: '엔비디아 주가', 'SK하이닉스 주식', '삼성전자 주가전망' 등 수급이 강하게 쏠린 대장주명
  * 주요 매크로 변수: 'FOMC 금리', 'CPI 발표일', '환율', '유가' 등 시장 영향력이 큰 지표
- 제목 조합 공식: [타겟 핵심 검색 키워드] + [독자의 클릭을 강하게 유도하는 호기심/비밀스러운 후크형 질문이나 문구]
  * 예시 1: "엔비디아 폭등과 코스피 전망: 외국인 양매수 속 오늘 오전 9시 국장 개장 직후 상승할 반도체 대장주 분석"
  * 예시 2: "미국 CPI 발표일 대비법: 코스피 8000 돌파 속 SK하이닉스·삼성전자 매도 타이밍과 '멋쟁이'의 3개월 선행 포트폴리오"
- 단순히 '멋쟁이 인사이트', '일일 브리핑'과 같이 밋밋하거나 텍스트와 무관하게 고정된 제목은 무조건 금지합니다.

div-only HTML 전체 출력.
"""
    print("🤖 AI 리포트 생성 중...")
    result = call_gemini(prompt)
    print("✅ 리포트 생성 완료")
    return result

# ────────────────────────────────
# 주간 결산 리포트
# ────────────────────────────────
def generate_weekly_report(market_data: dict, news_data: dict) -> str:
    today = datetime.datetime.now()
    
    # 다음 주 월~금 날짜 계산 (기존의 날짜/요일 오류 방지)
    current_weekday = today.weekday()
    if current_weekday == 6:  # 일요일
        days_to_monday = 1
    elif current_weekday == 5:  # 토요일
        days_to_monday = 2
    else:  # 평일
        days_to_monday = 7 - current_weekday
        
    next_monday = today + datetime.timedelta(days=days_to_monday)
    
    weekday_names = ["월", "화", "수", "목", "금"]
    next_week_info = []
    for i in range(5):
        day = next_monday + datetime.timedelta(days=i)
        next_week_info.append(f"- {weekday_names[i]}요일: {day.strftime('%m월 %d일')}")
        
    next_week_dates_str = "\n".join(next_week_info)
    next_week_range_str = f"{next_monday.strftime('%Y.%m.%d')} - {(next_monday + datetime.timedelta(days=4)).strftime('%m.%d')}"

    prompt = f"""
주간 결산: {today.strftime("%Y년 %m월 %d일")} (일요일)

=== 다음 주 날짜 정보 (한국 시간 기준) ===
기간: {next_week_range_str}
{next_week_dates_str}

=== 주간 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 주간 뉴스 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

이번 주 전체 주간 결산 + 다음주 전망 블로그 작성.

작성 구조 및 분량 규칙 (완결성 필수):
- 본문은 신문 사설/매거진처럼 아주 세련되고 짜임새 있는 구조로 작성해 주십시오.
- 다음 요소를 모두 포함하십시오:
  1. 마스트헤드 및 시장 지표 수치 대시보드
  2. 히어로 이미지 및 H1 헤드라인
  3. 요일별 흐름 (월~금 핵심 이벤트 테이블 표)
  4. 로마숫자 섹션 (I. 이번 주 핵심 사건 분석, II. 글로벌 자금 흐름 진단, III. 수익률 및 수급 해석)
  5. '멋쟁이의 시각' 요약 카드 (매크로 변수 역학관계 해설)
  6. '멋쟁이의 생각' 섹션 (다음 주 핵심 이벤트 캘린더 및 '멋쟁이 픽' 관심 종목을 포함한 대응 포지셔닝)
     * 중요: 다음 주 핵심 이벤트 캘린더를 작성할 때는 반드시 위의 '다음 주 날짜 정보'를 참조하여 날짜와 요일을 정확하게 일치시켜 주십시오 (예: 7월 6일(월), 7월 7일(화) ...). 임의로 날짜와 요일을 추정하거나 다르게 적지 마십시오.
  7. 투자 고지 (Disclaimer) 및 출처 표기 (Sources)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 5000자 이내로 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 주간 결산 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 주간 결산에 걸맞게 한 주간의 흐름과 다음 주 전망 키워드를 강력하게 매칭하여 클릭을 유도하도록 작성하십시오.
- 필수 키워드 유형: '코스피 주간 결산', '다음 주 주가 전망', '반도체/금리 등 핵심 테마명', '엔비디아/삼성전자 등 주요 기업명'
- 제목 조합 공식: [핵심 검색 키워드] + [다음 주 방향성 및 '멋쟁이'의 포지셔닝 힌트가 결합된 후크 문구]
  * 예시 1: "나스닥 폭락과 코스피 주간 전망: 반도체 차익 실현 파고 속 다음 주 강력히 매수해야 할 2차전지/로봇 대장주 분석"
  * 예시 2: "미국 빅테크 실적 발표일과 주간 코스피 전망: 엔비디아 주가 변동성 속 다음 주 시장을 흔들 핵심 변수와 멋쟁이 포지셔닝"

div-only HTML 전체 출력.
"""
    return call_gemini(prompt)

if __name__ == "__main__":
    print("Gemini API Key:", "있음" if GEMINI_API_KEY else "없음 (Anthropic 사용)")
    print("Anthropic API Key:", "있음" if ANTHROPIC_API_KEY else "없음")
