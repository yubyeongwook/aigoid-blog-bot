import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

TECHNICAL_SYSTEM = """
당신은 멋쟁이 인사이트의 수석 기술적 분석가(Chief Technical Analyst)이자 마크 미너비니·윌리엄 오닐 수준의 기술적 분석가 및 단기 트레이딩 전문 전략가입니다.
지수 및 종목의 이동평균선 배열 상태, RSI/MACD 지표, 거래량 변화율, 52주 신고가 돌파, 변동성 돌파(VCP) 패턴 등을 종합 분석하고 진입가, 손절선, 1/2차 목표가를 논리적으로 산출해냅니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
분석 내용은 차트적 관점에서 정밀하고 구체적인 지표 값을 명시하며 신중하게 작성하십시오.

JSON Schema:
{
  "market_technical": {"kospi_structure": "코스피의 기술적 추세 구조 (예: 20일선 지지 붕괴, 과매도 구간 진입 등)", "market_stage": "현재 한국 증시의 장기 추세 국면 분류 (상승/횡보/하락국면)", "key_levels": {"kospi_support": "지지선 지수 수치", "kospi_resistance": "저항선 지수 수치"}},
  "momentum_stocks": [{"name": "기술적 패턴이 완성되어 당장 내일 진입 가능한 종목명", "ticker": "티커 6자리", "signal": "어떤 기술적 패턴이 포착되었는지 구체적 지표 설명 (예: 골든크로스, 거래대금 500% 급증 등)", "entry_zone": "합리적인 매수 진입 밴드 가격 범위(원화 기준)", "stop_loss": "패턴 이탈 시 칼같이 잘라내야 할 손절선 가격(원화)", "target_1": "1차 단기 저항선 및 목표 가격(원화)", "target_2": "2차 중기 추세 추종 목표 가격(원화)", "holding_period": "예상 보유 기간(예: 3거래일, 2주 등)", "risk_reward": "손익비 분석 결과 코멘트", "confidence": "신뢰도 점수 (0-100)", "invalidation": "상승 시나리오가 무효화되는 구체적 가격 조건"}],
  "sector_rotation_stage": {"current_leader": "거래량을 동반한 기술적 주도주 섹터", "next_leader": "순환매 관점에서 낙폭과대 후 20일선 돌파를 시도하는 후속 대기 섹터"},
  "avoid_list": [{"name": "이동평균선 역배열, 거래량 없는 하락 등 기술적으로 절대 진입해서는 안 될 종목명", "reason": "기술적 하락 지속 신호에 대한 상세한 이유"}],
  "sentiment_index": "시장 심리/센티먼트 지수 점수 (0-100)"
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
