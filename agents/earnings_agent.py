import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

EARNINGS_SYSTEM = """
당신은 피터 린치·워런 버핏 수준의 바텀업 실적 분석 전문가입니다.
어닝 서프라이즈 사전 탐지, 공시 숨겨진 의미 해석, 내부자 거래 신호 분석을 수행합니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
분석 내용을 각 필드당 2~3문장 내외로 매우 압축적이고 간결하게 작성하여 토큰 크기를 절약하십시오.
불필요한 미사여구나 서론은 완전히 생략하십시오.

JSON Schema:
{
  "earnings_analysis": {
    "recent_surprises": [{"company": "", "real_reason": "", "next_quarter_outlook": ""}],
    "earnings_momentum": {"accelerating": [], "decelerating": []}
  },
  "hidden_gems": [{"company": "", "ticker": "", "reason": "", "catalyst": "", "risk": ""}],
  "sector_earnings_trend": {"strongest": "", "turning_point": ""}
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
    print("📈 실적·공시 에이전트 분석 중...")
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=EARNINGS_SYSTEM,
            messages=[{"role":"user","content":f"시장데이터:\n{json.dumps(market_data,ensure_ascii=False)}\n\n뉴스:\n{json.dumps(news_data,ensure_ascii=False)}"}]
        )
        return extract_json(resp.content[0].text)
    except Exception as e:
        print(f"실적 오류: {e}")
        return {"hidden_gems": [], "error": str(e)}
