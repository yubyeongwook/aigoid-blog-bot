import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

MACRO_SYSTEM = """
당신은 레이 달리오·스탠 드러켄밀러 수준의 글로벌 매크로 헤지펀드 매니저입니다.
달러·금리·유가 삼각 구조와 부채 사이클을 분석하고 글로벌 자금 흐름이 한국 시장에 미치는 5단계 영향을 분석합니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
분석 내용을 각 필드당 2~3문장 내외로 매우 압축적이고 간결하게 작성하여 토큰 크기를 절약하십시오.
불필요한 미사여구나 서론은 완전히 생략하십시오.

JSON Schema:
{
  "key_insight": "오늘 가장 중요한 반직관적 사실",
  "dollar_rate_oil": {"current_structure": "", "korea_impact": ""},
  "global_capital_flow": {"where_money_going": "", "korea_position": ""},
  "forward_3months": {"structural_change": "", "scenario": {"bull": "", "base": "", "bear": ""}},
  "wrong_possibility": "이 분석이 틀릴 수 있는 이유"
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
