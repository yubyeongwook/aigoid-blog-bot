import os, json
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

BACKTEST_SYSTEM = """
당신은 퀀트 투자 백테스팅 전문가입니다.
현재 픽 신호의 역사적 승률을 분석합니다.
반드시 JSON으로만 출력:
{
  "signal_reliability": {
    "score": "0-100 신뢰도",
    "grade": "A/B/C/D",
    "reasoning": "근거"
  },
  "optimal_parameters": {
    "stop_loss_pct": "최적 손절 %",
    "target_pct": "최적 목표 %",
    "position_size": "권장 포지션 크기 %"
  },
  "similar_past_cases": [
    {"date": "날짜", "situation": "상황", "result": "결과"}
  ],
  "risk_adjustment": "리스크 조정 권고"
}
"""

def analyze(technical_result, supply_result, macro_result, market_data) -> dict:
    print("📐 백테스팅 에이전트 분석 중...")
    prompt = f"""
기술적 신호: {json.dumps(technical_result, ensure_ascii=False)[:500]}
수급 신호: {json.dumps(supply_result, ensure_ascii=False)[:500]}
매크로: {json.dumps(macro_result, ensure_ascii=False)[:500]}

위 신호들의 역사적 패턴을 분석하고
현재 픽의 신뢰도를 평가하라.
JSON으로만 출력.
"""
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=BACKTEST_SYSTEM,
            messages=[{"role":"user","content":prompt}]
        )
        text = resp.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(text)
    except Exception as e:
        print(f"백테스팅 오류: {e}")
        return {"signal_reliability": {"score": 50, "grade": "C"}, "error": str(e)}
