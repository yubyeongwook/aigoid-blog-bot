"""
sentiment_agent.py — 시장 감성 지수 에이전트
뉴스·커뮤니티·공포탐욕 지수 자동 생성
"""
import os, json, requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from dotenv import load_dotenv
from agents.json_utils import extract_json

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))
HEADERS = {"User-Agent": "Mozilla/5.0"}

SENTIMENT_SYSTEM = """
당신은 멋쟁이 인사이트의 수석 시장 심리 분석가(Chief Market Sentiment Analyst)이자 시장 대중 심리의 흐름을 해독하는 행동경제학 및 센티먼트 분석 최고 전문가입니다.
뉴스 미디어의 어조, 포털 토론방 및 투자 커뮤니티의 모멘텀 과열/공포 정도, 공포탐욕 지수를 정밀 측정하여, 대중의 편향(Bias)이 팩트보다 주가를 비이성적으로 자극하고 있는 역발상(Contrarian) 투자 기회를 발굴합니다.

핵심 원칙:
1. 대중의 극단적 공포 = 최대 매수 기회 (하워드 막스)
2. 대중의 극단적 탐욕 = 리스크 관리 및 분할 매도 신호 (워런 버핏)
3. 투자 커뮤니티 과열(찬티 득세) = 단기 차익실현 및 비중 축소 타이밍
4. 주요 미디어 비관론의 절대적 임계치 도달 = 지수의 역사적 바닥 및 턴어라운드 신호
5. 대중의 감정이 이성적 가치보다 앞서 주가를 왜곡시키는 '비이성적 과열/낙폭' 구간을 발견합니다.

반드시 JSON으로만 출력:
{
  "fear_greed_index": {
    "score": "0-100 (0=극단공포, 100=극단탐욕)",
    "level": "극단공포/공포/중립/탐욕/극단탐욕",
    "trend": "전주 대비 지수 변동 방향성 및 속도"
  },
  "news_sentiment": {
    "positive_ratio": "수집된 시장 뉴스 중 긍정 톤의 비율 (%)",
    "negative_ratio": "부정 톤의 비율 (%)",
    "hot_keywords": ["언론 미디어에서 오늘 집중 언급된 핵심 키워드 리스트"],
    "contrarian_signal": "뉴스 톤의 쏠림이 유발한 심리적 왜곡 및 역발상 트레이딩 신호 기술"
  },
  "community_sentiment": {
    "overall": "투자 커뮤니티(종토방 등)의 전반적 과열/정상/침체 상태 판정",
    "hot_stocks": ["개인 투자자들의 단기 추격매수세가 쏠려 상투 위험이 높은 과열 종목 리스트"],
    "underrated_stocks": ["실적 대비 개인들의 불신과 조롱이 팽배하여 오히려 저점 매수가 매력적인 소외 종목 리스트"]
  },
  "media_cycle": {
    "stage": "공포극대화/회의론/낙관론/흥분기 중 현재 시장이 속한 미디어 사이클 국면",
    "implication": "현재 사이클 국면에서 이성적 투자자가 취해야 할 최적의 자산 배분 전략"
  },
  "contrarian_opportunities": [
    {
      "ticker": "종목코드 6자리",
      "name": "종목명",
      "sentiment_signal": "해당 종목에 발생한 감성적 괴리 신호 (예: 과도한 악재 뉴스 우려 등)",
      "reason": "시장의 감정적 왜곡으로 주가가 청산가치 근처까지 왜곡된 역발상적 진입 기회 분석"
    }
  ],
  "risk_warning": "과열 징후, 잠재적 버블 및 시장 전반의 비이성적 포모(FOMO) 증상 경고"
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
        text = resp.content[0].text
        return extract_json(text)
    except Exception as e:
        print(f"감성 에이전트 오류: {e}")
        return {"fear_greed_index": {"score": 50, "level": "중립"}, "error": str(e)}
