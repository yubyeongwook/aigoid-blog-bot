import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

EARNINGS_SYSTEM = """
당신은 피터 린치·워런 버핏 수준의
바텀업 실적 분석 전문가입니다.
어닝 서프라이즈 사전 탐지, 공시 숨겨진 의미 해석,
내부자 거래 신호 분석을 수행합니다.
반드시 JSON 형식으로만 출력하라.
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
            max_tokens=2000,
            system=EARNINGS_SYSTEM,
            messages=[{"role":"user","content":f"시장데이터:\n{json.dumps(market_data,ensure_ascii=False)}\n\n뉴스:\n{json.dumps(news_data,ensure_ascii=False)}"}]
        )
        return extract_json(resp.content[0].text)
    except Exception as e:
        print(f"실적 오류: {e}")
        return {"hidden_gems": [], "error": str(e)}
