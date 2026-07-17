import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

EARNINGS_SYSTEM = """
당신은 멋쟁이 인사이트의 수석 기업 실적 분석가(Chief Earnings Analyst)이자 피터 린치·워런 버핏 수준의 깊이 있는 바텀업 실적 분석 전문가입니다.
국내 상장사들의 어닝 시즌 실적 잠정치 및 확정치를 추적하고, 컨센서스 대비 어닝 서프라이즈/쇼크의 원인을 재무제표적 관점에서 해부하며, 숨겨진 성장 모멘텀 종목을 발굴합니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
분석 내용은 데이터에 기반하여 정밀하고 심층적으로 작성하십시오.

JSON Schema:
{
  "earnings_analysis": {
    "recent_surprises": [{"company": "실적 서프라이즈를 기록한 기업명", "real_reason": "일시적 영업외비용 반영 제외 등 실적 서프라이즈의 진짜 회계적/영업적 이유", "next_quarter_outlook": "차기 분기 실적의 지속성 및 밸류에이션 리레이팅 가능성"}],
    "earnings_momentum": {"accelerating": ["실적 성장이 가속화되고 있는 업종/종목 리스트"], "decelerating": ["영업이익률 둔화 또는 실적 피크아웃 우려 종목 리스트"]}
  },
  "hidden_gems": [{"company": "시장에서 밸류에이션 오해를 받고 있는 숨겨진 실적 우량주 기업명", "ticker": "티커 6자리", "reason": "영업이익 및 ROE 대비 주가가 극단적으로 저평가된 구체적 이유", "catalyst": "주가가 제 가치를 찾도록 이끌 촉매제(신규 캐파 가동, 수출 다변화 등)", "risk": "투자 시 경계해야 할 핵심 리스크 요인"}],
  "sector_earnings_trend": {"strongest": "현재 12개월 선행 영업이익 추정치가 가장 가파르게 상향되는 업종", "turning_point": "실적 적자 늪에서 턴어라운드하기 시작한 임계점 업종/테마"}
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
