"""
sentiment_agent.py — 시장 감성 지수 에이전트
뉴스·커뮤니티·공포탐욕 지수 자동 생성
"""
import os, json, requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))
HEADERS = {"User-Agent": "Mozilla/5.0"}

SENTIMENT_SYSTEM = """
당신은 시장 심리 분석 전문가입니다.
뉴스·커뮤니티 감성을 분석해서 
공포탐욕 지수와 역발상 신호를 도출합니다.

핵심 원칙:
1. 극단적 공포 = 매수 기회 (하워드 막스)
2. 극단적 탐욕 = 위험 신호 (워런 버핏)
3. 커뮤니티 과열 = 차익실현 타이밍
4. 언론 비관론 극대화 = 바닥 신호
5. 감성이 팩트보다 더 강하게 주가를 움직이는 구간을 찾아라

반드시 JSON으로만 출력:
{
  "fear_greed_index": {
    "score": "0-100 (0=극단공포, 100=극단탐욕)",
    "level": "극단공포/공포/중립/탐욕/극단탐욕",
    "trend": "전주 대비 방향"
  },
  "news_sentiment": {
    "positive_ratio": "긍정 뉴스 비율 %",
    "negative_ratio": "부정 뉴스 비율 %",
    "hot_keywords": ["오늘 가장 많이 언급된 키워드들"],
    "contrarian_signal": "역발상 신호 (있으면 설명)"
  },
  "community_sentiment": {
    "overall": "과열/정상/침체",
    "hot_stocks": ["커뮤니티 과열 종목들 - 주의 필요"],
    "underrated_stocks": ["커뮤니티에서 소외된 종목들 - 관심 필요"]
  },
  "media_cycle": {
    "stage": "공포극대화/회의론/낙관론/흥분기 중 어느 단계",
    "implication": "이 단계에서 어떻게 대응해야 하는가"
  },
  "contrarian_opportunities": [
    {
      "ticker": "종목코드",
      "name": "종목명",
      "sentiment_signal": "감성 역발상 신호",
      "reason": "왜 역발상인가"
    }
  ],
  "risk_warning": "과열·버블 경고 신호"
}
"""

def get_naver_news_sentiment() -> list:
    """네이버 금융 뉴스 수집"""
    try:
        url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("dl dd.articleSubject a")
        return [item.text.strip() for item in items[:20]]
    except:
        return []

def get_naver_hot_stocks() -> list:
    """네이버 급상승 검색 종목"""
    try:
        url = "https://finance.naver.com/sise/lastsearch2.naver"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.type_5 tr")
        hot = []
        for row in rows[:10]:
            name_el = row.select_one("td a")
            if name_el:
                hot.append(name_el.text.strip())
        return hot
    except:
        return []

def analyze(market_data: dict = None, news_data: dict = None) -> dict:
    print("💭 감성 에이전트 분석 중...")

    news_headlines = get_naver_news_sentiment()
    hot_stocks = get_naver_hot_stocks()

    prompt = f"""
오늘 주요 뉴스 헤드라인:
{json.dumps(news_headlines, ensure_ascii=False, indent=2)}

커뮤니티 급상승 검색 종목:
{json.dumps(hot_stocks, ensure_ascii=False, indent=2)}

시장 데이터:
{json.dumps(market_data or {}, ensure_ascii=False, indent=2)}

위 데이터를 바탕으로 시장 감성 지수를 분석하라.
극단적 공포·탐욕 구간을 탐지하고
역발상 기회를 찾아라.
JSON으로만 출력.
"""
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=SENTIMENT_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(text)
    except Exception as e:
        print(f"감성 에이전트 오류: {e}")
        return {"fear_greed_index": {"score": 50, "level": "중립"}, "error": str(e)}
