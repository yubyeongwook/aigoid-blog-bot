"""
pick_tracker.py — 픽 성과 추적 시스템
매일 장 마감 후 자동으로 지난 픽 성과 업데이트
누적 승률·평균 수익률 자동 계산
"""
import os, json, datetime, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

TRACKER_FILE = Path(__file__).parent / "picks_history.json"
KIS_APP_KEY = os.getenv("KIS_APP_KEY", "")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET", "")

# ────────────────────────────────
# 픽 저장
# ────────────────────────────────
def save_picks(picks: list, date_str: str = None):
    if not date_str:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    history = load_history()

    history[date_str] = {
        "date": date_str,
        "picks": picks,
        "updated_at": datetime.datetime.now().isoformat()
    }

    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"✅ 픽 저장 완료: {len(picks)}개")

def load_history() -> dict:
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ────────────────────────────────
# KIS 현재가 조회
# ────────────────────────────────
def get_current_price(ticker: str) -> float:
    try:
        url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": KIS_APP_KEY,
            "appsecret": KIS_APP_SECRET
        }
        token_res = requests.post(url, json=body, timeout=10)
        token = token_res.json().get("access_token", "")
        if not token:
            return 0.0

        price_url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "authorization": f"Bearer {token}",
            "appkey": KIS_APP_KEY,
            "appsecret": KIS_APP_SECRET,
            "tr_id": "FHKST01010100"
        }
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": ticker}
        res = requests.get(price_url, headers=headers, params=params, timeout=10)
        output = res.json().get("output", {})
        return float(output.get("stck_prpr", 0))
    except:
        return 0.0

# ────────────────────────────────
# 픽 성과 업데이트
# ────────────────────────────────
def update_performance():
    history = load_history()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    updated = 0

    for date_str, data in history.items():
        for pick in data.get("picks", []):
            ticker = pick.get("ticker", "")
            if not ticker:
                continue

            entry = pick.get("entry_price", 0)
            stop = pick.get("stop_loss", 0)
            target1 = pick.get("target_1", 0)
            target2 = pick.get("target_2", 0)

            if not entry:
                continue

            current = get_current_price(ticker)
            if not current:
                continue

            pct = round((current - entry) / entry * 100, 2)
            pick["current_price"] = current
            pick["current_pct"] = pct
            pick["last_updated"] = today

            # 상태 판단
            if stop and current <= stop:
                pick["status"] = "손절"
                pick["result_pct"] = round((stop - entry) / entry * 100, 2)
            elif target2 and current >= target2:
                pick["status"] = "목표2달성"
                pick["result_pct"] = round((target2 - entry) / entry * 100, 2)
            elif target1 and current >= target1:
                pick["status"] = "목표1달성"
                pick["result_pct"] = round((target1 - entry) / entry * 100, 2)
            else:
                pick["status"] = "진행중"
                pick["result_pct"] = pct

            updated += 1

    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"✅ 성과 업데이트: {updated}개")
    return history

# ────────────────────────────────
# 누적 통계 계산
# ────────────────────────────────
def calculate_stats() -> dict:
    history = load_history()
    all_picks = []

    for date_str, data in history.items():
        for pick in data.get("picks", []):
            if pick.get("status") in ["손절", "목표1달성", "목표2달성"]:
                all_picks.append(pick)

    if not all_picks:
        return {
            "total": 0, "win": 0, "lose": 0,
            "win_rate": 0, "avg_return": 0,
            "best": None, "worst": None
        }

    wins = [p for p in all_picks if p["status"] in ["목표1달성", "목표2달성"]]
    losses = [p for p in all_picks if p["status"] == "손절"]
    returns = [p.get("result_pct", 0) for p in all_picks]

    return {
        "total": len(all_picks),
        "win": len(wins),
        "lose": len(losses),
        "win_rate": round(len(wins) / len(all_picks) * 100, 1),
        "avg_return": round(sum(returns) / len(returns), 2),
        "best": max(all_picks, key=lambda x: x.get("result_pct", 0)),
        "worst": min(all_picks, key=lambda x: x.get("result_pct", 0))
    }

