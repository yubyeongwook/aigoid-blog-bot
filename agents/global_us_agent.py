import os, json
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

US_SYSTEM = """
당신은 뉴욕 월스트리트의 헤지펀드 시니어 글로벌 매크로 분석가입니다.
전일 미국 증시(S&P 500, NASDAQ, SOXX 반도체 지수 등)의 움직임, 미국 국채 금리, 주요 빅테크 종목(Nvidia, Tesla, Micron, Apple 등)의 개별 호재/악재와 실적 발표 내용을 심층 분석하여, 당일 한국 증시의 개장 및 특정 섹터(반도체, 2차전지, 바이오 등)에 미칠 영향력을 연결 분석합니다.

★ 월요일 오전 특별 지침:
- 한국 시간 기준 월요일 오전의 경우, 밤사이(일요일 밤) 미국 정규장이 열리지 않았으므로 전주 금요일 마감 종가 및 주말 동안의 주요 뉴스를 기준으로 분석을 작성하십시오.

★ 중요 이스케이프 지침:
- JSON 출력 내부의 모든 문자열 값 안에서 쌍따옴표(")를 절대 그냥 쓰지 마십시오. 필요한 경우 반드시 홑따옴표(')를 쓰거나 역슬래시로 이스케이프(\\") 하십시오.
- 문장의 끝에 쉼표(,)를 남기는 문법 오류를 저지르지 마십시오.
- 분석 내용을 각 필드당 2~3문장 내외로 매우 압축적이고 간결하게 작성하십시오.

반드시 다음 형식의 JSON 구조로만 답변하십시오. 텍스트 설명이나 백틱(```) 없이 순수 JSON만 출력해야 합니다.
{
  "us_market_brief": "전일 미국 증시 요약 및 주 요인 (3줄 내외)",
  "index_movement": {
    "spy": "S&P 500 움직임 및 특징",
    "qqq": "나스닥 움직임 및 특징",
    "soxx": "필라델피아 반도체 지수 움직임 및 한국 반도체 영향"
  },
  "bigtech_catalysts": [
    {"stock": "종목명 (예: 엔비디아)", "change": "등락률 및 주 재료", "korea_spillover": "한국 관련 밸류체인 영향"}
  ],
  "macro_indicators": {
    "us_10y_yield": "미국 10년물 국채금리 수준 및 영향",
    "vix": "공포지수 흐름 및 위험자산 선호도"
  },
  "korean_market_opening_impact": "오늘 한국 시장 시초가 방향성 및 강세/약세 예상 섹터"
}
"""

def extract_json(text: str) -> dict:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]
    return json.loads(text)

def analyze_us_market(market_data, news_data) -> dict:
    print("🌍 글로벌 미국장 에이전트 분석 중...")
    prompt = f"""
전일 미국 시장 데이터:
{json.dumps(market_data.get("us_etfs", {}), ensure_ascii=False, indent=2)}

장중 급등락 종목 정보:
{json.dumps(market_data.get("surging_stocks", []), ensure_ascii=False, indent=2)}

최신 외신 및 뉴스 헤드라인:
{json.dumps(news_data, ensure_ascii=False, indent=2)}

위 데이터를 바탕으로 글로벌 매크로/미국장 관점의 심층 분석 JSON을 작성하라.
"""
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=US_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        return extract_json(resp.content[0].text)
    except Exception as e:
        print(f"글로벌 미국장 분석 오류: {e}")
        return {
            "us_market_brief": "글로벌 미국장 분석가 분석 실패",
            "index_movement": {"spy": "", "qqq": "", "soxx": ""},
            "bigtech_catalysts": [],
            "macro_indicators": {"us_10y_yield": "", "vix": ""},
            "korean_market_opening_impact": "오류 발생으로 인한 예측 불가능"
        }
