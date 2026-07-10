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
당신은 멋쟁이 인사이트(aigoid.blogspot.com)의
수석 글로벌 매크로 애널리스트입니다.
멋쟁이 캐피탈 브랜드의 신뢰도를 지키는 것이 최우선입니다.

═══════════════════════════════
분석 철학
═══════════════════════════════

레이 달리오·하워드 막스·스탠 드러켄밀러를 인용할 때는
반드시 오늘 실제 수치와 직접 연결해서 설명한다.

나쁜 예:
"레이 달리오는 분산투자를 강조했습니다."

좋은 예:
"레이 달리오는 '빚을 통한 투자의 위험은
수익을 극대화하는 동시에 손실도 극대화한다'고 했다.
오늘 KODEX 레버리지 거래대금이 1조 2,000억원이다.
이 레버리지가 오늘 사이드카 발동을 만들었다."

분석은 반드시 5단계 구조를 따른다:
1단계: 팩트 (수치+출처)
2단계: 이게 왜 중요한가
3단계: 시장이 왜 그렇게 반응했는가
4단계: 반대 시나리오는 무엇인가
5단계: 그렇다면 지금 무엇을 해야 하는가

반드시 반직관적 사실 하나를 포함한다.
독자가 "이건 몰랐다"고 느끼는 데이터여야 한다.

예시:
"나스닥 사상 최고치인데 SK하이닉스만 -14.57% 폭락했다"
"89.4조 역대 최대 실적인데 주가는 -8%였다"
"외국인이 8.3조를 팔 때 개인이 혼자 8.1조를 받아냈다"

═══════════════════════════════
절대 금지 표현 — 하나라도 있으면 전면 재작성
═══════════════════════════════

금지 1 — 느낌표·과장 표현
✗ "~선 예상!" (느낌표 절대 금지)
✗ "급등 임박"
✗ "돌파 임박"
✗ "수급 폭발"
✗ "초강세"
✗ "폭발적 상승"
✗ "주도주 포착"

금지 2 — 투자 유인 표현
✗ "오늘 유력 급등 테마"
✗ "지금이 매수 타이밍"
✗ "이 종목을 주목하라"
✗ "오전 9시 진입"
✗ "놓치면 후회"
✗ "세력 매집 포착"
✗ "80% 지배 세력"

금지 3 — 확신형 예측
✗ "반드시 오른다"
✗ "~% 상승 예상" (구체적 수익률 예측 금지)
✗ "승리할 것이다"
✗ "이미 포지션을 구축했다"

금지 4 — 출처 없는 수치
✗ 출처 없는 수치 사용
✗ 추정치를 확정치처럼 표현
✗ "~로 알려졌다" 식의 모호한 근거

금지 5 — 섹션 제목에 투자 유인
✗ "오늘 유망 종목"
✗ "급등 예상 테마"
✗ "놓치면 안 되는 종목"

올바른 섹션 제목 예시:
✓ "I · 오늘 수급 분석 — 외국인이 돌아왔는가"
✓ "II · 반도체 피크아웃인가 노이즈인가"
✓ "III · 멋쟁이 픽 — 팩트 기반 관심 종목"

═══════════════════════════════
반드시 지켜야 할 표현 원칙
═══════════════════════════════

원칙 1 — 수치는 반드시 출처 명시
✓ "코스피 7,530.25 (7/10 동시호가 KIS API)"
✓ "SK하이닉스 -14.57% (7/9 종가 KRX)"
✗ "코스피 약 7500선"

원칙 2 — 예측은 반드시 조건부
✓ "외국인이 순매수 전환 시 코스피 7,600선 회복 가능"
✓ "CPI가 낮게 나오면 원달러 하락 → 외국인 복귀 기대"
✗ "코스피 7,600선 예상!"

원칙 3 — 3개 시나리오는 반드시 조건 포함
✓ 낙관: "빅테크 AI 투자 가이던스 상향 시 → 반도체 반등"
✓ 중립: "CPI 예상 수준 시 → 현 수준 유지"
✓ 비관: "이란 재점화 + 유가 90달러 복귀 시 → 추가 하락"
✗ "낙관: 7600 / 중립: 7500 / 비관: 7400" (숫자만 나열 금지)

원칙 4 — 종목 픽은 반드시 근거 + 리스크 동시 표기
✓ 근거: "HBM 점유율 58%·ADR 나스닥 상장 (공시 확인)"
✓ 리스크: "⚠️ 엔비디아 GPU 수요 둔화 시 HBM 수요 감소"
✗ 근거만 있고 리스크 없는 픽 절대 금지

원칙 5 — 투자 고지 필수
모든 글 마지막에 반드시 포함:
"본 글은 투자 정보 제공 목적이며
특정 종목의 매수·매도를 권유하지 않습니다.
모든 투자의 최종 판단과 책임은
전적으로 투자자 본인에게 있습니다."

═══════════════════════════════
HTML 구조 — 반드시 이 순서대로
═══════════════════════════════

Blogger div-only HTML (DOCTYPE·html·head 없음)
JSON-LD script 태그 절대 사용 금지 (Blogger에서 본문 노출됨)

1. 마스트헤드 (table 태그)
   - 왼쪽: VOL·날짜·브리핑 종류
   - 가운데: 멋쟁이 인사이트 (Playfair Display체 느낌)
   - 오른쪽: KST 날짜·요일·분석 종류

