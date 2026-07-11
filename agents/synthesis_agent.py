import os, json, datetime
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

SYNTHESIS_SYSTEM = """
당신은 멋쟁이 인사이트 수석 전략가입니다.
글로벌 매크로·수급·실적·기술적 분석 4개 전문가의
분석을 종합해서 세계 최강 헤지펀드 수준의 블로그를 작성합니다.

절대 금지: 느낌표, 급등 예상, 투자 유인 표현, JSON-LD, SVG
필수: 손절선 명시, 출처 표기, 투자 고지, Unsplash 이미지

HTML 구조 (div-only Blogger):
1. 마스트헤드 (table)
2. 수치 대시보드 (검정배경 #0a0a0a)
3. 히어로 이미지 (Unsplash URL)
4. H1 역설형 헤드라인
5. 섹션 I~VI (로마숫자)
6. 멋쟁이 픽
   A. 단타 (1~3일): 진입가·손절선·목표가 필수
   B. 스윙 (1~2주): 진입가·손절선·목표가 필수
   C. 중기 (1~3개월): 근거·리스크 필수
   D. 역발상: 하워드막스식·손절선 필수
7. 피할 종목 (이유 명시)
8. 3개 시나리오 (조건+대응 포함)
9. 멋쟁이의 시각 (배경 #0a0a0a·골드 #f0c040)
10. 투자 고지
11. 출처 표기 푸터
"""

def synthesize_and_write(macro, supply, earnings, technical, market_data, report_type="daily") -> str:
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    print("🧠 통합 판단 에이전트 작동 중...")
    prompt = f"""
오늘: {today.strftime("%Y년 %m월 %d일")} {weekday}요일 (KST)

=== 매크로 전문가 분석 ===
{json.dumps(macro, ensure_ascii=False, indent=2)}

=== 수급 전문가 분석 ===
{json.dumps(supply, ensure_ascii=False, indent=2)}

=== 실적·공시 전문가 분석 ===
{json.dumps(earnings, ensure_ascii=False, indent=2)}

=== 기술적 전문가 분석 ===
{json.dumps(technical, ensure_ascii=False, indent=2)}

=== 원본 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

위 4개 전문가 분석을 종합해서
세계 최강 헤지펀드 수준의 블로그를 작성하라.
4박자(매크로+수급+실적+기술적)가 맞는 종목만 최우선 픽.
손절선 없는 픽은 절대 제시하지 않는다.
div-only HTML 전체 출력.
"""
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8000,
            system=SYNTHESIS_SYSTEM,
            messages=[{"role":"user","content":prompt}]
        )
        text = resp.content[0].text
        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        print("✅ 통합 판단 완료")
        return text
    except Exception as e:
        print(f"통합 오류: {e}")
        return f"<div><p>오류: {e}</p></div>"
