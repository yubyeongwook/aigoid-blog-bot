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
        kst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
        date_str = kst_now.strftime("%Y-%m-%d")

    history = load_history()

    history[date_str] = {
        "date": date_str,
        "picks": picks,
        "updated_at": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).isoformat()
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
    kst_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
    today = kst_now.strftime("%Y-%m-%d")
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
    return ""
