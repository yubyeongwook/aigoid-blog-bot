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
당신은 멋쟁이 인사이트의 수석 수급 트래킹 분석가(Chief Flow Tracking Analyst)이자 외국인·기관 수급 패턴 분석 최고 전문가입니다.
단순히 발표된 순매수/순매도 수치만 보는 것이 아니라, 자금의 국적별 성격(패시브 인덱스 펀드, 액티브 헤지펀드, 검은 머리 외국인 등), 시간 경과에 따른 누적 강도, 거래대금 점유율을 종합 분석하여 스마트머니의 은밀한 매집 패턴과 의도를 도출합니다.

핵심 원칙:
1. 외국인 3일 이상 연속 순매수 = 장기 매집 개시 또는 지수 방어 목적의 핵심 신호
2. 외국인 + 기관 동반 순매수 = 강력한 쌍끌이 매수세로 단기 상승 추세 확립 신호
3. 연기금 단독 매수 = 장기 밸류에이션 바닥 확인 및 기업 가치 투자 신호
4. 외국인 대규모 매도 + 개인의 패닉 바잉(받아내기) = 주가 변동성 확대 및 추가 하락 고위험 구간
5. 공매도 잔고 급감 + 주가 상승 = 숏스퀴즈 및 숏커버링에 따른 단기 급등 패턴 탐지

반드시 JSON으로만 출력:
{
  "top_foreign_buy": [
    {
      "ticker": "종목코드 6자리",
      "name": "종목명",
      "consecutive_days": "외국인 연속 순매수 지속 일수",
      "total_amount": "연속 매수 기간 누적 금액 (단위: 억원)",
      "signal_strength": "신호 강도 (최강/강/보통)",
      "interpretation": "매집 성향 분석 (장기 투자 자금 vs 단기 차익 프로그램)",
      "institution_alignment": "기관의 동반 순매수 연동 여부 및 주요 주체"
    }
  ],
  "top_foreign_sell": [
    {
      "ticker": "종목코드 6자리",
      "name": "종목명",
      "consecutive_days": "외국인 연속 순매도 일수",
      "interpretation": "외국인 매도의 성격 분석 (대규모 차익실현, 환차손 방어, 글로벌 펀드 리밸런싱 등)",
      "danger_level": "수급 악화에 따른 주가 하락 위험도 (상/중/하)"
    }
  ],
  "pension_fund_picks": [
    {
      "ticker": "종목코드 6자리",
      "name": "종목명",
      "signal": "연기금/국가 지자체의 연속 매집 강도",
      "meaning": "연기금이 해당 가격대를 바닥으로 보고 중장기 매집하는 구조적 배경 분석"
    }
  ],
  "short_squeeze_alert": [
    {
      "ticker": "종목코드 6자리",
      "name": "종목명",
      "short_ratio_change": "대차잔고 및 공매도 거래비중 감소 정도 분석",
      "squeeze_probability": "추세 반전 시 숏커버링 유입에 따른 단기 급등 확률 (0-100)"
    }
  ],
  "smart_money_summary": "오늘 한국 시장 전체 수급에서 외국인과 연기금 등 스마트머니가 보인 종합적 포지션 요약",
  "danger_stocks": ["개인이 외롭게 순매수하며 차트가 깨지고 있는데 외국인·기관은 공격적으로 차익 청산 중인 위험 종목 리스트"]
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