# ────────────────────────────────
# 성과 블록 HTML 생성 (블로그 상단 표시용)
# ────────────────────────────────
def generate_performance_html() -> str:
    stats = calculate_stats()
    history = load_history()

    # 최근 7일 픽
    recent = []
    dates = sorted(history.keys(), reverse=True)[:7]
    for d in dates:
        for p in history[d].get("picks", []):
            recent.append({**p, "pick_date": d})

    win_color = "#4ade80" if stats["win_rate"] >= 60 else "#f0c040" if stats["win_rate"] >= 50 else "#ef4444"

    recent_rows = ""
    for p in recent[:8]:
        status = p.get("status", "진행중")
        pct = p.get("result_pct", p.get("current_pct", 0))
        color = "#4ade80" if pct > 0 else "#ef4444"
        status_color = {
            "목표1달성": "#4ade80",
            "목표2달성": "#4ade80",
            "손절": "#ef4444",
            "진행중": "#f0c040"
        }.get(status, "#888")

        recent_rows += f"""
<tr style="border-bottom:1px solid #1a1a1a;">
  <td style="padding:7px 10px;font-size:12px;color:#ccc;">{p.get("pick_date","")}</td>
  <td style="padding:7px 10px;font-size:12px;font-weight:600;color:#f0f0f0;">{p.get("name","")}</td>
  <td style="padding:7px 10px;font-size:11px;color:#888;">{p.get("type","")}</td>
  <td style="padding:7px 10px;font-size:12px;color:{color};font-weight:700;">{"+"+str(pct)+"%" if pct>0 else str(pct)+"%"}</td>
  <td style="padding:7px 10px;"><span style="background:{status_color};color:#000;font-size:10px;padding:2px 6px;border-radius:2px;font-weight:700;">{status}</span></td>
</tr>"""

    html = f"""
<div style="background:#0a0a0a;border:1px solid #222;margin:0 0 24px;font-family:Apple SD Gothic Neo,sans-serif;">
  <div style="padding:14px 20px;border-bottom:1px solid #1a1a1a;display:flex;justify-content:space-between;align-items:center;">
    <div>
      <span style="font-family:Georgia,serif;font-size:16px;font-weight:700;color:#f0f0f0;">멋쟁이 픽 누적 성과</span>
      <span style="font-size:10px;color:#555;margin-left:10px;font-family:monospace;">LIVE TRACK RECORD</span>
    </div>
    <span style="font-size:10px;color:#555;font-family:monospace;">업데이트: {datetime.datetime.now().strftime("%Y.%m.%d")}</span>
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:#1a1a1a;">
    <div style="background:#0a0a0a;padding:16px;text-align:center;">
      <div style="font-size:9px;color:#555;font-family:monospace;margin-bottom:4px;">누적 승률</div>
      <div style="font-size:28px;font-weight:700;color:{win_color};font-family:Georgia,serif;">{stats["win_rate"]}%</div>
      <div style="font-size:10px;color:#555;">{stats["win"]}승 {stats["lose"]}패</div>
    </div>
    <div style="background:#0a0a0a;padding:16px;text-align:center;">
      <div style="font-size:9px;color:#555;font-family:monospace;margin-bottom:4px;">평균 수익률</div>
      <div style="font-size:28px;font-weight:700;color:#4ade80;font-family:Georgia,serif;">+{stats["avg_return"]}%</div>
      <div style="font-size:10px;color:#555;">완료 픽 기준</div>
    </div>
    <div style="background:#0a0a0a;padding:16px;text-align:center;">
      <div style="font-size:9px;color:#555;font-family:monospace;margin-bottom:4px;">총 픽 수</div>
      <div style="font-size:28px;font-weight:700;color:#f0f0f0;font-family:Georgia,serif;">{stats["total"]}</div>
      <div style="font-size:10px;color:#555;">단타·스윙·중기</div>
    </div>
    <div style="background:#0a0a0a;padding:16px;text-align:center;">
      <div style="font-size:9px;color:#555;font-family:monospace;margin-bottom:4px;">최고 수익</div>
      <div style="font-size:28px;font-weight:700;color:#4ade80;font-family:Georgia,serif;">+{stats["best"]["result_pct"] if stats["best"] else 0}%</div>
      <div style="font-size:10px;color:#555;">{stats["best"]["name"] if stats["best"] else "-"}</div>
    </div>
  </div>
  <div style="padding:0;">
    <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
      <thead>
        <tr style="background:#111;">
          <th style="padding:8px 10px;font-size:10px;color:#555;text-align:left;font-family:monospace;">날짜</th>
          <th style="padding:8px 10px;font-size:10px;color:#555;text-align:left;font-family:monospace;">종목</th>
          <th style="padding:8px 10px;font-size:10px;color:#555;text-align:left;font-family:monospace;">유형</th>
          <th style="padding:8px 10px;font-size:10px;color:#555;text-align:left;font-family:monospace;">수익률</th>
          <th style="padding:8px 10px;font-size:10px;color:#555;text-align:left;font-family:monospace;">상태</th>
        </tr>
      </thead>
      <tbody>
        {recent_rows}
      </tbody>
    </table>
  </div>
  <div style="padding:8px 16px;border-top:1px solid #1a1a1a;">
    <p style="font-size:10px;color:#333;margin:0;">⚠️ 과거 성과가 미래 수익을 보장하지 않습니다. 모든 투자 책임은 본인에게 있습니다.</p>
  </div>
</div>"""
    return html
