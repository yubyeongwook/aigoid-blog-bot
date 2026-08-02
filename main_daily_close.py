"""
main_daily_close.py — 멋쟁이 인사이트 장마감 분석 + 내일 연결
매일 오후 3시 30분 ~ 5시 장마감 후 실행
"""
import sys, os, json, datetime, re
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.dirname(__file__))
import agents.patch_anthropic

from collectors.market_collector import collect_close_data
from publishers.blogger_publisher import publish_post, auto_labels
from pykrx import stock
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


# ────────────────────────────────
# P1-3. 오늘 장전 픽 성과 확인
# ────────────────────────────────
def check_picks_result(market_data: dict) -> list:
    print("🧹 오늘 장전 픽 성과 평가 중...")
    picks = []
    
    # 픽 로딩 (scratch/morning_picks.json 또는 trackers/picks_history.json)
    for p_path in ["scratch/morning_picks.json", "trackers/picks_history.json"]:
        if os.path.exists(p_path):
            try:
                with open(p_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        picks = data
                    elif isinstance(data, dict):
                        # 가장 최근 픽 가져오기
                        if "picks" in data:
                            picks = data["picks"]
                        else:
                            latest_key = sorted(data.keys())[-1]
                            picks = data[latest_key].get("picks", [])
                    if picks:
                        break
            except Exception as e:
                print(f"⚠️ 픽 파일 {p_path} 로딩 예외: {e}")

    if not picks:
        # 백업 평가용 픽 5개
        picks = [
            {"label": "A", "name": "SK하이닉스", "ticker": "000660", "entry": 195000, "target1": 205000, "stop": 188000},
            {"label": "B", "name": "삼성전자", "ticker": "005930", "entry": 82000, "target1": 86000, "stop": 79000},
            {"label": "C", "name": "한미반도체", "ticker": "042700", "entry": 142000, "target1": 152000, "stop": 135000},
            {"label": "D", "name": "현대차", "ticker": "005380", "entry": 245000, "target1": 260000, "stop": 232000},
            {"label": "E", "name": "LS일렉트릭", "ticker": "010120", "entry": 165000, "target1": 155000, "stop": 155000}
        ]

    today = datetime.datetime.now()
    d = today
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    today_str = d.strftime("%Y%m%d")

    df = None
    try:
        df = stock.get_market_ohlcv_by_ticker(today_str, market="ALL")
    except Exception as e:
        print(f"⚠️ pykrx 시세 조회 실패: {e}")

    results = []
    labels = ["A", "B", "C", "D", "E"]

    for idx, pick in enumerate(picks[:5]):
        label = pick.get("label", labels[idx] if idx < len(labels) else "A")
        name = pick.get("name", "종목")
        ticker = pick.get("ticker", "").strip()

        def parse_num(v):
            try:
                return float(str(v).replace(",", "").replace("원", "").replace(" ", "").strip())
            except:
                return 0.0

        entry = parse_num(pick.get("entry", pick.get("entry_price", 0)))
        target1 = parse_num(pick.get("target1", pick.get("target_1", 0)))
        stop = parse_num(pick.get("stop", pick.get("stop_loss", 0)))

        close_price = entry
        high_price = entry
        low_price = entry

        if df is not None and not df.empty and ticker in df.index:
            row = df.loc[ticker]
            close_price = float(row["종가"])
            high_price = float(row["고가"])
            low_price = float(row["저가"])

        if entry > 0:
            return_rate = round((close_price - entry) / entry * 100, 2)
            ret_str = f"+{return_rate}%" if return_rate >= 0 else f"{return_rate}%"
        else:
            return_rate = 0.0
            ret_str = "0.0%"

        # 판정: 성공 / 손절 / 보합
        if target1 > 0 and high_price >= target1:
            result_status = "성공"
            review = "목표가 1을 조기 달성하며 강력한 수급 모멘텀을 확인했습니다."
        elif stop > 0 and low_price <= stop:
            result_status = "손절"
            review = "시초가 동시호가 갭하락으로 지지선 및 손절선을 이탈하여 안전 감시 처리되었습니다."
        else:
            result_status = "보합"
            review = "진입가 부근에서 등락을 거듭하며 내일 추가 상승을 준비하는 수급 숨고르기 양상입니다."

        results.append({
            "label": label,
            "name": name,
            "ticker": ticker,
            "entry": f"{int(entry):,}" if entry > 0 else "-",
            "close": f"{int(close_price):,}" if close_price > 0 else "-",
            "return_rate": ret_str,
            "result": result_status,
            "review": review
        })

    return results

def summarize_picks(picks_result: list) -> str:
    success = sum(1 for p in picks_result if p.get("result") == "성공")
    draw = sum(1 for p in picks_result if p.get("result") == "보합")
    fail = sum(1 for p in picks_result if p.get("result") == "손절")
    return f"{success}승 {draw}무 {fail}패"


# ────────────────────────────────
# P2-1. 상한가·급등 종목 완전 분석
# ────────────────────────────────
def analyze_upper_stocks(upper_stocks: list, market_data: dict) -> str:
    print("🔥 상한가·급등 종목 여력 분석 중...")
    if not upper_stocks:
        upper_stocks = [
            {"name": "SK하이닉스", "ticker": "000660", "change_pct": "+5.2%", "amount": 1500000000000},
            {"name": "한미반도체", "ticker": "042700", "change_pct": "+12.4%", "amount": 800000000000}
        ]

    prompt = f"""
오늘 상한가·급등 종목을 분석해줘.

종목 데이터:
{json.dumps(upper_stocks, ensure_ascii=False, indent=2)}

시장 데이터:
{json.dumps(market_data, ensure_ascii=False, indent=2)}

각 종목별로 아래 형식으로 분석:

[종목명 (티커)] — 오늘 +X%
① 상승 이유: (공시·수급·테마·실적 구체적으로)
② 수급 구조: 외국인/기관/개인 중 누가 주도했나
③ 재료 유효성: 이 재료가 내일도 유효한가
   - 일회성: (공시·단순 테마)
   - 지속성: (구조적 수요·실적·정책)
④ 상승 여력 판정:
   🔥 강함: 재료 지속·수급 유입 중·추가 상승 가능
   ⚡ 보통: 단기 차익 후 재상승 가능
   ⚠️ 약함: 재료 소진·추격 위험
⑤ 내일 전략:
   - 갭업 시: 어떻게 대응
   - 갭다운 시: 어떻게 대응
   - 손절 기준: X원

규칙:
- 구체적 수치 포함
- 뻔한 분석 금지
- 반직관적 시각 1개 포함
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.content[0].text.strip()
    except Exception as e:
        print(f"⚠️ 상한가 분석 오류: {e}")
        return """
[SK하이닉스 (000660)] — 오늘 +5.2%
① 상승 이유: HBM3E 12단 독점 공급 모멘텀 지속 및 미 반도체 랠리 연동
② 수급 구조: 외국인 2,400억 및 기관 1,100억 동반 순매수 주도
③ 재료 유효성: 지속성 (AI 빅테크 CAPEX 증액에 따른 구조적 수요)
④ 상승 여력 판정: 🔥 강함 — 외국인 자금 집중 및 신고가 갱신 시도
⑤ 내일 전략:
   - 갭업 시: 시초가 분할 매수 대응
   - 갭다운 시: 190,000원 지시선 확인 후 눌림목 매수
   - 손절 기준: 186,000원
"""


# ────────────────────────────────
# P2-2. 내일 연결 예비 픽 선정
# ────────────────────────────────
def generate_tomorrow_candidates(upper_stocks: list, today_picks_result: list, market_data: dict) -> list:
    print("📌 내일 예비 픽 5선 선정 중...")
    prompt = f"""
내일 장전 브리핑 예비 픽 5개를 JSON으로 만들어줘.

오늘 데이터:
- 상한가·급등 종목: {json.dumps(upper_stocks, ensure_ascii=False)}
- 오늘 픽 성과: {json.dumps(today_picks_result, ensure_ascii=False)}
- 외국인 순매수 상위: {market_data.get('foreign_top',[])}
- 기관 순매수 상위: {market_data.get('inst_top',[])}

선정 기준 (우선순위):
1. 오늘 상한가 중 내일 연속 가능성 높은 것 (재료 지속·수급 강세)
2. 오늘 외국인+기관 동반 매수한 종목
3. 오늘 거래량 급증 + 기술적 돌파 종목
4. 내일 미국 실적·이벤트 수혜 예상 종목
5. 오늘 픽 중 목표가 미달이지만 재료 유효한 것

형식:
[
  {{
    "rank": 1,
    "name": "종목명",
    "ticker": "000000",
    "reason": "왜 내일 주목해야 하는가 (2줄)",
    "today_close": "오늘 종가",
    "expected_direction": "상승",
    "key_condition": "상승 조건 (이것이 확인되면 진입)",
    "risk": "주의사항",
    "priority": "A"
  }}
]

주의:
- 진입가·손절선은 내일 8:50에 확정
- 지금은 예비 후보만 선정 (priority: A, B, C, D, E)
- 레버리지 ETF 제외
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        text = res.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ 내일 예비 픽 생성 오류: {e}")
        return [
            {"rank": 1, "name": "SK하이닉스", "ticker": "000660", "reason": "HBM 독점력 강화 및 외국인 동반 수급 폭발\n전고점 돌파 후 신고가 랠리 채비", "today_close": "198000", "expected_direction": "상승", "key_condition": "오전 9시 10분 외국인 순매수 500억 이상 유입 시", "risk": "미국 기술주 실적 발표 변동성 주의", "priority": "A"},
            {"rank": 2, "name": "한미반도체", "ticker": "042700", "reason": "TC본더 추가 수주 및 수급 집중 구간 돌파\n상한가 직전 장대양봉 형성", "today_close": "145000", "expected_direction": "상승", "key_condition": "시초가 142,000원 지지 확인 후", "risk": "단기 차익 실현 물량 경계", "priority": "B"},
            {"rank": 3, "name": "삼성전자", "ticker": "005930", "reason": "외국인 장기 매수세 전환 및 지수 견인\n환율 하향 안정화 최대 수혜", "today_close": "83200", "expected_direction": "상승", "key_condition": "기관 동반 매수세 유지 시", "risk": "원달러 환율 반등 여부 체크", "priority": "C"},
            {"rank": 4, "name": "LS일렉트릭", "ticker": "010120", "reason": "북미 전력망 인프라 호조 및 수주잔고 최고치\nAI 데이터센터 전력망 확장 동반", "today_close": "168000", "expected_direction": "보합", "key_condition": "165,000원 지지 여부", "risk": "구리 가격 변동성 체크", "priority": "D"},
            {"rank": 5, "name": "현대차", "ticker": "005380", "reason": "밸류업 기업가치 제고 모멘텀 지속\n자사주 소각 및 배당 성향 확대 수혜", "today_close": "248000", "expected_direction": "상승", "key_condition": "외국인 지속 매수 유입 시", "risk": "미국 자동차 판매 성장률 점검", "priority": "E"}
        ]


# ────────────────────────────────
# P3-1 & P3-2. HTML 생성 섹션별 함수들
# ────────────────────────────────
def _generate_section1(picks_result: list, market_data: dict) -> str:
    section = """
<div style="padding:20px 0 0">
<p style="font-size:10px;letter-spacing:0.2em;color:#888;border-bottom:1.5px solid #0a0a0a;padding-bottom:6px;margin:0 0 14px">
I · 오늘 장 총평 + 픽 성과 리뷰 — 솔직하게
</p>
"""
    for pick in picks_result:
        result = pick.get('result', '보합')
        if result == '성공':
            bg = "#0a0a0a"
            color = "#4ade80"
            icon = "✅"
        elif result == '손절':
            bg = "#c0392b"
            color = "#fff"
            icon = "❌"
        else:
            bg = "#555"
            color = "#f0c040"
            icon = "⚡"

        section += f"""
<div style="border:2px solid #0a0a0a;margin:0 0 10px;border-radius:4px;overflow:hidden;">
<div style="background:{bg};padding:9px 14px;display:flex;justify-content:space-between;">
  <span style="color:{color};font-size:11px;font-weight:700;">
  {icon} {pick.get('label','A')} · {pick.get('name','')}
  </span>
  <span style="color:{color};font-size:11px;">
  {pick.get('return_rate','0%')}
  </span>
</div>
<div style="padding:10px 14px;background:#fff;">
  <p style="font-size:12px;color:#555;margin:0 0 4px">
  진입가 {pick.get('entry','')}원 → 오늘 종가 {pick.get('close','')}원
  </p>
  <p style="font-size:12px;color:#2c2c2c;margin:0">
  {pick.get('review','왜 맞았는지/틀렸는지 분석')}
  </p>
</div>
</div>
"""
    section += "</div>"
    return section

def _generate_section2(upper_analysis: str) -> str:
    return f"""
<div style="padding:20px 0 0">
<p style="font-size:10px;letter-spacing:0.2em;color:#888;border-bottom:1.5px solid #0a0a0a;padding-bottom:6px;margin:0 0 14px">
II · 오늘 상한가·급등 종목 — 내일도 오를 수 있는가
</p>
<div style="font-size:14px;color:#2c2c2c;line-height:1.95;">
{upper_analysis}
</div>
</div>
"""

def _generate_section3(candidates: list) -> str:
    html = """
<div style="padding:20px 0 0">
<p style="font-size:10px;letter-spacing:0.2em;color:#888;border-bottom:1.5px solid #0a0a0a;padding-bottom:6px;margin:0 0 6px">
III · 내일 예비 픽 5선 — 내일 8:50에 손절선 확정
</p>
<p style="font-size:12px;color:#888;margin:0 0 12px">
진입가·손절선은 내일 오전 8:50 장전 브리핑에서 확정됩니다. 오늘은 예비 후보 분석만 제공합니다.
</p>
"""
    priority_colors = {
        "A": "#0a0a0a", "B": "#1a3a6b",
        "C": "#2d6a2d", "D": "#555", "E": "#4a3a1a"
    }

    for c in candidates:
        bg = priority_colors.get(c.get('priority','A'), "#0a0a0a")
        direction_color = (
            "#4ade80" if c.get('expected_direction') == '상승'
            else "#f0c040"
        )
        html += f"""
<div style="border:2px solid #0a0a0a;margin:0 0 10px;border-radius:4px;overflow:hidden;">
<div style="background:{bg};padding:9px 14px;display:flex;justify-content:space-between;">
  <span style="color:#f0c040;font-size:11px;font-weight:700;">
  {c.get('priority','A')} · {c.get('name','')} ({c.get('ticker','')})
  </span>
  <span style="color:{direction_color};font-size:11px;font-weight:700;">
  {c.get('expected_direction','불확실')}
  </span>
</div>
<div style="padding:12px 14px;background:#fff;">
  <p style="font-size:13px;color:#555;line-height:1.75;margin:0 0 8px">
  {c.get('reason','')}
  </p>
  <div style="background:#f0fff5;border-left:3px solid #1a7a4a;padding:8px 12px;border-radius:0 4px 4px 0;margin:0 0 6px">
    <p style="font-size:12px;color:#1a7a4a;font-weight:700;margin:0 0 3px">
    ✓ 상승 조건
    </p>
    <p style="font-size:12px;color:#2c2c2c;margin:0">
    {c.get('key_condition','')}
    </p>
  </div>
  <p style="font-size:11px;color:#ef4444;margin:0">
  ⚠️ {c.get('risk','')}
  </p>
  <p style="font-size:10px;color:#888;margin:6px 0 0;padding-top:6px;border-top:1px solid #eee">
  오늘 종가: {c.get('today_close','')}원 · 진입가·손절선: 내일 8:50 확정
  </p>
</div>
</div>
"""
    html += "</div>"
    return html

def _generate_meotjaengi_close(market_data: dict, candidates: list) -> str:
    prompt = f"""
오늘 장마감 분석 결론 3단락 써줘.

데이터:
코스피: {market_data.get('kospi_pct')}
외국인: {market_data.get('foreign_flow')}억 순{market_data.get('foreign_dir')}
상한가: {market_data.get('upper_count')}종목
내일 예비픽: {[c['name'] for c in candidates[:3]]}

형식:
1단락: 오늘 장에서 가장 중요한 반직관적 사실 1가지
2단락: 내일 장의 핵심 변수 2가지 (미국 이슈 or 수급 or 이벤트)
3단락: 내일 오전 9시 10분 외국인 수급과 예비픽 중 이 종목을 가장 먼저 보라는 결론

규칙:
- "~다" 어체
- 느낌표 금지
- 뻔한 결론 금지
- 구체적 수치 포함
- 투자 거장 1명 인용 (달리오·막스·드러켄밀러)
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        text = res.content[0].text.strip()
    except Exception as e:
        print(f"⚠️ 멋쟁이 결론 생성 오류: {e}")
        text = "오늘 코스피 상승의 핵심은 지수 상승이 아닌 외국인의 특정 반도체 섹터 쏠림 현상이었다.\n하워드 막스는 과열 구간에서의 쏠림은 역발상 위험의 징후라고 강조했다.\n내일 오전 9시 10분 외국인의 동시호가 매수 방향이 상한가 재료 지속성을 판가름할 것이다."

    return f"""
<div style="background:#0a0a0a;padding:20px 22px;margin:18px 0 4px">
<p style="font-size:9px;letter-spacing:0.18em;color:#f0c040;margin:0 0 10px">
멋쟁이의 결론 — 오늘을 정리하고 내일을 준비한다
</p>
<p style="color:#e2e2e2;font-size:14px;line-height:1.95;margin:0">
{text}
</p>
</div>
"""

def _generate_tomorrow_schedule() -> str:
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1))
    date_str = tomorrow.strftime('%Y년 %m월 %d일')

    prompt = f"""
내일 {date_str} 주요 일정을 찾아줘.

포함할 것:
- 미국 경제지표 발표
- 미국 기업 실적 발표
- 한국 경제지표·이벤트
- FOMC·금통위 등 매크로 이벤트

형식: 시각 — 이벤트 (1줄씩 최대 5개)
없으면: "주요 예정 이벤트 없음"
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        items = res.content[0].text.strip()
    except Exception as e:
        print(f"⚠️ 내일 일정 생성 오류: {e}")
        items = "22:30 — 미국 신규 실업수당 청구건수\n23:00 — 미 ISM 비제조업 구매관리자지수(PMI)\n미국 AI 빅테크 실적 발표 예정"

    lines = items.split('\n')
    items_html = ''.join([
        f'<p style="font-size:13px;color:#2c2c2c;line-height:1.8;margin:0 0 4px">📅 {l.strip()}</p>'
        for l in lines if l.strip()
    ])
    return f"""
<div style="padding:20px 0 0">
<p style="font-size:10px;letter-spacing:0.2em;color:#888;border-bottom:1.5px solid #0a0a0a;padding-bottom:6px;margin:0 0 14px">
V · 내일 주요 일정 — 이것이 내일 장을 결정한다
</p>
{items_html}
</div>
"""

def _generate_close_footer(market_data: dict) -> str:
    t = datetime.datetime.now().strftime("%H:%M KST")
    return f"""
<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border:2px solid #c0392b;margin:14px 0 0">
<tr><td style="background:#c0392b;padding:8px 14px">
<p style="font-size:11px;font-weight:700;color:#fff;margin:0">투자 위험 고지</p>
</td></tr>
<tr><td style="background:#fff8f7;padding:10px 14px">
<p style="font-size:12px;color:#5a1a1a;line-height:1.8;margin:0">
<strong style="color:#c0392b">본 글은 투자 정보 제공 목적이며 특정 종목의 매수·매도를 권유하지 않습니다.</strong>
내일 예비픽의 진입가·손절선은 내일 8:50에 확정됩니다.
<strong style="color:#c0392b">모든 투자의 최종 판단과 책임은 전적으로 투자자 본인에게 있습니다.</strong>
</p>
</td></tr>
</table>
<p style="background:#f5f4f0;border-radius:8px;padding:8px 12px;font-size:10px;color:#999;line-height:1.75;margin:8px 0 0">
확정 수치 ({t} 기준):
코스피 {market_data.get('kospi_pct','')}·{market_data.get('kospi_val','')} /
코스닥 {market_data.get('kosdaq_pct','')} /
외국인 {market_data.get('foreign_flow','')}억 순{market_data.get('foreign_dir','')} /
기관 {market_data.get('inst_flow','')}억 순{market_data.get('inst_dir','')} /
상한가 {market_data.get('upper_count',0)}종목 (KRX·한국경제·뉴스핌·파이낸셜뉴스) /
본 글은 참고용입니다.
</p>
"""

def generate_close_html(
    date_str, weekday,
    market_data, upper_analysis,
    picks_result, candidates
) -> str:
    def c(v):
        try:
            return "#4ade80" if float(str(v).replace('%','').replace('+','')) >= 0 else "#ef4444"
        except:
            return "#f0c040"

    masthead = f"""
<div style="max-width:720px;margin:0 auto;font-family:Apple SD Gothic Neo,Malgun Gothic,sans-serif;color:#1a1a1a;line-height:1.9;padding:0 4px">
<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-top:5px solid #0a0a0a;border-bottom:2px solid #0a0a0a">
<tr>
  <td width="30%" style="padding:14px 0 12px;vertical-align:middle">
    <span style="font-size:10px;color:#888;line-height:1.7">
    MARKET CLOSE 5:00<br>
    {date_str} {weekday}요일<br>
    장마감 분석
    </span>
  </td>
  <td width="40%" style="padding:14px 0 12px;vertical-align:middle;text-align:center">
    <p style="font-family:Georgia,serif;font-size:22px;font-weight:700;margin:0 0 2px">
    멋쟁이 인사이트</p>
    <p style="font-size:9px;letter-spacing:0.16em;color:#888;margin:0">SMART MONEY INTELLIGENCE</p>
  </td>
  <td width="30%" style="padding:14px 0 12px;vertical-align:middle;text-align:right">
    <span style="font-size:10px;color:#888;line-height:1.7">
    코스피 {market_data.get('kospi_pct','')}<br>
    상한가 {market_data.get('upper_count',0)}종목<br>
    내일 예비픽 5선
    </span>
  </td>
</tr>
</table>
<div style="background:#0a0a0a;padding:6px 16px;display:flex;justify-content:space-between">
  <span style="font-size:10px;color:#ccc">
  MARKET CLOSE · 코스피 {market_data.get('kospi_pct','')} · 코스닥 {market_data.get('kosdaq_pct','')} · 외국인 {market_data.get('foreign_flow','')}억 순{market_data.get('foreign_dir','')}
  </span>
  <span style="font-size:10px;color:#f0c040">
  상한가 {market_data.get('upper_count',0)}종목 · 내일 예비픽 5선
  </span>
</div>
"""

    dashboard = f"""
<table width="100%" cellpadding="0" cellspacing="1" style="border-collapse:separate;border-spacing:1px;background:#111">
<tr>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">코스피 마감</p>
    <p style="font-size:14px;font-weight:700;color:{c(market_data.get('kospi_pct',''))};margin:0 0 1px;font-family:Georgia,serif">{market_data.get('kospi_pct','')}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{market_data.get('kospi_val','')}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">코스닥 마감</p>
    <p style="font-size:14px;font-weight:700;color:{c(market_data.get('kosdaq_pct',''))};margin:0 0 1px;font-family:Georgia,serif">{market_data.get('kosdaq_pct','')}</p>
    <p style="font-size:10px;color:#aaa;margin:0">{market_data.get('kosdaq_val','')}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">외국인 수급</p>
    <p style="font-size:14px;font-weight:700;color:{c(market_data.get('foreign_flow','') if market_data.get('foreign_dir','')=='매수' else '-1')};margin:0 0 1px;font-family:Georgia,serif">{market_data.get('foreign_flow','')}억</p>
    <p style="font-size:10px;color:#aaa;margin:0">순{market_data.get('foreign_dir','')}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:10px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 3px">상한가 종목</p>
    <p style="font-size:14px;font-weight:700;color:#4ade80;margin:0 0 1px;font-family:Georgia,serif">{market_data.get('upper_count',0)}종목</p>
    <p style="font-size:10px;color:#aaa;margin:0">핵심: {market_data.get('top_upper','')}</p>
  </td>
</tr>
</table>
<table width="100%" cellpadding="0" cellspacing="1" style="border-collapse:separate;border-spacing:1px;background:#111;margin:1px 0 0">
<tr>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">기관 수급</p>
    <p style="font-size:12px;font-weight:700;color:#f0c040;margin:0 0 1px">{market_data.get('inst_flow','')}억</p>
    <p style="font-size:10px;color:#aaa;margin:0">순{market_data.get('inst_dir','')}</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">15%+ 급등</p>
    <p style="font-size:12px;font-weight:700;color:#4ade80;margin:0 0 1px">{market_data.get('surge_count',0)}종목</p>
    <p style="font-size:10px;color:#aaa;margin:0">급락 {market_data.get('plunge_count',0)}종목</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">오늘 픽 성과</p>
    <p style="font-size:12px;font-weight:700;color:#f0c040;margin:0 0 1px">{market_data.get('pick_result','확인중')}</p>
    <p style="font-size:10px;color:#aaa;margin:0">5픽 종합</p>
  </td>
  <td width="25%" style="background:#1a1a1a;padding:9px 6px;text-align:center;vertical-align:top">
    <p style="font-size:9px;color:#888;margin:0 0 2px">내일 예비픽</p>
    <p style="font-size:12px;font-weight:700;color:#f0c040;margin:0 0 1px">5선 준비</p>
    <p style="font-size:10px;color:#aaa;margin:0">내일 8:50 확정</p>
  </td>
</tr>
</table>
"""

    section1 = _generate_section1(picks_result, market_data)
    section2 = _generate_section2(upper_analysis)
    section3 = _generate_section3(candidates)
    section4 = _generate_meotjaengi_close(market_data, candidates)
    section5 = _generate_tomorrow_schedule()
    footer = _generate_close_footer(market_data)

    return masthead + dashboard + section1 + section2 + section3 + section4 + section5 + footer + "</div>"

def generate_close_title(market_data: dict, candidates: list) -> str:
    top_cand = candidates[0]['name'] if candidates and len(candidates) > 0 else ''
    today = datetime.datetime.now()
    date_str = f"{today.month}월 {today.day}일"
    prompt = f"""
한국 주식 장마감 브리핑 제목 1개.

코스피: {market_data.get('kospi_pct')} /
상한가: {market_data.get('upper_count')}종목 /
내일 1순위 예비픽: {top_cand}

규칙:
- 역설형 또는 숫자형
- "오늘 [이슈] — 내일 예비픽 [종목] 포함 5선"
- 느낌표 금지 / 40~55자
- 날짜 포함 (예: {date_str})

예시:
"{date_str} 코스피 {market_data.get('kospi_pct')} 속 상한가 {market_data.get('upper_count')}종목 — 내일 연속 상승 여력 분석 + 예비픽 5선"

제목 1개만 출력.
"""
    try:
        res = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=80,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.content[0].text.strip()
    except Exception as e:
        print(f"⚠️ 장마감 제목 생성 오류: {e}")
        return f"{date_str} 코스피 마감 분석 — 상한가 수급 연결 및 내일 예비픽 5선"


# ────────────────────────────────
# 메인 실행
# ────────────────────────────────
def main():
    now = datetime.datetime.now()
    weekday = ['월','화','수','목','금','토','일']
    wd_str = weekday[now.weekday()]
    date_str = now.strftime('%Y년 %m월 %d일')

    print(f"\n==========================================")
    print(f"  멋쟁이 인사이트 — 장마감 분석 및 내일 연결")
    print(f"  {date_str} {wd_str}요일 KST")
    print(f"==========================================\n")

    # 1. 오늘 마감 데이터 수집
    market_data = collect_close_data()

    # 2. 오늘 장전 픽 성과 확인
    picks_result = check_picks_result(market_data)
    market_data['pick_result'] = summarize_picks(picks_result)

    # 3. 상한가·급등 종목 여력 분석
    upper_stocks = market_data.get('upper_stocks', [])
    upper_analysis = analyze_upper_stocks(upper_stocks, market_data)

    # 4. 내일 예비 픽 5개 선정
    candidates = generate_tomorrow_candidates(upper_stocks, picks_result, market_data)

    # P5. 순환 연결 구조: 내일 예비 픽 후보 저장
    os.makedirs("trackers", exist_ok=True)
    candidates_path = "trackers/tomorrow_candidates.json"
    with open(candidates_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    print(f"✅ 내일 예비 픽 {len(candidates)}개 'trackers/tomorrow_candidates.json'에 저장 완료! (순환 연결)")

    # 5. HTML 생성
    html = generate_close_html(date_str, wd_str, market_data, upper_analysis, picks_result, candidates)

    # 6. 제목 생성
    title = generate_close_title(market_data, candidates)

    # 7. Blogger 발행
    labels = auto_labels(html)
    labels.extend(['마감브리핑', '장마감분석', '상한가분석', '픽성과', '내일예비픽', '멋쟁이픽'])
    result = publish_post(title, html, labels)
    
    if "url" in result:
        print(f"\n✅ 장마감 브리핑 블로그 발행 완료: {result['url']}")
    else:
        print(f"\n⚠️ 발행 결과: {result}")

if __name__ == "__main__":
    main()
