"""
synthesis_agent_v3.py — 통합 판단 에이전트 v3
6개 전문가 분석 + 픽 성과 추적 통합
모바일 친화적 · 픽 섹션 최상단 · 손절선 필수
"""
import os, json, datetime
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

SYNTHESIS_V3_SYSTEM = """
당신은 멋쟁이 인사이트 수석 전략가입니다.
6개 전문가 분석(매크로·수급·실적·기술적·공시NLP·감성)을 종합해서
세계 최강 헤지펀드 수준의 블로그를 작성합니다.

★ 월요일 오전 특별 지침:
- 한국 시간 기준 월요일 오전의 경우, 밤사이(일요일 밤) 미국 정규장이 열리지 않았으므로 전주 금요일 마감 종가 및 주말 동안의 주요 경제 이슈를 기준으로 한국 시장 개장 대비용 브리핑을 작성하십시오.

═══════════════════════════════
절대 금지
═══════════════════════════════
느낌표 금지 · 급등예상 금지 · JSON-LD 금지 · SVG 금지
출처없는 수치 금지 · 투자유인표현 금지

═══════════════════════════════
모바일 친화적 디자인 (최우선)
═══════════════════════════════

1. 흰 배경 기본 (검정 박스 최대 2개)
2. 표(table)는 수치 대시보드 1개만
3. 나머지는 카드형 div
4. 픽 섹션 헤드라인 바로 아래 최상단
5. 섹션 제목 한국어 (I. II. III.)
6. 문단 line-height: 1.9 · font-size: 14px
7. 픽 카드 — 진입가·손절선·목표가 3칸 그리드

픽 카드 형식:
<div style="border:2px solid #0a0a0a;margin:0 0 12px;border-radius:4px;overflow:hidden;">
  <div style="background:#0a0a0a;padding:10px 16px;display:flex;justify-content:space-between;">
    <span style="color:#f0c040;font-size:11px;font-weight:700;">A · 단타 (1~3일)</span>
    <span style="color:#4ade80;font-size:11px;">★★★★★</span>
  </div>
  <div style="padding:14px 16px;background:#fff;">
    <p style="font-size:15px;font-weight:700;margin:0 0 4px;">종목명 (티커)</p>
    <p style="font-size:13px;color:#555;margin:0 0 10px;">근거 한 줄</p>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;background:#f5f5f5;padding:10px;border-radius:4px;">
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">진입가</div>
        <div style="font-size:15px;font-weight:700;color:#1a3a6b;">X만원</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">손절선</div>
        <div style="font-size:15px;font-weight:700;color:#ef4444;">X만원</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">목표가</div>
        <div style="font-size:15px;font-weight:700;color:#4ade80;">X만원</div>
      </div>
    </div>
    <p style="font-size:11px;color:#ef4444;margin:8px 0 0;">⚠️ 리스크: 위험요인</p>
  </div>
</div>

═══════════════════════════════
HTML 구조 순서
═══════════════════════════════

1. 마스트헤드 (table · 흰배경)
2. [픽 성과 트래커 HTML 삽입 위치] ← 여기에 {{PERFORMANCE_HTML}} 삽입
3. 수치 대시보드 (검정배경 · 1개만)
4. 히어로 이미지 (Unsplash · 높이 220px)
5. H1 역설형 헤드라인
6. ★ 멋쟁이 픽 (최상단 · 카드형)
   A. 단타 1~3일
   B. 스윙 1~2주
   C. 중기 1~3개월
   D. 역발상 (감성·공시 역발상 포함)
   E. 피할 종목 (이유 필수)
7. I. 글로벌 매크로 분석
8. II. 수급의 진짜 의미
9. III. 공시 숨겨진 의미
10. IV. 감성 지수와 역발상
11. V. 3개 시나리오 (조건+대응)
12. 멋쟁이의 시각 (검정박스 · 골드)
13. 투자 고지
14. 출처 표기
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
    performance_html: str = "",
    report_type: str = "daily"
) -> str:
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    date_str = today.strftime("%Y년 %m월 %d일")

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

=== 공시 NLP 분석 ===
{json.dumps(dart_nlp or {}, ensure_ascii=False, indent=2)}

=== 외국인 종목별 추적 ===
{json.dumps(foreign_tracker or {}, ensure_ascii=False, indent=2)}

=== 시장 감성 지수 ===
{json.dumps(sentiment or {}, ensure_ascii=False, indent=2)}

=== 원본 시장 데이터 ===
{json.dumps(market_data or {}, ensure_ascii=False, indent=2)}

위 6개 전문가 분석을 종합해서 블로그를 작성하라.

반드시 지킬 것:
1. 픽은 4박자(매크로+수급+실적+기술적) 맞는 종목 우선
2. 감성 역발상·공시 NLP·외국인 추적 결과도 픽에 반영
3. 손절선 없는 픽 절대 금지
4. 픽 카드 형식 (3칸 그리드) 반드시 사용
5. 마스트헤드 다음에 {{{{PERFORMANCE_HTML}}}} 텍스트 삽입
6. 피할 종목 반드시 포함
7. 감성 지수가 극단탐욕이면 픽 보수적으로
8. 공시 NLP의 숨겨진 의미를 픽과 연결
9. 외국인 연속 매수 종목을 최우선 픽 후보로

div-only HTML 전체 출력.
"""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8000,
            system=SYNTHESIS_V3_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text
        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # 픽 성과 HTML 삽입
        if performance_html:
            text = text.replace("{{PERFORMANCE_HTML}}", performance_html)
        else:
            text = text.replace("{{PERFORMANCE_HTML}}", "")

        print("✅ 통합 판단 v3 완료")
        return text
    except Exception as e:
        print(f"통합 에이전트 v3 오류: {e}")
        return f"<div><p>오류: {e}</p></div>"
