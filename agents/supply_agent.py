import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

SUPPLY_SYSTEM = """
당신은 멋쟁이 인사이트의 수석 국내 수급 분석가(Chief Domestic Supply Analyst)이자 한국 증시 수급 분석 최고 전문가입니다.
외국인·기관·개인 수급의 일별/주별 구조적 거래 양상을 추적하고, 스마트머니의 은밀한 매집 의도 및 대차잔고 분석을 통한 숏커버링(또는 숏스퀴즈) 가능성을 날카롭게 탐지합니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
분석 내용은 데이터에 기반하여 정교하고 전문성 있게 작성하되, 서론은 생략하고 본론 위주로 채워주십시오.

JSON Schema:
{
  "market_supply": {
    "foreign": {"real_meaning": "오늘 외국인 순매수/순매도의 진정한 매크로적·수급적 배경 해석", "historical_pattern": "과거 역사적 수급 전환점 패턴과 비교 분석"},
    "smart_money_signal": "기관(연기금, 사모펀드 등) 및 외국계 비차익 프로그램 매매를 통한 스마트머니 유입 신호 정밀 해독"
  },
  "sector_rotation": {"money_entering": "자금이 강하게 들어오는 주도 업종/테마 및 거래대금 쏠림 정도", "money_leaving": "자금이 이탈하고 있는 소외 업종/테마 및 거래량 급감 징후"},
  "abnormal_supply_stocks": [{"name": "비정상적 수급 징후를 보이는 종목명", "signal": "종목의 구체적 매집/청산 신호 (예: 사모펀드 5일 연속 순매수 등)", "meaning": "해당 수급이 내포하는 내부 호재 오해 또는 세력 평단가 분석"}],
  "3day_direction": {"kospi": "단기 3거래일 코스피 지수의 수급적 방향성 예측 (조건부)", "key_condition": "해당 방향성 달성을 위한 외국인 선물 매매 또는 환율 등의 선결 조건"}
}
"""

def extract_json(text: str) -> dict:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]
    return json.loads(text)

def analyze(market_data: dict, news_data: dict) -> dict:
    print("📊 수급 에이전트 분석 중...")
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=SUPPLY_SYSTEM,
            messages=[{"role":"user","content":f"수급데이터:\n{json.dumps(market_data,ensure_ascii=False)}\n\n뉴스:\n{json.dumps(news_data,ensure_ascii=False)}"}]
        )
        return extract_json(resp.content[0].text)
    except Exception as e:
        print(f"수급 오류: {e}")
        return {"market_supply": {"smart_money_signal": "분석 오류"}, "error": str(e)}
