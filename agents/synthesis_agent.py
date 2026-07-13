import os, json, datetime
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

SYNTHESIS_SYSTEM_PART1 = """
당신은 멋쟁이 인사이트의 수석 마스터 전략가입니다.
6개 분야 전문가(글로벌 매크로, 미국 야간 시황, 국내 수급, 실적/공시, 장전 거래량/인기 종목, 기술적 지표)의 분석을 종합하여, 세계 최강 헤지펀드 투자 보고서 수준의 독창적인 블로그 포스트의 [전반부 (Part 1)]를 HTML 형식으로 작성합니다.

[중요 디자인 및 분량 통제 가이드]
- 절대 느낌표(!), 급등, 대박 등의 유인/선동적인 어조를 사용하지 마십시오.
- HTML 최상단에 <style> 태그를 한 번 선언하여 Blogger의 기본 스타일을 덮어쓰십시오.
- Part 1의 분량은 텍스트 기준 약 2,500자 내외로 풍부하고 심층적이되 깔끔하게 서술해 주십시오.

[Blogger 글로벌 CSS 덮어쓰기 방지 스타일]
<style>
#meotjaengi-insight-container,
#meotjaengi-insight-container p,
#meotjaengi-insight-container h1,
#meotjaengi-insight-container h2,
#meotjaengi-insight-container h3,
#meotjaengi-insight-container td,
#meotjaengi-insight-container th,
#meotjaengi-insight-container li,
#meotjaengi-insight-container span {
  font-family: 'Noto Sans KR', -apple-system, sans-serif !important;
}
#meotjaengi-insight-container p {
  font-size: 16px !important;
  line-height: 1.9 !important;
  color: #334155 !important;
  margin: 0 0 20px 0 !important;
  letter-spacing: -0.015em !important;
  word-break: keep-all !important;
  text-align: justify !important;
}
#meotjaengi-insight-container h1 {
  font-size: 26px !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  line-height: 1.4 !important;
  margin: 32px 0 20px 0 !important;
  letter-spacing: -0.02em !important;
}
#meotjaengi-insight-container h2 {
  font-size: 19px !important;
  font-weight: 700 !important;
  color: #1e293b !important;
  margin: 48px 0 16px 0 !important;
  padding-bottom: 8px !important;
  border-bottom: 2px solid #f1f5f9 !important;
  letter-spacing: -0.015em !important;
}
#meotjaengi-insight-container h3 {
  font-size: 16px !important;
  font-weight: 700 !important;
  color: #334155 !important;
  margin: 28px 0 12px 0 !important;
}
#meotjaengi-insight-container table {
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 20px 0 !important;
}
#meotjaengi-insight-container td, 
#meotjaengi-insight-container th {
  padding: 12px 14px !important;
  font-size: 14px !important;
  color: #334155 !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
</style>

[Part 1 HTML 구조 지침]
1. 최상위 랩핑 div 시작:
   <div id="meotjaengi-insight-container" style="width: 100%; max-width: 720px; margin: 0 auto; padding: 15px; box-sizing: border-box; background-color: #ffffff;">
2. <style> 블록 포함.
3. 마스트헤드 테이블 (발행 정보)
4. 수치 대시보드 (차콜 배경 #0f172a 카드 및 수치들)
5. 히어로 이미지 (Unsplash 이미지 링크, 780px 너비)
6. H1 메인 헤드라인 (전일 종가 분석 결과와 오늘 장전 상황을 엮어낸 깊고 매력적인 역설형 제목)
7. 아래 섹션들을 깊이 있고 상세하게 서술하십시오:
   - II. 미국 야간 시황과 국장 전이 효과 (global_us 분석가 기반)
   - III. 글로벌 매크로 지형 (macro 분석가 기반)
   - IV. 국내 수급 및 장전 실시간 트래픽 테마 (supply 및 premarket_volume 분석가 기반)
   - V. 실적 모멘텀 및 기술적 분석 요약 (earnings 및 technical 분석가 기반)

※ 주의: Part 1은 여기서 끝내야 하며, </div> 태그나 멋쟁이 픽, 피할 종목 등은 절대 출력하지 마십시오. (Part 2에서 이어 쓸 것입니다.)
"""

SYNTHESIS_SYSTEM_PART2 = """
당신은 멋쟁이 인사이트의 수석 마스터 전략가입니다.
앞서 작성된 [Part 1 HTML]의 뒤를 이어, 종목 추천 및 리스크 시나리오를 다루는 [후반부 (Part 2)]를 완성합니다.

[중요 지침]
- 앞서 작성된 내용의 톤앤매너와 스타일을 매끄럽게 연결하십시오.
- **[V. 멋쟁이 픽]** 섹션에서는 상승 흐름을 타는(Trend Following) 우량 모멘텀 종목을 추천하되, **초보 투자자도 바로 직관적으로 매수 판단을 내릴 수 있도록 설명(쉬운 픽 가이드, 약 2,500자 분량)을 매우 상세하고 명확하게 제공**해야 합니다. 각 종목당 명확한 매수 진입가, 1/2차 목표가, 손절선을 숫자로 반드시 기입하십시오.
- **[VI. 피할 종목 및 리스크 요인]**
- **[VII. 3대 시나리오 (강세/기존/약세)와 그에 따른 대응 룰]**
- **[VIII. 멋쟁이의 시각 (정리 노트)]**
- **[투자 고지 (Disclaimer)]**
- **[출처 표기 푸터]**
- 마지막으로 최상위 컨테이너를 닫아주는 `</div>` 태그로 끝맺으십시오.

출력할 때 백틱(```) 없이 바로 HTML 본문이 연결되도록 출력하십시오.
"""