2. 에디션바 (검정 배경 #0a0a0a)
   - 좌: 오늘 핵심 키워드
   - 우: 가장 중요한 수치 (골드 #f0c040)

3. 수치 대시보드 (table·검정 배경 2행 4칸)
   - 상승: #4ade80
   - 하락: #ef4444
   - 주목: #f0c040
   - 각 셀: 라벨·수치·설명

4. 출처 한 줄 (font-size 11px·회색)

5. 히어로 이미지
   - Unsplash URL만 사용
   - SVG 절대 금지
   - 형식: https://images.unsplash.com/photo-XXXXX?w=900&auto=format&fit=crop&q=80

6. H1 헤드라인 (SEO 최적화)
   - 역설형: "~인데 왜 ~인가"
   - 숫자형: "X조가 팔린 날"
   - 느낌표 절대 금지

7. 본문 섹션 (로마숫자 I·II·III·IV·V)
   - 각 섹션 font-size 14px
   - 줄간격 1.95
   - 5단계 분석 구조 적용

8. 멋쟁이의 시각 박스
   - 배경: #0a0a0a
   - 제목: 골드 #f0c040·9px·letter-spacing 0.18em
   - 본문: #e2e2e2·14px

9. 멋쟁이 픽 (A·B·C 그룹)
   - 각 종목: 근거 + ⚠️ 리스크 동시 표기

10. 투자 고지 (빨간 테두리 table)

11. 출처 표기 푸터 (배경 #f5f4f0)

═══════════════════════════════
날짜·요일 처리 원칙 (필수)
═══════════════════════════════

날짜와 요일은 반드시 KST(한국표준시) 기준으로 표기한다.
발행 전 반드시 달력으로 요일을 확인한다.

2026년 7월 달력:
07/06 월 / 07/07 화 / 07/08 수 / 07/09 목 / 07/10 금
07/13 월 / 07/14 화 / 07/15 수 / 07/16 목 / 07/17 금
07/20 월 / 07/21 화 / 07/22 수 / 07/23 목 / 07/24 금
07/27 월 / 07/28 화 / 07/29 수 / 07/30 목 / 07/31 금

오전 7시 발행 = 당일 KST 날짜
오후 4시 발행 = 당일 KST 날짜

═══════════════════════════════
SEO 제목 패턴
═══════════════════════════════

역설형 (클릭률 최고):
"코스피가 오르는 날 내 계좌가 빠지는 이유"
"89.4조 역대 최대 실적인데 주가는 -8%인 이유"

숫자형 (검색 노출 최고):
"외국인이 8.3조를 판 날 코스피가 -5.81%인 이유"
"SK하이닉스 -14.57% — Meta가 HBM을 안 쓴다는 오해의 구조"

조건형:
"PCE가 3%대로 내려오면 코스피는 어디까지 가는가"

느낌표 절대 사용 금지.

═══════════════════════════════
품질 자가 체크 — 발행 전 12개 확인
═══════════════════════════════

□ 1. 모든 수치에 출처가 있는가
□ 2. 느낌표가 하나도 없는가
□ 3. 금지 표현이 없는가
□ 4. 투자 고지가 포함됐는가
□ 5. JSON-LD script 태그가 없는가
□ 6. 마스트헤드가 있는가
□ 7. 수치 대시보드가 있는가
□ 8. Unsplash 이미지인가 (SVG 금지)
□ 9. 멋쟁이의 시각 박스가 있는가
□ 10. 출처 표기 푸터가 있는가
□ 11. 종목 픽에 근거 AND 리스크 둘 다 있는가
□ 12. 날짜·요일이 KST 기준으로 맞는가

12개 중 하나라도 없으면 재작성한다.
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
# 마크다운 ** 및 이모지/특수 기호 제거
# ────────────────────────────────
def clean_html_content(html_content: str) -> str:
    import re
    # 1. 마크다운 별표(**) 제거
    html_content = html_content.replace("**", "")
    
    # 2. 이모지 및 특수 데코용 기호 제거 (정규식 활용)
    emoji_pattern = re.compile(
        '['
        '\U0001F600-\U0001F64F'  # emoticons
        '\U0001F300-\U0001F5FF'  # symbols & pictographs
        '\U0001F680-\U0001F6FF'  # transport & map symbols
        '\U0001F1E0-\U0001F1FF'  # flags
        '\U0001F900-\U0001F9FF'  # supplemental symbols
        '\u2600-\u26FF'          # misc symbols
        '\u2700-\u27BF'          # dingbats
        '\ufe0f'                 # variation selector
        ']+', flags=re.UNICODE
    )
    html_content = emoji_pattern.sub('', html_content)
    
    # 혹시 남을 수 있는 대표적인 데코용 특수문자 개별 소거
    for char in ["📊", "🤖", "⚠️", "✅", "✔", "📈", "📉", "🔥", "💡", "📢", "🔍", "⚡", "⭐", "☑", "✨"]:
        html_content = html_content.replace(char, "")

    # 3. 절대 금지 표현 방어적 교체 (이중 레이어 방어막)
    forbidden_replacements = {
        "급등 예상": "상승 흐름 전망",
        "지금이 매수 타이밍": "관심 구간 진입 판단",
        "오전 9시 진입하라": "개장 후 흐름 모니터링",
        "방아쇠를 당겨라": "리스크를 검토하라",
        "놓치면 후회한다": "유의 깊게 관찰해야 한다",
        "이 종목을 주목하라": "이 종목의 공시 분석",
        "수익을 챙겨라": "수익 관리에 유의하라",
        "반드시 오른다": "상승 가능성이 높다",
        "승리할 것이다": "안정적인 흐름이 기대된다",
        "이미 포지션을 구축했다": "포지션 전략을 검토했다",
        "압도적 수익 추구": "포트폴리오 수익 극대화",
        "비대칭 포지셔닝": "비대칭 포지션 검토",
        "멋쟁이만 아는": "멋쟁이 분석의",
        "독점 분석": "심층 분석",
        "지금 바로 확인": "참조 가능",
    }
    for old, new in forbidden_replacements.items():
        html_content = html_content.replace(old, new)
        
    return html_content

# ────────────────────────────────
# 투자 고지(Disclaimer) 보장 및 닫는 태그 보정
# ────────────────────────────────
# ────────────────────────────────
# HTML 클래스를 인라인 스타일로 변환 (토큰 절약 및 호환성 보장)
# ────────────────────────────────
def inline_css_styles(html_content: str) -> str:
    styles_map = {
        "mi-container": "max-width: 720px; margin: 0 auto; font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif; background: #0a0a0a; color: #f0f0f0; line-height: 1.95; padding: 24px 16px;",
        "mi-section-header": "font-family: 'Space Mono', monospace; font-size: 10px; letter-spacing: 0.2em; color: #888; border-bottom: 1.5px solid #f0c040; padding-bottom: 6px; margin: 30px 0 14px; font-weight: bold;",
        "mi-paragraph": "font-size: 14px; color: #f0f0f0; line-height: 1.95; margin: 0 0 14px; text-align: justify; word-break: keep-all;",
        
        "mi-card-positive": "border-left: 3px solid #4ade80; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-positive-title": "font-size: 13px; font-weight: 700; color: #4ade80; margin: 0 0 4px;",
        
        "mi-card-negative": "border-left: 3px solid #ef4444; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-negative-title": "font-size: 13px; font-weight: 700; color: #ef4444; margin: 0 0 4px;",
        
        "mi-card-neutral": "border-left: 3px solid #888; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-neutral-title": "font-size: 13px; font-weight: 700; color: #aaa; margin: 0 0 4px;",
        
        "mi-card-blue": "border-left: 3px solid #1a3a6b; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-blue-title": "font-size: 13px; font-weight: 700; color: #f0c040; margin: 0 0 4px;",
        
        "mi-card-content": "font-size: 13px; color: #f0f0f0; line-height: 1.85; margin: 0;",
        
        "mi-dark-box": "background: #000; border: 1px solid #222; padding: 16px 18px; margin: 16px 0 4px;",
        "mi-dark-box-title": "font-family: 'Space Mono', monospace; font-size: 9px; letter-spacing: 0.18em; color: #f0c040; margin: 0 0 8px; font-weight: bold;",
        "mi-dark-box-content": "color: #f0f0f0; font-size: 14px; line-height: 1.95; margin: 0;",
        
        "mi-group-container": "border: 1px solid #222; background: #111; margin: 0 0 10px; border-radius: 4px; overflow: hidden;",
        "mi-group-header-a": "background: #1a3a6b; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-b": "background: #333; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-c": "background: #ef4444; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-title": "font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700; color: #fff; margin: 0;",
        "mi-group-header-stars": "font-size: 11px; color: #f0c040; margin: 0;",
        "mi-group-content": "padding: 12px 16px; color: #f0f0f0;",
        
        "mi-headline-container": "padding: 0 0 18px; border-bottom: 2px solid #f0c040;",
        "mi-headline-meta": "font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 0.15em; color: #f0c040; margin: 0 0 8px; font-weight: bold;",
        "mi-headline-title": "font-family: 'Playfair Display', Georgia, serif; font-size: 26px; font-weight: 900; line-height: 1.15; color: #f0f0f0; margin: 0 0 12px; letter-spacing: -0.02em;",
        "mi-headline-lead": "font-size: 14px; color: #aaa; line-height: 1.85; margin: 0; border-left: 4px solid #f0c040; padding-left: 14px;",
        
        "mi-disclaimer-table": "border-collapse: collapse; border: 2px solid #ef4444; margin: 24px 0 0; width: 100%;",
        "mi-disclaimer-header": "background: #ef4444; padding: 10px 16px;",
        "mi-disclaimer-content": "background: #111; padding: 12px 16px; text-align: left;"
    }
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. 일반 클래스 인라인 처리
    for class_name, style_str in styles_map.items():
        elements = soup.find_all(class_=class_name)
        for el in elements:
            existing_style = el.get("style", "")
            if existing_style:
                el["style"] = style_str + " " + existing_style
            else:
                el["style"] = style_str
                
    # 1.5. 브랜드 아이덴티티(CI) 글꼴 및 레이아웃 강제 동기화 (Playfair Display 900 / Space Mono / Noto Sans KR)
    # 테이블 탐색
    tables = soup.find_all("table")
    if tables:
        # 첫 번째 테이블: 마스트헤드 (table 태그)
        masthead = tables[0]
        # 혹시 클래스명이나 식별 정보가 없을 경우를 대비하여 td 갯수로 매칭
        m_cells = masthead.find_all("td")
        if len(m_cells) == 3:
            m_cells[0]["style"] = "width: 30%; text-align: left; font-family: 'Space Mono', monospace; font-size: 9px; color: #888; line-height: 1.7;"
            m_cells[1]["style"] = "width: 40%; text-align: center; font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 900; color: #f0f0f0; line-height: 1.2;"
            m_cells[2]["style"] = "width: 30%; text-align: right; font-family: 'Space Mono', monospace; font-size: 9px; color: #888; line-height: 1.7;"
            
        # 두 번째 테이블: 수치 대시보드
        if len(tables) >= 2:
            dashboard = tables[1]
            if "mi-disclaimer-table" not in dashboard.get("class", []):
                dashboard["style"] = "width: 100%; border-collapse: collapse; background-color: #0a0a0a; color: #f0f0f0; margin-bottom: 20px; border: 1px solid #222;"
                d_cells = dashboard.find_all("td")
                for cell in d_cells:
                    cell["style"] = "width: 25%; text-align: center; border: 1px solid #222; padding: 10px 8px; background-color: #111;"
                    p_tags = cell.find_all("p")
                    for idx, p in enumerate(p_tags):
                        p_existing = p.get("style", "")
                        if idx == 0:
                            # 라벨 (Space Mono)
                            p["style"] = "font-family: 'Space Mono', monospace; font-size: 9px; color: #888; margin: 0 0 4px; line-height: 1.2; " + p_existing
                        elif idx == 1:
                            # 수치 데이터 (Space Mono)
                            p["style"] = "font-family: 'Space Mono', monospace; font-size: 16px; font-weight: bold; margin: 0 0 4px; line-height: 1.2; " + p_existing
                        elif idx == 2:
                            # 설명 (Noto Sans KR)
                            p["style"] = "font-family: 'Noto Sans KR', sans-serif; font-size: 9px; color: #555; margin: 0; line-height: 1.3; " + p_existing

        # 기타 수치 비교 데이터 테이블 (두 번째 테이블 이후, disclaimer 제외)
        for tbl in tables[2:]:
            if "mi-disclaimer-table" in tbl.get("class", []):
                continue
            tbl["style"] = "width: 100%; border-collapse: collapse; margin-bottom: 15px; border: 1px solid #222; background-color: #0a0a0a;"
            for tr in tbl.find_all("tr"):
                for th in tr.find_all("th"):
                    th["style"] = "background: #000; color: #f0c040; font-family: 'Space Mono', monospace; font-size: 11px; font-weight: bold; padding: 8px; border: 1px solid #222; text-align: center;"
                for td in tr.find_all("td"):
                    td["style"] = "padding: 8px; border: 1px solid #222; font-family: 'Noto Sans KR', sans-serif; font-size: 12px; color: #f0f0f0; background: #111; text-align: center;"
                    # 숫자/퍼센트/날짜 등이 포함되어 있으면 글꼴을 Space Mono로 강제 지정
                    td_text = td.get_text().strip()
                    if any(char.isdigit() for char in td_text) or "%" in td_text or "/" in td_text or "-" in td_text:
                        td["style"] += " font-family: 'Space Mono', monospace;"

    # 에디션바 검색 및 Space Mono 폰트 지정
    divs = soup.find_all("div")
    for d in divs:
        d_text = d.get_text()
        if "핵심 키워드" in d_text or "키워드" in d_text:
            existing = d.get("style", "")
            d["style"] = "background-color: #0a0a0a; color: #f0f0f0; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; font-family: 'Space Mono', monospace; font-size: 10px; " + existing
            for span in d.find_all("span"):
                span_style = "font-family: 'Space Mono', monospace;"
                span_existing = span.get("style", "")
                if span_existing:
                    span["style"] = span_style + " " + span_existing
                else:
                    span["style"] = span_style

    # 헤드라인 H1 강제 Playfair Display 900 지정
    h1_tags = soup.find_all("h1")
    for h1 in h1_tags:
        h1_style = "font-family: 'Playfair Display', serif; font-weight: 900; line-height: 1.2; color: #f0f0f0;"
        existing = h1.get("style", "")
        if existing:
            h1["style"] = h1_style + " " + existing
        else:
            h1["style"] = h1_style

                
    # 2. 멋쟁이 픽 그룹 내용물의 p 태그들 인라인 처리
    group_contents = soup.find_all(class_="mi-group-content")
    for gc in group_contents:
        p_tags = gc.find_all("p")
        for i, p in enumerate(p_tags):
            p_style = "font-size: 13.5px; color: #f0f0f0; line-height: 1.85;"
            if i < len(p_tags) - 1:
                p_style += " margin: 0 0 8px;"
            else:
                p_style += " margin: 0;"
            
            existing = p.get("style", "")
            if existing:
                p["style"] = p_style + " " + existing
            else:
                p["style"] = p_style

    # 3. 투자 고지 안쪽 내용 처리
    disclaimer_content_td = soup.find(class_="mi-disclaimer-content")
    if disclaimer_content_td:
        p_tags = disclaimer_content_td.find_all("p")
        for i, p in enumerate(p_tags):
            p_style = "font-size: 12.5px; color: #f0f0f0; line-height: 1.8; font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;"
            if i < len(p_tags) - 1:
                p_style += " margin: 0 0 8px;"
            else:
                p_style += " margin: 0;"
            
            existing = p.get("style", "")
            if existing:
                p["style"] = p_style + " " + existing
            else:
                p["style"] = p_style
                
    disclaimer_header_td = soup.find(class_="mi-disclaimer-header")
    if disclaimer_header_td:
        p_tag = disclaimer_header_td.find("p")
        if p_tag:
            p_style = "font-size: 11px; font-weight: 700; color: #fff; margin: 0; font-family: 'Space Mono', monospace;"
            existing = p_tag.get("style", "")
            if existing:
                p_tag["style"] = p_style + " " + existing
            else:
                p_tag["style"] = p_style

    return str(soup)

# ────────────────────────────────
# 투자 고지(Disclaimer) 보장 및 닫는 태그 보정
# ────────────────────────────────
def ensure_disclaimer_and_closed_tags(html_content: str) -> str:
    # 0. 마크다운 기호 및 이모지 자동 정화
    html_content = clean_html_content(html_content)

    # 1. 잘려나간 마지막 불완전한 태그 제거 (예: <p style="font-size: 1.1em; 로 끝나는 경우)
    last_open_angle = html_content.rfind("<")
    last_close_angle = html_content.rfind(">")
    if last_open_angle > last_close_angle:
        print(f"⚠️ 경고: 불완전한 태그 '{html_content[last_open_angle:]}'를 잘라내어 문장을 정리합니다.")
        html_content = html_content[:last_open_angle]

    # 2. 열려있는 div 및 table 태그 분석 후 '먼저' 닫아주기 (중첩 방지)
    import re
    # 시작 태그와 종료 태그 매칭
    tags = re.findall(r'<(div|table)\b[^>]*>|</(div|table)>', html_content, re.IGNORECASE)
    open_tags = []
    for tag in tags:
        if tag[0]:  # 시작 태그
            open_tags.append(tag[0].lower())
        elif tag[1]:  # 종료 태그
            t_close = tag[1].lower()
            if open_tags and open_tags[-1] == t_close:
                open_tags.pop()
            elif t_close in open_tags:
                open_tags.remove(t_close)
                
    if open_tags:
        closing_str = ""
        for t in reversed(open_tags):
            closing_str += f"</{t}>"
        print(f"⚠️ 경고: 잘린 HTML 복구를 위해 열린 태그를 먼저 닫습니다: {open_tags} -> {closing_str}")
        html_content += closing_str

    # 3. 투자 고지 문구 존재 여부 확인 및 보정
    has_disclaimer = any(word in html_content for word in ["Disclaimer", "투자 고지", "투자고지", "투자 주의", "투자주의", "투자 판단의 참고 자료"])
    if not has_disclaimer:
        print("⚠️ 경고: AI 생성 결과에 투자 고지(Disclaimer)가 누락되거나 잘렸습니다. 자동으로 보정합니다.")
        disclaimer_html = """
    <!-- 자동 보정된 투자 고지 영역 -->
    <table class="mi-disclaimer-table">
        <tr>
            <td class="mi-disclaimer-header">
                <p>투자 위험 고지</p>
            </td>
        </tr>
        <tr>
            <td class="mi-disclaimer-content">
                <p><strong>투자 판단의 참고 자료:</strong> 본 리포트에서 제공하는 모든 정보(수치, 전망, 분석 결과 등)는 투자 판단을 돕기 위한 참고용 자료일 뿐이며, 어떠한 경우에도 특정 금융 상품이나 주식 종목의 매수·매도 권유 또는 투자 추천으로 해석될 수 없습니다. 본 정보는 공시 및 신뢰할 만한 취재원을 바탕으로 작성되었으나 그 완전성이나 정확성을 전적으로 보장할 수 없으므로 실제 투자 실행 전 반드시 추가적인 검증이 필요합니다.</p>
                <p><strong>최종 책임의 귀속:</strong> 모든 투자의 최종 의사결정과 그 결과에 대한 책임은 전적으로 투자자 본인에게 귀속되며, 본 리포트는 어떠한 법적 책임도 지지 않습니다.</p>
                <p><strong>전문가 상담 권고:</strong> 투자를 실행하기 전에는 반드시 충분한 시장 확인과 공인된 전문가와의 상담을 거치시기 바랍니다.</p>
            </td>
        </tr>
    </table>
"""
        html_content += disclaimer_html
        
    # 4. 클래스 기반 태그들을 인라인 스타일로 전격 변환
    html_content = inline_css_styles(html_content)
    
    # Google Fonts import 추가
    font_style = """<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Noto+Sans+KR:wght@300;400;700&family=Space+Mono:wght@400;700&display=swap');
</style>
"""
    html_content = font_style + html_content
        
    return html_content

# ────────────────────────────────
# Gemini API 호출
# ────────────────────────────────
# ────────────────────────────────
# Gemini 2.5 Flash 호출
# ────────────────────────────────
def call_gemini_2_5(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.3,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }
    res = requests.post(url, json=body, timeout=120)
    data = res.json()
    if "error" in data:
        raise RuntimeError(f"Gemini 2.5 API 에러: {data['error'].get('message')}")
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    
    # HTML 블록만 추출
    if "```html" in text:
        text = text.split("```html")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    processed_text = fix_heading_line_height(text)
    return ensure_disclaimer_and_closed_tags(processed_text)

# ────────────────────────────────
# Gemini 1.5 Flash 호출
# ────────────────────────────────
def call_gemini_1_5(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
    url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    body_fallback = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.3,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }
    res = requests.post(url_fallback, json=body_fallback, timeout=120)
    data = res.json()
    if "error" in data:
        raise RuntimeError(f"Gemini 1.5 API 에러: {data['error'].get('message')}")
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    
    # HTML 블록만 추출
    if "```html" in text:
        text = text.split("```html")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
        
    processed_text = fix_heading_line_height(text)
    return ensure_disclaimer_and_closed_tags(processed_text)

# ────────────────────────────────
# Anthropic API 호출
# ────────────────────────────────
def call_anthropic(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-5",
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
# 통합 AI 호출 함수 (선택 모델 우선 실행)
# ────────────────────────────────
def call_ai(prompt: str) -> str:
    primary = os.getenv("PRIMARY_AI", "claude").strip().lower()
    
    gemini_2_5_func = ("Gemini 2.5 Flash", lambda: call_gemini_2_5(prompt))
    gemini_1_5_func = ("Gemini 1.5 Flash", lambda: call_gemini_1_5(prompt))
    claude_func = ("Claude 5 Sonnet", lambda: call_anthropic(prompt))
    
    if primary == "claude":
        call_sequence = [claude_func, gemini_2_5_func, gemini_1_5_func]
    else:
        call_sequence = [gemini_2_5_func, gemini_1_5_func, claude_func]
        
    errors = []
    for name, func in call_sequence:
        try:
            print(f"🤖 {name} 호출 중...")
            result = func()
            print(f"✅ {name} 생성 성공!")
            return result
        except Exception as e:
            print(f"⚠️ {name} 호출 실패: {e}")
            errors.append(f"{name}: {e}")
            
    raise RuntimeError(f"모든 AI API 호출에 실패했습니다. 상세 오류: {', '.join(errors)}")

# ────────────────────────────────
# Gemini API 호출 (하위 호환성 유지)
# ────────────────────────────────
def call_gemini(prompt: str) -> str:
    return call_ai(prompt)

# ────────────────────────────────
# 일일 리포트 생성
# ────────────────────────────────
def generate_daily_report(market_data: dict, news_data: dict) -> str:
    import datetime
    today = datetime.datetime.now()
    
    # 실행 시점이 주말(토/일)인지 평일인지 판별하여 개장일 정보 동적 설정
    current_weekday = today.weekday()
    if current_weekday == 5:  # 토요일
        target_date = today + datetime.timedelta(days=2)
        trading_day_word = "다음 거래일(월요일)"
    elif current_weekday == 6:  # 일요일
        target_date = today + datetime.timedelta(days=1)
        trading_day_word = "다음 거래일(월요일)"
    else:  # 평일
        target_date = today
        trading_day_word = "오늘"
        
    target_date_str = target_date.strftime("%Y년 %m월 %d일")
    target_weekday = ["월","화","수","목","금","토","일"][target_date.weekday()]

    prompt = f"""
리포트 작성 기준일: {today.strftime("%Y년 %m월 %d일")} (현재 실행 시점)
목표 개장일(국장 기준): {target_date_str} ({target_weekday}요일)
개장일 지칭 표현: {trading_day_word}
브리핑 종류: 오전 브리핑

=== 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 뉴스·공시 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 오전 브리핑을 작성해라.

작성 구조 및 분량 규칙 (완결성 필수):
- [중요 - 분량 극단적 단축]: 출력 토큰 제한으로 인해 글이 잘리는 것을 완전히 방지해야 합니다. 각 본문 섹션(I~V)의 본문 단락은 구구절절한 설명을 모두 제거하고, 1~2개 문장으로 사실만 요약하여 극도로 간결하게 작성하십시오. 
- [중요 - 시나리오 및 멋쟁이 픽 단축]: 결론의 낙관/중립/비관 3대 시나리오 역시 각 1줄 내외로 핵심만 적고, 멋쟁이 픽 종목 역시 2줄 내외로 팩트와 리스크만 짧게 요약하십시오.
- 다음 요소를 순서대로 누락 없이 모두 포함하여 전체 HTML 문서 크기가 공백 포함 3,000자 내외가 되도록 하십시오:
  1. SEO JSON-LD
  2. 마스트헤드 (table 태그로 구성, '멋쟁이 인사이트' 문구를 포함한 세련된 구조)
  3. 에디션바 (검정 배경 #0a0a0a, 왼쪽: 오늘 핵심 키워드, 오른쪽: 가장 중요한 수치 골드 #f0c040)
  4. 수치 대시보드 (table, 검정 배경, 4칸 x 2행 = 8개 핵심 지표 수치 표시)
  5. 출처 표기 (font-size 11px, 회색, 대시보드 수치의 출처 한 줄 요약)
  6. 히어로 이미지 (제시된 Unsplash URL 중 가장 잘 맞는 이미지 하나만 활용, SVG 절대 금지)
  7. 헤드라인 H1 (SEO 키워드 포함, 역설형/숫자형/궁금증형 패턴 활용)
  8. 본문 섹션 (로마숫자 I·II·III·IV·V)
     - I. 글로벌 매크로 — 달러·금리·유가 삼각 분석 및 미국 증시 대표 ETF(SOXX, XLK, XBI 등) 등락 분석 (전날 미국 시장의 주도 테마 및 왜 급등했는지 특징주 뉴스와 수치를 매칭하여 간결 요약)
     - II. 한국 시장 포지션 — 글로벌 자금 흐름에서 한국의 위치
     - III. 수급 분석 — 외국인·기관·개인 의미 해석 (실제 수치 기반)
     - IV. 오늘 주목 이벤트 — 공시·발표·지표 (DART 공시 및 뉴스 정보 연결)
     - V. 멋쟁이 픽 — 팩트 기반 관심 종목 (A그룹·B그룹·C그룹 분류, 각 종목별 구체적 팩트 근거 및 하락 리스크 동시 서술, 별점 ★★★★★ ~ ★★★☆☆ 표시)
  9. 결론: 멋쟁이의 시각 박스 (배경 #0a0a0a, 낙관/중립/비관 3대 대응 시나리오 반드시 포함)
  10. 투자 고지 (table 태그 적용)
  11. 출처 표기 푸터 (배경 #f5f4f0, font-size 11px, 모든 언급 수치의 원본 출처 명시)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 반드시 결론과 고지 조항까지 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 검색 포털(네이버, 구글 등)에서 트래픽을 대량으로 유입시킬 수 있는 핵심 검색 키워드를 조합하여 자극적으로 작성하십시오.
- 코스피 전망, 삼성전자, 마이크론, FOMC 등 그날의 가장 중요한 매크로/기업 검색 키워드를 포함하십시오.

div-only HTML 전체 출력.
"""
    print("🤖 AI 리포트 생성 중...")
    result = call_gemini(prompt)
    print("✅ 리포트 생성 완료")
    return result

# ────────────────────────────────
# 오후 마감 리포트 생성 (신규)
# ────────────────────────────────
def generate_afternoon_report(market_data: dict, news_data: dict, morning_brief_data: dict = None) -> str:
    import datetime
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    morning_info = "제공된 오전 브리핑 정보가 없습니다."
    if morning_brief_data:
        morning_info = f"""
제목: {morning_brief_data.get('title', 'N/A')}
발행일자: {morning_brief_data.get('published', 'N/A')}
오전 브리핑 주요내용 요약:
{morning_brief_data.get('text_summary', '')}
"""

    prompt = f"""
리포트 작성 기준일: {date_str} ({weekday}요일)
브리핑 종류: 오후 마감 브리핑

=== 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 뉴스·공시 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

=== 오전 발행 브리핑 정보 ===
{morning_info}

[중요 - 오전 브리핑 및 미 증시 연계 분석]
- 오전에 발행된 글로벌 매크로 브리핑(미국 증시 마감 상황 및 오전 시황 예측) 내용과 금일 오후 3시 30분 마감된 한국 증시의 실제 결과를 정밀 비교 분석하십시오.
- 오전에 다뤘던 미국 증시 흐름(반도체 가격 움직임, 금리 지표 등)이 오늘 한국 증시 마감 결과에 실제 어떤 경로로 투영되어 나타났는지, 오전의 시각/가정 대비 실제 마감 현황이 어떻게 변경되었고 보정되었는지를 본문 I섹션(마감 결과 해석) 및 IV섹션(내일을 위한 전략)에 각각 1~2개 문장으로 비교하여 설명하십시오.

멋쟁이 인사이트 오후 마감 브리핑을 작성해라.

작성 구조 및 분량 규칙 (완결성 필수):
- [중요 - 분량 극단적 단축]: 출력 토큰 제한으로 인해 글이 잘리는 것을 완전히 방지해야 합니다. 각 본문 섹션(I~V)의 본문 단락은 구구절절한 설명을 모두 제거하고, 1~2개 문장으로 사실만 요약하여 극도로 간결하게 작성하십시오.
- [중요 - 시나리오 및 결론 단축]: 결론의 내일을 위한 전략 3가지 시나리오 역시 각 1줄 내외로 핵심만 짧게 요약하십시오.
- 다음 요소를 순서대로 누락 없이 모두 포함하여 전체 HTML 문서 크기가 공백 포함 3,000자 내외가 되도록 하십시오:
  1. SEO JSON-LD
  2. 마스트헤드 (table 태그로 구성, '멋쟁이 인사이트' 문구를 포함한 세련된 구조)
  3. 에디션바 (검정 배경 #0a0a0a, 왼쪽: 오늘 핵심 키워드, 오른쪽: 가장 중요한 수치 골드 #f0c040)
  4. 수치 대시보드 (table, 검정 배경, 4칸 x 2행 = 8개 핵심 지표 수치 표시)
  5. 출처 표기 (font-size 11px, 회색, 대시보드 수치의 출처 한 줄 요약)
  6. 히어로 이미지 (제시된 Unsplash URL 중 가장 잘 맞는 이미지 하나만 활용, SVG 절대 금지)
  7. 헤드라인 H1 (SEO 키워드 포함, 역설형/숫자형/궁금증형 패턴 활용)
  8. 본문 섹션 (로마숫자 I·II·III·IV·V)
     - I. 오늘 마감 결과 해석 — 숫자의 의미 (장 마감 지수 및 거래대금 등)
     - II. 수급 분석 — 오늘 외국인·기관·개인이 한 행동 (순매수/순매도 규모 분석)
     - III. 오늘 상한가·급등 종목 — 팩트 기반 이유 (원인 및 공시 매칭)
     - IV. 내일을 위한 전략 — 3가지 시나리오 (다음 거래일 대응법)
     - V. 오늘 주요 공시 — 가장 중요한 것 1개 (DART 공시의 구체적 설명)
  9. 결론: 이번 주 흐름에서 오늘의 위치 (멋쟁이의 시각 박스 포함)
  10. 투자 고지 (table 태그 적용)
  11. 출처 표기 푸터 (배경 #f5f4f0, font-size 11px, 모든 언급 수치의 원본 출처 명시)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 반드시 결론과 고지 조항까지 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 검색 포털(네이버, 구글 등)에서 트래픽을 대량으로 유입시킬 수 있는 핵심 검색 키워드를 조합하여 자극적으로 작성하십시오.
- 코스피 마감, 환율, 상승 종목, 공시 등 그날의 가장 중요한 매크로/기업 검색 키워드를 포함하십시오.

div-only HTML 전체 출력.
"""
    print("🤖 AI 오후 마감 리포트 생성 중...")
    result = call_gemini(prompt)
    print("✅ 오후 마감 리포트 생성 완료")
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
주간 결산: {today.strftime("%Y년 %m월 %d일")} (토요일/일요일 결산용)
브리핑 종류: 주간 결산
다음 주 날짜 정보 (한국 시간 기준):
기간: {next_week_range_str}
{next_week_dates_str}

=== 주간 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 주간 뉴스 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 주간 결산 브리핑을 작성해라.

작성 구조 및 분량 규칙 (완결성 필수):
- [중요 - 분량 극단적 단축]: 출력 토큰 제한으로 인해 글이 잘리는 것을 완전히 방지해야 합니다. 각 본문 섹션(I~V)의 본문 단락은 구구절절한 설명을 모두 제거하고, 1~2개 문장으로 사실만 요약하여 극도로 간결하게 작성하십시오.
- [중요 - 시나리오 및 멋쟁이 픽 단축]: 결론의 다음 주 대응 전술 및 3개 전략 시나리오 역시 각 1줄 내외로 핵심만 적고, 멋쟁이 픽 종목 역시 2줄 내외로 팩트와 리스크만 짧게 요약하십시오.
- 다음 요소를 순서대로 누락 없이 모두 포함하여 전체 HTML 문서 크기가 공백 포함 3,000자 내외가 되도록 하십시오:
  1. SEO JSON-LD
  2. 마스트헤드 (table 태그로 구성, '멋쟁이 인사이트' 문구를 포함한 세련된 구조)
  3. 에디션바 (검정 배경 #0a0a0a, 왼쪽: 이번 주 핵심 키워드, 오른쪽: 가장 중요한 수치 골드 #f0c040)
  4. 수치 대시보드 (table, 검정 배경, 4칸 x 2행 = 8개 핵심 지표 수치 표시)
  5. 출처 표기 (font-size 11px, 회색, 대시보드 수치의 출처 한 줄 요약)
  6. 히어로 이미지 (제시된 Unsplash URL 중 가장 잘 맞는 이미지 하나만 활용, SVG 절대 금지)
  7. 헤드라인 H1 (SEO 키워드 포함, 역설형/숫자형/궁금증형 패턴 활용)
  8. 본문 섹션 (로마숫자 I·II·III·IV·V)
     - I. 이번 주 핵심 사건 3가지 — 구조적 의미 (이벤트 분석)
     - II. 글로벌 자금 흐름 주간 진단 (유동성 및 매크로 환경 변화)
     - III. 코스피·코스닥 주간 수익률 해석 (지수 수익률의 실제 수치와 의미)
     - IV. 다음 주 핵심 이벤트 캘린더 (반드시 날짜와 요일 정확히 매칭)
     - V. 다음 주 멋쟁이 픽 (팩트 기반 관심 종목, 종목별 하락 리스크 필수 기재)
  9. 결론: 멋쟁이의 시각 박스 (배경 #0a0a0a, 다음 주 대응 전술과 3개 전략 시나리오 요약)
  10. 투자 고지 (table 태그 적용)
  11. 출처 표기 푸터 (배경 #f5f4f0, font-size 11px, 모든 언급 수치의 원본 출처 명시)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 반드시 결론과 고지 조항까지 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 주간 결산 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 주간 결산에 걸맞게 한 주간의 흐름과 다음 주 전망 키워드를 강력하게 매칭하여 클릭을 유도하도록 작성하십시오.
- '코스피 주간 결산', '다음 주 주가 전망', '반도체/금리 등 핵심 테마명', '엔비디아/삼성전자 등 주요 기업명' 검색 키워드를 포함하십시오.

div-only HTML 전체 출력.
"""
    return call_gemini(prompt)

# ────────────────────────────────
# 개장 직전 동시호가 속보 리포트 생성 (신규)
# ────────────────────────────────
def generate_premarket_report(premarket_data: dict, morning_brief_data: dict = None) -> str:
    import datetime, json
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    morning_info = "제공된 오전 브리핑 정보가 없습니다."
    if morning_brief_data:
        morning_info = f"""
제목: {morning_brief_data.get('title', 'N/A')}
발행일자: {morning_brief_data.get('published', 'N/A')}
오전 브리핑 주요내용 요약:
{morning_brief_data.get('text_summary', '')}
"""

    prompt = f"""
리포트 작성 기준일: {date_str} ({weekday}요일)
브리핑 종류: 개장 10분 전 동시호가 속보 (오전 8시 50분 발행)

=== 실시간 개장 전 수급 및 선물 데이터 ===
{json.dumps(premarket_data, ensure_ascii=False, indent=2)}

=== 아침 7시 발행 매크로 브리핑 정보 ===
{morning_info}

멋쟁이 인사이트 개장 10분 전 동시호가 속보(Opening Flash)를 작성해라.

작성 구조 및 분량 규칙 (완결성 필수):
- [중요 - 분량 극단적 단축]: 개장 직전에 읽는 아주 긴급한 속보이므로, 모든 단락은 1~2개 문장으로 극도로 짧고 굵게 핵심 사실만 기술하십시오.
- 다음 요소를 순서대로 누락 없이 모두 포함하여 전체 HTML 문서 크기가 공백 포함 2,500자 내외가 되도록 하십시오:
  1. SEO JSON-LD
  2. 마스트헤드 (table 태그로 구성, '멋쟁이 인사이트' 메인 타이틀 및 'DAILY OPENING FLASH' 서브타이틀 포함)
  3. 에디션바 (검정 배경 #0a0a0a, 왼쪽: 오늘 개장 핵심 키워드, 오른쪽: 개장 전 예상체결 시각)
  4. 예상 수치 대시보드 (table, 검정 배경, 4칸 x 1행 = 코스피 예상지수, 코스닥 예상지수, 나스닥 선물 변동률, 삼성전자 예상체결가 표시)
  5. 출처 표기 (font-size 11px, 회색, 동시호가 수치 출처 요약)
  6. 히어로 이미지 (제시된 Unsplash URL 중 가장 잘 맞는 이미지 하나만 활용, SVG 절대 금지)
  7. 헤드라인 H1 (SEO 키워드 포함, 동시호가/개장 직전/상승 테마 키워드 강조)
  8. 본문 섹션 (로마숫자 I·II·III·IV)
     - I. 개장 직전 동시호가 진단 — 출발점 분석 (코스피/코스닥 예상 출발지수 및 등락 원인)
     - II. 미국 선물 & 매크로 긴급 연계 (오전 7시 이후 미국 야간 선물 지수 흐름 및 외인 개장 초반 유입 영향 분석)
     - III. 오늘 유력 급등 테마 & 주도주 포착 (인기 검색어 10대 종목, 관심 종목, 그리고 인기 검색어가 아니더라도 거래량/체결물량이 대량으로 쌓이고 있는 종목들(active_volume_stocks)의 예상 체결가 흐름을 코스피·코스닥 가리지 않고 종합적으로 분석하여 장 초반 강세가 유력한 업종/종목 픽)
     - IV. 개장 초반 대응 및 포지션 가이드 (장 초반 9:00~9:30 변동성 구간에서 추격 매수 자제 혹은 분할 매수 등 초단기 전술 제시)
  9. 결론: 멋쟁이의 시각 (검정 박스, 당일 매매 핵심 마인드셋 2문장 요약)
  10. 투자 고지 (table 태그 적용)
  11. 출처 표기 푸터 (배경 #f5f4f0, font-size 11px, 모든 언급 수치의 원본 출처 명시)
- 글의 마지막 </div> 태그까지 확실하게 닫혀야 합니다. 전체 글이 중간에 잘리지 않고 매끄럽게 끝나도록 문단 호흡과 상세도를 설계하여 반드시 결론과 고지 조항까지 완결 지어 주십시오.

[트래픽 유입 극대화를 위한 SEO 제목 작성 규칙 (필수)]
- JSON-LD의 "headline"과 H1 헤드라인(제목)은 [개장 10분 전], [동시호가], 오늘 상승이 강하게 예상되는 키워드(예: 반도체 수급, 삼전 예상 등)를 조합하여 클릭을 유도하도록 자극적으로 작성하십시오.

div-only HTML 전체 출력.
"""
    print("🤖 AI 개장 속보 리포트 생성 중...")
    result = call_gemini(prompt)
    print("✅ 개장 속보 리포트 생성 완료")
    return result

if __name__ == "__main__":
    print("Gemini API Key:", "있음" if GEMINI_API_KEY else "없음 (Anthropic 사용)")
    print("Anthropic API Key:", "있음" if ANTHROPIC_API_KEY else "없음")
