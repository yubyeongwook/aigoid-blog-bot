"""
foreign_tracker_agent.py — 외국인 종목별 실시간 추적
연속 매수/매도 패턴 탐지 + 기관 유형별 분리 분석
"""
import os, json, requests, datetime
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))
KIS_APP_KEY = os.getenv("KIS_APP_KEY","")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET","")

FOREIGN_SYSTEM = """
당신은 외국인·기관 수급 패턴 분석 최고 전문가입니다.
단순 수급 수치가 아니라 패턴과 의도를 읽습니다.

핵심 원칙:
1. 외국인 3일 이상 연속 순매수 = 가장 강한 신호
2. 외국인 + 기관 동반 순매수 = 최강 신호
3. 연기금 단독 매수 = 장기 가치투자 신호
4. 외국인 매도 + 개인 매수 = 위험 구간
5. 공매도 잔고 급감 + 주가 상승 = 숏커버링

반드시 JSON으로만 출력:
{
  "top_foreign_buy": [
    {
      "ticker": "종목코드",
      "name": "종목명",
      "consecutive_days": "연속 매수 일수",
      "total_amount": "누적 금액(억)",
      "signal_strength": "신호 강도 (최강/강/보통)",
      "interpretation": "이 수급의 의미",
      "institution_alignment": "기관 동반 여부"
    }
  ],
  "top_foreign_sell": [
    {
      "ticker": "종목코드",
      "name": "종목명",
      "consecutive_days": "연속 매도 일수",
      "interpretation": "매도 이유 (이탈/ADR전환/헤지/차익)",
      "danger_level": "위험도 (상/중/하)"
    }
  ],
  "pension_fund_picks": [
    {
      "ticker": "종목코드",
      "name": "종목명",
      "signal": "연기금 매수 신호",
      "meaning": "연기금이 사는 이유"
    }
  ],
  "short_squeeze_alert": [
    {
      "ticker": "종목코드",
      "name": "종목명",
      "short_ratio_change": "공매도 잔고 변화",
      "squeeze_probability": "숏스퀴즈 확률"
    }
  ],
  "smart_money_summary": "스마트머니 종합 신호",
  "danger_stocks": ["개인만 사고 외국인·기관 파는 종목들"]
}
"""

def get_kis_token() -> str:
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET
    }
    try:
        res = requests.post(url, json=body, timeout=10)
        return res.json().get("access_token", "")
    except:
        return ""

def get_foreign_trading_top(token: str) -> list:
    """외국인 순매수 상위 종목"""
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/ranking/foreign-institution-total"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "FHPST02060000"
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_COND_SCR_DIV_CODE": "20061",
        "FID_INPUT_ISCD": "0000",
        "FID_DIV_CLS_CODE": "0",
        "FID_BLNG_CLS_CODE": "0",
        "FID_TRGT_CLS_CODE": "111111111",
        "FID_TRGT_EXLS_CLS_CODE": "0000000000",
        "FID_INPUT_PRICE_1": "0",
        "FID_INPUT_PRICE_2": "0",
        "FID_VOL_CNT": "0",
        "FID_INPUT_DATE_1": ""
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        return res.json().get("output", [])[:20]
    except:
        return []

def get_naver_foreign_top() -> list:
    """네이버 외국인 순매수 상위 (백업)"""
    from bs4 import BeautifulSoup
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = "https://finance.naver.com/sise/sise_net_investor.naver?sosok=0"
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.type_2 tr")
        result = []
        for row in rows[:15]:
            cols = row.select("td")
            if len(cols) >= 5:
                name_el = row.select_one("td.name a")
                if name_el:
                    result.append({
                        "name": name_el.text.strip(),
                        "foreign": cols[2].text.strip() if len(cols) > 2 else "0"
                    })
        return result
    except:
        return []

def analyze(market_data: dict = None) -> dict:
    print("🔍 외국인 추적 에이전트 분석 중...")

    token = get_kis_token()
    foreign_data = []

    if token:
        foreign_data = get_foreign_trading_top(token)
    if not foreign_data:
        foreign_data = get_naver_foreign_top()

    data_text = json.dumps(foreign_data[:15], ensure_ascii=False, indent=2)
    market_text = json.dumps(market_data or {}, ensure_ascii=False, indent=2)

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=FOREIGN_SYSTEM,
            messages=[{"role": "user", "content": f"""
외국인 종목별 수급 데이터:
{data_text}

전체 시장 데이터:
{market_text}

위 데이터를 분석해서 스마트머니 패턴을 찾아라.
JSON으로만 출력.
"""}]
        )
        text = resp.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(text)
    except Exception as e:
        print(f"외국인 추적 오류: {e}")
        return {"smart_money_summary": "분석 오류", "error": str(e)}
