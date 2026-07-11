import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

TECHNICAL_SYSTEM = """
당신은 마크 미너비니·윌리엄 오닐 수준의 기술적 분석가이자 단기 트레이딩 전문가입니다.
52주 신고가 돌파, 거래량 급증, 섹터 로테이션을 분석하고 반드시 손절선과 목표가를 함께 제시합니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
분석 내용을 각 필드당 2~3문장 내외로 매우 압축적이고 간결하게 작성하여 토큰 크기를 절약하십시오.
불필요한 미사여구나 서론은 완전히 생략하십시오.

JSON Schema:
{
  "market_technical": {"kospi_structure": "", "market_stage": "", "key_levels": {"kospi_support": "", "kospi_resistance": ""}},
  "momentum_stocks": [{"name": "", "ticker": "", "signal": "", "entry_zone": "", "stop_loss": "", "target_1": "", "target_2": "", "holding_period": "", "risk_reward": "", "confidence": "", "invalidation": ""}],
  "sector_rotation_stage": {"current_leader": "", "next_leader": ""},
  "avoid_list": [{"name": "", "reason": ""}]
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
    print("📉 기술적 에이전트 분석 중...")
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=TECHNICAL_SYSTEM,
            messages=[{"role":"user","content":f"가격데이터:\n{json.dumps(market_data,ensure_ascii=False)}\n\n뉴스:\n{json.dumps(news_data,ensure_ascii=False)}"}]
        )
        return extract_json(resp.content[0].text)
    except Exception as e:
        print(f"기술적 오류: {e}")
        return {"momentum_stocks": [], "avoid_list": [], "error": str(e)}
