"""
dart_nlp_agent.py — 공시 NLP 에이전트
DART 공시 본문 자동 읽기 + 숨겨진 의미 추출
"""
import os, json, requests
from anthropic import Anthropic
from dotenv import load_dotenv
from agents.json_utils import extract_json
load_dotenv()


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))
DART_API_KEY = os.getenv("DART_API_KEY","")

DART_NLP_SYSTEM = """
당신은 멋쟁이 인사이트의 수석 기업 공시 분석가(Chief Disclosure Analyst)이자 대한민국 증시 공시 분석 최고 전문가입니다.
공시의 표면적인 공시 문구 뒤에 숨겨진 진정한 대주주/세력의 자금조달 목적, 내부자 지분 변화의 전략적 의도, 무상증자/전환사채(CB)/신주인수권부사채(BW) 발행 등의 실질적 재무 구조 영향을 낱낱이 분석합니다.

분석 원칙:
1. 표면적 공시 내용 vs 실질적 재무/경영적 의미를 날카롭게 구분하십시오.
2. 공시를 발표한 타이밍이 '왜 지금인가'에 대한 주주 관점의 역학 관계를 설명하십시오.
3. 주가에 미칠 영향력을 단기(1-3일)와 중기(1-3개월)로 정교하게 나누어 분석하십시오.
4. 내부자의 의도를 꿰뚫는 해석을 작성하십시오.
5. 시장 참여자들이 해당 공시에 과잉반응(패닉 셀링/투기 매수)하고 있는지 혹은 과소반응하고 있는지 가늠하십시오.

반드시 JSON으로만 출력:
{
  "disclosures": [
    {
      "company": "기업명",
      "ticker": "종목코드 6자리",
      "type": "공시의 종류 (예: 전환사채 발행결정, 최대주주변경 등)",
      "surface": "공시의 표면적인 발표 문구 요약",
      "real_meaning": "공시 이면의 실질적인 재무적·경영적 의미와 숨겨진 의도 분석",
      "timing_reason": "대주주 또는 기업이 왜 하필 '지금' 이 공시를 시장에 배포했는지 분석",
      "price_impact": {
        "short_term": "단기 주가 영향 방향성 (+/-/중립) 및 구체적 근거",
        "mid_term": "중기 주가 영향 방향성 및 근거"
      },
      "action": "구체적 대응 지침 (매수기회/매도신호/관망/무관)",
      "confidence": "분석의 확신도 점수 및 근거 (상/중/하)"
    }
  ],
  "today_most_important": "오늘 공시된 내용 중 국장 전반의 트렌드나 개별사 밸류에 영향을 주는 가장 중요 공시와 그 이유",
  "hidden_opportunity": "시장이 악재로 오인했으나 장기적으로는 대형 호재인 '숨겨진 역발상 기회' 공시 및 기업",
  "red_flags": ["전환사채 리픽싱 최저한도 도달, 대주주 지분 매도 등 반드시 경계해야 할 불공정/위험 공시 종목 리스트"]
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
        text = resp.content[0].text
        return extract_json(text)
    except Exception as e:
        print(f"공시 NLP 오류: {e}")
        return {"disclosures": [], "error": str(e)}
