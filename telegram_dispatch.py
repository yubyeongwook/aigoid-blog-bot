"""
telegram_dispatch.py
텔레그램 명령어를 받아 GitHub Actions workflow_dispatch를 트리거합니다.
GitHub Actions에서 5분마다 실행됩니다.
"""
import os
import sys
import requests
from datetime import datetime, timezone, timedelta
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass



BOT_TOKEN      = os.getenv("TELEGRAM_BOT_TOKEN", "")

ALLOWED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "5003319374"))
GH_PAT         = os.getenv("GH_DISPATCH_TOKEN", "")   # workflow 권한 있는 PAT
REPO           = os.getenv("GITHUB_REPOSITORY", "yubyeongwook/aigoid-blog-bot")

# 명령어 → (workflow 파일명, 라벨)
WORKFLOW_MAP = {
    "/run_morning":   ("daily.yml",       "오전 7시 아침 브리핑"),
    "/run_premarket": ("premarket.yml",   "오전 8시 50분 동시호가"),
    "/run_afternoon": ("daily_close.yml", "오후 5시 마감 브리핑"),
    "/run_trending":  ("trending.yml",    "트렌드 키워드"),
    "/run_weekly":    ("weekly.yml",      "주간 결산 리포트"),
}

HELP_TEXT = (
    "🤖 *멋쟁이 인사이트 컨트롤러*\n\n"
    "📌 사용 가능한 명령어:\n"
    "• `/run_morning` — 오전 7시 아침 브리핑 즉시 발행\n"
    "• `/run_premarket` — 오전 8:50 동시호가 브리핑 즉시 발행\n"
    "• `/run_afternoon` — 오후 5시 마감 브리핑 즉시 발행\n"
    "• `/run_trending` — 트렌드 키워드 즉시 발행\n"
    "• `/run_weekly` — 주간 결산 즉시 발행\n\n"
    "⏱ 명령 후 약 5~7분 내 블로그에 게시됩니다."
)


def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception as e:
        print(f"[Telegram] 메시지 전송 실패: {e}")


def trigger_workflow(workflow_file: str) -> bool:
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/{workflow_file}/dispatches"
    headers = {
        "Authorization": f"token {GH_PAT}",
        "Accept": "application/vnd.github.v3+json",
    }
    try:
        res = requests.post(url, json={"ref": "master"}, headers=headers, timeout=15)
        print(f"[GitHub] {workflow_file} 트리거 → {res.status_code}")
        return res.status_code == 204
    except Exception as e:
        print(f"[GitHub] 트리거 실패: {e}")
        return False


def main():
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN 없음 — 종료")
        return
    if not GH_PAT:
        print("GH_DISPATCH_TOKEN 없음 — 종료")
        return

    # 최근 6분 이내 메시지만 처리 (5분 주기 실행 기준, 여유 1분)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=6)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url, params={"timeout": 0, "limit": 100}, timeout=15)
    except Exception as e:
        print(f"[Telegram] getUpdates 실패: {e}")
        return

    if res.status_code != 200:
        print(f"[Telegram] API 오류: {res.status_code} — {res.text[:200]}")
        return

    updates = res.json().get("result", [])
    print(f"[Telegram] 업데이트 {len(updates)}건 수신")

    processed = set()

    for u in updates:
        message = u.get("message", {})
        if not message:
            continue
        chat_id  = message.get("chat", {}).get("id")
        if not chat_id:
            continue
        msg_text = str(message.get("text") or "").strip()
        if not msg_text:
            continue
        text     = msg_text.split()[0]  # 첫 단어만 (파라미터 무시)
        date     = message.get("date", 0)


        # 시간 필터
        msg_time = datetime.fromtimestamp(date, tz=timezone.utc)
        if msg_time < cutoff:
            continue

        # 권한 필터
        if chat_id != ALLOWED_CHAT_ID:
            print(f"[Telegram] 미인가 chat_id {chat_id} — 무시")
            continue

        # 중복 처리 방지
        update_id = u.get("update_id")
        if update_id in processed:
            continue
        processed.add(update_id)

        print(f"[Telegram] 명령어: {text!r}  (chat_id={chat_id})")

        if text in ("/start", "/help"):
            send_message(chat_id, HELP_TEXT)

        elif text in WORKFLOW_MAP:
            workflow_file, label = WORKFLOW_MAP[text]
            send_message(
                chat_id,
                f"🚀 *{label}* 강제 발행을 시작합니다\n"
                f"약 5~7분 후 블로그에서 확인하세요.",
            )
            ok = trigger_workflow(workflow_file)
            if not ok:
                send_message(chat_id, f"❌ GitHub Actions 트리거에 실패했습니다. 잠시 후 다시 시도해주세요.")

        else:
            send_message(chat_id, f"⚠️ 알 수 없는 명령어입니다.\n`/help` 로 명령어 목록 확인.")


if __name__ == "__main__":
    main()
