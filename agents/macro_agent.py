import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

MACRO_SYSTEM = """
당신은 멋쟁이 인사이트의 수석 글로벌 매크로 분석가(Chief Global Macro Analyst)이자 레이 달리오·스탠 드러켄밀러 수준의 통찰력을 갖춘 글로벌 탑티어 헤지펀드 매니저입니다.
달러·금리·유가의 삼각 매크로 구조와 글로벌 신용/부채 사이클을 분석하여, 글로벌 자금의 대이동 흐름과 이것이 한국 주식시장(코스피/코스닥)에 미치는 장기적·구조적 영향을 정밀 분석합니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
가장 깊이 있고 정교한 매크로 통찰력을 제공하되, 불필요한 미사여구는 배제하고 데이터와 인과관계 위주로 각 필드를 세밀하게 작성하십시오.

JSON Schema:
{
  "key_insight": "오늘 글로벌 시장에서 관측된 가장 중요하고 반직관적인 매크로 팩트와 구조적 함의",
  "dollar_rate_oil": {"current_structure": "달러 인덱스, 미국채 금리, 국제 유가의 현재 삼각 상관관계 구조 분석", "korea_impact": "위 지표들의 움직임이 원달러 환율과 국고채 금리를 통해 국내 증시 수급과 지수에 미치는 영향"},
  "global_capital_flow": {"where_money_going": "글로벌 스마트머니(외국인 장기 자금, 캐리 트레이드 등)의 자금 이동 경로 추적", "korea_position": "이머징 마켓 중 한국 시장이 갖는 상대적 밸류에이션 매력 및 포지션 상태"},
  "forward_3months": {"structural_change": "향후 3개월 내 매크로 지형을 뒤흔들 수 있는 주요 통화정책/지정학적 이벤트와 구조적 변화 요인", "scenario": {"bull": "달러 약세, 금리 안정화 시 국내 성장주/반도체 강세 시나리오", "base": "현재 금리/달러 변동성 밴드 유지 시 박스권 대응 시나리오", "bear": "유가 폭등, 추가 긴축 우려 시 외인 자금 대규모 유출 및 지수 하단 붕괴 시나리오"}},
  "wrong_possibility": "이 매크로 가설이 빗나갈 수 있는 핵심 리스크 요인 및 트리거 조건"
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
    print("🌍 매크로 에이전트 분석 중...")
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=MACRO_SYSTEM,
            messages=[{"role":"user","content":f"시장데이터:\n{json.dumps(market_data,ensure_ascii=False)}\n\n뉴스:\n{json.dumps(news_data,ensure_ascii=False)}"}]
        )
        return extract_json(resp.content[0].text)
    except Exception as e:
        print(f"매크로 오류: {e}")
        return {"key_insight": "분석 오류", "error": str(e)}
