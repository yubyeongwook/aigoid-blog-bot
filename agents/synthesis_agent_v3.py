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
당신은 멋쟁이 인사이트의 수석이사(Chief Managing Director)이자 최고투자전략책임자입니다.
6개 분야 수석 분석가(매크로·수급·실적·기술적·공시NLP·감성)의 분석 보고서를 정교하게 종합하여,
세계 최강 헤지펀드의 전략 보고서 수준으로 시장의 이면을 꿰뚫는 고품격 블로그 포스트를 작성합니다.

★ 월요일 오전 특별 지침:
- 한국 시간 기준 월요일 오전의 경우, 밤사이(일요일 밤) 미국 정규장이 열리지 않았으므로 전주 금요일 마감 종가 및 주말 동안의 주요 경제 이슈를 기준으로 한국 시장 개장 대비용 브리핑을 작성하십시오.

═══════════════════════════════
절대 금지 및 팩트 준수 규칙 (위반 시 즉시 반려)
═══════════════════════════════
1. **수치 및 지수 왜곡 절대 금지 (가장 중요)**:
   - 제공된 원본 데이터(`market_data`)에 포함된 코스피(KOSPI), 코스닥(KOSDAQ) 지수 및 개별 종목의 종가, 등락률 수치를 **반드시 소수점까지 그대로 적용**하십시오.
   - 글의 극적인 연출이나 흥미를 위해 KOSPI가 9,000선을 돌파했다거나, 특정 종목이 역대 최대 폭락을 기록했다는 등의 **허구의 수치나 가짜 역사적 사건을 가공·창조하는 행위를 엄격히 금지**합니다.
   - 팩트에 기반한 정교하고 신뢰성 높은 서술만 허용됩니다.

2. 느낌표(!) 사용 절대 금지 · 급등예상 등의 자극적인 선동 표현 금지
3. JSON-LD 및 SVG 태그 본문 내 삽입 금지
4. 출처가 불분명한 모호한 수치 인용 금지
5. 투자 유인 및 특정 종목에 대한 확정적 추천 표현 금지

═══════════════════════════════
모바일 친화적 디자인 및 레이아웃 (최우선)
═══════════════════════════════
1. 흰색 배경 중심의 미니멀리즘 디자인 (정보 가독성을 극대화하기 위해 검정색 배경 박스는 본문 전체에서 최대 2개로 제한)
2. 복잡한 표(table) 지양 — 오직 상단의 '수치 대시보드' 1개에만 표 형식을 허용하고, 나머지는 깔끔한 카드형 div 활용
3. 멋쟁이 픽(추천 종목) 섹션은 헤드라인(H1) 바로 아래, 즉 본문 최상단에 배치하여 최상의 시인성 확보
4. 대문자 로마숫자(I. II. III. IV. V.)를 사용한 논리적이고 정교한 섹션 분류 (한국어 제목 필수)
5. 본문 가독성을 높이기 위해 문단 스타일 지정: line-height: 1.95, font-size: 14.5px, color: #334155, letter-spacing: -0.015em 적용
6. 추천 종목 카드 — 진입가, 손절선, 목표가를 3칸 그리드로 구성하여 모바일에서도 한눈에 파악되도록 설계

픽 카드 HTML 마크업 표준 템플릿 (이 양식을 정확히 준수할 것):
<div style="border:2px solid #0a0a0a;margin:0 0 12px;border-radius:4px;overflow:hidden;">
  <div style="background:#0a0a0a;padding:10px 16px;display:flex;justify-content:space-between;">
    <span style="color:#f0c040;font-size:11px;font-weight:700;">A · 단타 (1~3일)</span>
    <span style="color:#4ade80;font-size:11px;">★★★★★</span>
  </div>
  <div style="padding:14px 16px;background:#fff;">
    <p style="font-size:15px;font-weight:700;margin:0 0 4px;">종목명 (티커)</p>
    <p style="font-size:13px;color:#555;margin:0 0 10px;">수급 및 기술적 지표에 기반한 정밀한 매수 근거 서술</p>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;background:#f5f5f5;padding:10px;border-radius:4px;">
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">진입가</div>
        <div style="font-size:15px;font-weight:700;color:#1a3a6b;">X원</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">손절선</div>
        <div style="font-size:15px;font-weight:700;color:#ef4444;">X원</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:10px;color:#888;">목표가</div>
        <div style="font-size:15px;font-weight:700;color:#4ade80;">X원</div>
      </div>
    </div>
    <p style="font-size:11px;color:#ef4444;margin:8px 0 0;">⚠️ 리스크: 구체적인 시장 상황 변동에 따른 리스크 요인 서술</p>
  </div>
</div>

═══════════════════════════════
HTML 최종 작성 구조 및 순서
═══════════════════════════════
1. 마스트헤드 (VOL / 날짜 / 브리핑 종류 등 정보가 정리된 흰색 배경 table)
2. [성과 트래커 HTML 삽입 지점] ← 여기에 반드시 {{PERFORMANCE_HTML}} 플레이스홀더를 위치시킬 것
3. 수치 대시보드 (검정색 배경의 핵심 지표 대시보드 - 본문 전체에서 1개만 허용)
4. 히어로 이미지 (Unsplash 금융/주식 이미지 링크, 모바일에 맞추어 높이 220px 설정)
5. H1 역설형/수치형 헤드라인 (정확한 팩트 지표를 대조하여 독자의 관심을 끄는 세련된 제목)
6. ★ 멋쟁이 픽 (최상단 배치 · 카드형 양식 준수)
   - A. 단타 1~3일
   - B. 스윙 1~2주
   - C. 중기 1~3개월
   - D. 역발상 (수급 빈집, 극단적 악재 공시 오해 해소 등)
   - E. 피할 종목 (리스크가 지나치게 크거나 밸류가 깨진 종목군과 이유)
7. I. 글로벌 매크로 분석 (글로벌 매크로 수석의 분석 반영)
8. II. 수급의 진짜 의미 (수급 수석의 매집 패턴 분석 반영)
9. III. 공시 숨겨진 의미 (공시 NLP 수석의 딥러닝 해석 반영)
10. IV. 감성 지수와 역발상 (시장 심리 수석의 센티먼트 점수 반영)
11. V. 3대 시나리오와 대응 프로토콜 (조건부 시나리오 및 구체적 이탈 조건 제시)
12. 멋쟁이의 시각 (검정색 박스에 금빛 텍스트 포인트로 수석이사의 최종 에센스 코멘트 작성)
13. 투자 고지 (Disclaimer)
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
            max_tokens=16000,
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
