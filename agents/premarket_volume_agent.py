import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

PREMARKET_SYSTEM = """
당신은 한국 여의도 증권가의 데일리 트레이딩 데스크 전략가이자 인기 주식 전문 채널의 콘텐츠 디렉터입니다.
개인 투자자들의 실시간 매수 체결량, 네이버/다움 인기 검색 종목 트래픽, 급등 종목 리스트, 그리고 전일 시간외 단일가 특징주 및 당일 시초가 호가 급증 종목들을 분석하여 당일 개인 투자자들의 자금이 몰려 검색량이 폭발할 주도 테마와 급등 유망 종목을 선별합니다.

★ 중요 이스케이프 지침:
- JSON 출력 내부의 모든 문자열 값 안에서 쌍따옴표(")를 절대 그냥 쓰지 마십시오. 필요한 경우 반드시 홑따옴표(')를 쓰거나 역슬래시로 이스케이프(\\") 하십시오.
- 문장의 끝에 쉼표(,)를 남기는 문법 오류를 저지르지 마십시오.
- 분석 내용을 각 필드당 2~3문장 내외로 매우 압축적이고 간결하게 작성하십시오.

반드시 다음 형식의 JSON 구조로만 답변하십시오. 텍스트 설명이나 백틱(```) 없이 순수 JSON만 출력해야 합니다.
{
  "traffic_themes": [
    {"theme": "테마명 (예: 온디바이스 AI)", "reason": "실시간 관심도 급증 사유", "strength": "상/중/하"}
  ],
  "momentum_candidates": [
    {
      "ticker": "종목코드 (숫자 6자리 또는 영어 티커)",
      "name": "종목명",
      "catalyst": "실시간 검색 유발 촉매 (뉴스, 공급계약, 시간외 급등 등)",
      "expected_flow": "예상 자금 흐름 방향 (시초가 갭상승 후 눌림목 매수 유효 등)"
    }
  ],
  "retail_keyword_ranking": [
    {"keyword": "인기 검색 키워드", "sentiment": "긍정/부정/중립", "description": "투자자들이 이 키워드를 찾는 핵심 배경"}
  ]
}
"""

def extract_json(text: str) -> dict:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]
    return json.loads(text)

def analyze_premarket_momentum(market_data, news_data) -> dict:
    print("📈 장전 거래량/인기종목 분석 에이전트 분석 중...")
    prompt = f"""
최근 한국 및 글로벌 시장 데이터:
{json.dumps(market_data.get("surging_stocks", []), ensure_ascii=False, indent=2)}
{json.dumps(market_data.get("watchlist", []), ensure_ascii=False, indent=2)}

최신 뉴스 및 공시 정보:
{json.dumps(news_data, ensure_ascii=False, indent=2)}

위 데이터를 기반으로 실시간 개인 투자자 트래픽이 폭발하여 오늘 시초가 이후 큰 움직임을 보일 테마와 급등 모멘텀 종목을 분석하여 JSON으로 작성하라.
"""
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=PREMARKET_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        return extract_json(resp.content[0].text)
    except Exception as e:
        print(f"장전 모멘텀 분석 오류: {e}")
        return {
            "traffic_themes": [],
            "momentum_candidates": [],
            "retail_keyword_ranking": []
        }
