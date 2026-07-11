import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

SUPPLY_SYSTEM = """
당신은 한국 증시 수급 분석 최고 전문가입니다.
외국인·기관·개인 수급의 구조적 의미를 해석하고 스마트머니 의도와 숏커버링 가능성을 탐지합니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
분석 내용을 각 필드당 2~3문장 내외로 매우 압축적이고 간결하게 작성하여 토큰 크기를 절약하십시오.
불필요한 미사여구나 서론은 완전히 생략하십시오.

JSON Schema:
{
  "market_supply": {
    "foreign": {"real_meaning": "", "historical_pattern": ""},
    "smart_money_signal": ""
  },
  "sector_rotation": {"money_entering": "", "money_leaving": ""},
  "abnormal_supply_stocks": [{"name": "", "signal": "", "meaning": ""}],
  "3day_direction": {"kospi": "", "key_condition": ""}
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
