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
너는 멋쟁이 인사이트의 수석 글로벌 매크로 애널리스트다.

분석 철학:
- 레이 달리오 수준의 거시경제 통찰
- 하워드 막스의 시장 사이클 진단
- 스탠 드러켄밀러 수준의 선제 포지셔닝
- 단순 뉴스 요약이 아닌 구조적 원인 분석
- 글로벌 자금 흐름 → 한국 시장 연결 설명
- 3개월 후 시장을 미리 보는 선행 분석

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
    return re.sub(pattern, repl, html_content, flags=re.IGNORECASE)

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
        return fix_heading_line_height(text)
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
    return fix_heading_line_height(text)

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
- 본문은 신문 사설/매거진처럼 아주 세련되고 짜임새 있는 구조로 작성해 주십시오.
- 다음 요소를 모두 포함하십시오:
  1. 마스트헤드 및 시장 지표 수치 대시보드
  2. 히어로 이미지 및 H1 헤드라인
  3. 로마숫자 섹션 (I. 글로벌 매크로 분석, II. 한국 시장 포지셔닝, III. 수급 분석과 섹터 방향)
  4. '멋쟁이의 시각' 요약 카드 (구조적 이면과 자금 이동에 대한 매크로 해설)
  5. '멋쟁이의 생각' 섹션 (낙관/중립/비관 3대 시나리오 및 '멋쟁이 픽' 관심 종목을 포함한 구체적 투자 전술과 결론)
  6. 투자 고지 (Disclaimer) 및 출처 표기 (Sources)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 5000자 이내로 완결 지어 주십시오.

SEO 제목 패턴 (역설형):
"코스피가 오르는 날 내 계좌가 빠지는 이유"
"외국인이 X조를 판 날 코스피는 왜 올랐나"

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
    prompt = f"""
주간 결산: {today.strftime("%Y년 %m월 %d일")} (일요일)

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
  7. 투자 고지 (Disclaimer) 및 출처 표기 (Sources)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 5000자 이내로 완결 지어 주십시오.

div-only HTML 전체 출력.
"""
    return call_gemini(prompt)

if __name__ == "__main__":
    print("Gemini API Key:", "있음" if GEMINI_API_KEY else "없음 (Anthropic 사용)")
    print("Anthropic API Key:", "있음" if ANTHROPIC_API_KEY else "없음")
