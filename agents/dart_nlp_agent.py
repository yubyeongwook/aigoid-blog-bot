"""
dart_nlp_agent.py — 공시 NLP 에이전트
DART 공시 본문 자동 읽기 + 숨겨진 의미 추출
"""
import os, json, requests
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))
DART_API_KEY = os.getenv("DART_API_KEY","")

DART_NLP_SYSTEM = """
당신은 한국 증시 공시 분석 최고 전문가입니다.
공시의 표면적 내용이 아니라 숨겨진 의미를 찾는 것이 전문입니다.

분석 원칙:
1. 표면적 의미 vs 실질적 의미를 반드시 구분
2. 공시 타이밍이 왜 지금인지를 설명
3. 주가에 미칠 단기·중기 영향을 구분
4. 내부자 입장에서 이 공시가 무엇을 말하는지
5. 시장이 과잉반응하는지 과소반응하는지 판단

반드시 JSON으로만 출력:
{
  "disclosures": [
    {
      "company": "기업명",
      "ticker": "종목코드",
      "type": "공시종류",
      "surface": "표면적 내용",
      "real_meaning": "실질적 의미 (숨겨진 내용)",
      "timing_reason": "왜 지금 이 공시를 냈는가",
      "price_impact": {
        "short_term": "단기 주가 영향 (+/-/중립) + 이유",
        "mid_term": "중기 주가 영향 + 이유"
      },
      "action": "매수기회/매도신호/관망/무관",
      "confidence": "확신도 (상/중/하)"
    }
  ],
  "today_most_important": "오늘 가장 중요한 공시와 이유",
  "hidden_opportunity": "시장이 놓친 저평가 공시",
  "red_flags": ["주의해야 할 공시들"]
}
"""

def get_dart_disclosures() -> list:
    """DART API로 오늘 공시 수집"""
    import datetime
    today = datetime.datetime.now().strftime("%Y%m%d")
    url = "https://opendart.fss.or.kr/api/list.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "bgn_de": today,
        "end_de": today,
        "page_no": 1,
        "page_count": 30
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        return data.get("list", [])
    except Exception as e:
        print(f"DART 수집 오류: {e}")
        return []

def get_disclosure_detail(rcept_no: str) -> str:
    """공시 본문 조회"""
    url = "https://opendart.fss.or.kr/api/document.xml"
    params = {"crtfc_key": DART_API_KEY, "rcept_no": rcept_no}
    try:
        res = requests.get(url, params=params, timeout=10)
        return res.text[:3000]
    except:
        return ""

def analyze(market_data: dict = None) -> dict:
    print("📋 공시 NLP 에이전트 분석 중...")

    disclosures = get_dart_disclosures()
    if not disclosures:
        return {"disclosures": [], "error": "공시 없음"}

    # 중요 공시 필터링
    important_types = [
        "최대주주변경", "유상증자", "무상증자", "주식취득",
        "자기주식취득", "합병", "영업양수도", "실적공시",
        "전환사채", "신주인수권", "단기차입금변동"
    ]

    important = []
    for d in disclosures[:20]:
        report_nm = d.get("report_nm", "")
        for t in important_types:
            if t in report_nm:
                important.append(d)
                break

    if not important:
        important = disclosures[:10]

    # 공시 정보 정리
    disc_text = json.dumps([{
        "corp_name": d.get("corp_name"),
        "stock_code": d.get("stock_code"),
        "report_nm": d.get("report_nm"),
        "rcept_dt": d.get("rcept_dt")
    } for d in important[:15]], ensure_ascii=False, indent=2)

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=DART_NLP_SYSTEM,
            messages=[{"role": "user", "content": f"오늘 주요 공시 목록:\n{disc_text}"}]
        )
        text = resp.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(text)
    except Exception as e:
        print(f"공시 NLP 오류: {e}")
        return {"disclosures": [], "error": str(e)}