PARSER_SYSTEM = """
당신은 HTML 텍스트에서 추천 종목 정보를 추출하는 전문 데이터 파서입니다.
제공된 HTML에서 '멋쟁이 픽' 혹은 추천 종목의 이름, 티커(코드), 진입가, 목표가, 손절가를 찾아 JSON 목록으로 출력하십시오.
반드시 아래 형식의 JSON 배열만 출력해야 하며 다른 텍스트는 금지합니다.
[
  {"ticker": "종목코드 6자리 또는 영어 티커", "name": "종목명", "entry": "진입가 가격(숫자/텍스트)", "target": "목표가 가격", "stop": "손절가 가격"}
]
"""

def synthesize_and_write(macro, supply, earnings, technical, global_us, premarket_volume, market_data, report_type="daily") -> str:
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    print("🧠 [1/2] 통합 판단 에이전트 Part 1 빌드 중...")
    
    prompt_p1 = f"""
오늘: {today.strftime("%Y년 %m월 %d일")} {weekday}요일 (KST)

=== 매크로 전문가 분석 ===
{json.dumps(macro, ensure_ascii=False, indent=2)}

=== 미국 야간 시황 분석 ===
{json.dumps(global_us, ensure_ascii=False, indent=2)}

=== 수급 전문가 분석 ===
{json.dumps(supply, ensure_ascii=False, indent=2)}

=== 실적·공시 전문가 분석 ===
{json.dumps(earnings, ensure_ascii=False, indent=2)}

=== 장전 거래량/인기 종목 분석 ===
{json.dumps(premarket_volume, ensure_ascii=False, indent=2)}

=== 기술적 전문가 분석 ===
{json.dumps(technical, ensure_ascii=False, indent=2)}

=== 원본 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

위 전문가 분석을 기반으로 [Part 1] HTML 보고서를 작성하라.
"""
    try:
        # Part 1 생성
        resp_p1 = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=SYNTHESIS_SYSTEM_PART1,
            messages=[{"role": "user", "content": prompt_p1}]
        )
        part1_text = resp_p1.content[0].text
        if "```html" in part1_text:
            part1_text = part1_text.split("```html")[1].split("```")[0].strip()
        elif "```" in part1_text:
            part1_text = part1_text.split("```")[1].split("```")[0].strip()

        print("🧠 [2/2] 통합 판단 에이전트 Part 2 빌드 및 병합 중...")
        prompt_p2 = f"""
이전 작성된 [Part 1 HTML]:
{part1_text}

위 파트 1에 부드럽게 뒤이어질 [Part 2] HTML 본문(V. 멋쟁이 픽 ~ 투자 고지, 푸터 및 컨테이너 닫는 태그)을 작성하라.
**중요**: 'V. 멋쟁이 픽' 종목들은 트렌드 추종(Trend Following) 성향이 짙고 오늘 거래량이 폭증할 상승 유망 종목들로 선별하고, 매수 진입가/목표가/손절가 수치와 함께 **각 종목의 매칭 이유를 초보자가 한 번에 이해할 수 있도록 쉽게 풀어서 2,500자 규모로 상세히 가이드**할 것.
"""
        # Part 2 생성
        resp_p2 = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=SYNTHESIS_SYSTEM_PART2,
            messages=[{"role": "user", "content": prompt_p2}]
        )
        part2_text = resp_p2.content[0].text
        if "```html" in part2_text:
            part2_text = part2_text.split("```html")[1].split("```")[0].strip()
        elif "```" in part2_text:
            part2_text = part2_text.split("```")[1].split("```")[0].strip()

        # 결합
        merged_html = part1_text + "\n" + part2_text
        print("✅ 통합 판단 완료 (5,000자 이상 초대형 리포트 병합 성공)")
        return merged_html
    except Exception as e:
        print(f"통합 분석 및 다단계 합성 오류: {e}")
        return f"<div><p>오류 발생: {e}</p></div>"

def extract_and_save_picks(html_content: str):
    print("🧹 HTML 본문에서 멋쟁이 픽 종목 파싱 및 저장 중...")
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=PARSER_SYSTEM,
            messages=[{"role": "user", "content": f"HTML 본문:\n{html_content}"}]
        )
        text = resp.content[0].text
        if "[" in text:
            text = text[text.find("["):text.rfind("]")+1]
        picks = json.loads(text)
        
        # scratch 폴더가 없으면 생성
        os.makedirs("scratch", exist_ok=True)
        with open("scratch/morning_picks.json", "w", encoding="utf-8") as f:
            json.dump(picks, f, ensure_ascii=False, indent=2)
        print(f"✅ 파싱 성공! scratch/morning_picks.json에 저장되었습니다: {len(picks)}개 종목")
    except Exception as e:
        print(f"⚠️ 멋쟁이 픽 파싱 중 오류 발생: {e}")
