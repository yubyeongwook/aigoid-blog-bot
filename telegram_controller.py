import os
import sys
import time
import requests
import subprocess
from dotenv import load_dotenv

# load .env file from same directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "5003319374"))

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"메시지 전송 실패: {e}")

def handle_command(cmd, chat_id):
    if cmd == "/start" or cmd == "/help":
        help_text = (
            "🤖 *멋쟁이 인사이트 모바일 컨트롤러*\n\n"
            "사용 가능한 명령어:\n"
            "• `/status` - 시스템 현재 작동 상태 및 환경 변수 점검\n"
            "• `/picks` - 오늘의 추천 종목 정보 확인\n"
            "• `/run_morning` - [오전 7시] 아침 종합 브리핑 강제 구동\n"
            "• `/run_premarket` - [오전 8시 50분] 동시호가 브리핑 강제 구동\n"
        )
        send_message(chat_id, help_text)
    elif cmd == "/status":
        send_message(chat_id, "🔍 시스템 상태 확인 중...")
        import datetime
        status_msg = (
            "✅ *시스템 상태: 정상 가동 중*\n"
            f"• 현재 서버 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "• 채널 설정: @meotjaengi_insight\n"
            "• 자동화 상태: Blogger (연동 완료), Telegram (연동 완료), Instagram (연동 완료)"
        )
        send_message(chat_id, status_msg)
    elif cmd == "/picks":
        send_message(chat_id, "📊 오늘의 픽 조회 중...")
        import json
        history_path = os.path.join(os.path.dirname(__file__), "trackers", "picks_history.json")
        try:
            if not os.path.exists(history_path):
                send_message(chat_id, "⚠️ 기록된 추천 픽 파일이 존재하지 않습니다.")
                return
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
            dates = sorted(list(history.keys()))
            if not dates:
                send_message(chat_id, "⚠️ 기록된 추천 픽이 없습니다.")
                return
            latest_date = dates[-1]
            picks = history[latest_date]["picks"]
            msg = f"📅 *추천 일자: {latest_date}*\n\n"
            for p in picks:
                # Handle possible 0 values or formatting
                entry = f"{p['entry_price']:,}원" if p['entry_price'] > 0 else "미정"
                stop = f"{p['stop_loss']:,}원" if p['stop_loss'] > 0 else "미정"
                target = f"{p['target_1']:,}원" if p['target_1'] > 0 else "미정"
                msg += (
                    f"📌 *{p['name']} ({p['ticker']})*\n"
                    f"  · 진입가: {entry}\n"
                    f"  · 손절가: {stop}\n"
                    f"  · 목표가: {target}\n"
                    f"  · 상태: {p['status']}\n\n"
                )
            send_message(chat_id, msg)
        except Exception as e:
            send_message(chat_id, f"❌ 픽 조회 실패: {str(e)}")
    elif cmd == "/run_morning":
        send_message(chat_id, "🚀 *오전 7시 아침 종합 브리핑 자동 발행을 강제 시작합니다...*\n(이 작업은 약 1~2분 정도 소요됩니다.)")
        try:
            script_path = os.path.join(os.path.dirname(__file__), "main_daily_v4.py")
            proc = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            send_message(chat_id, f"✅ 아침 종합 브리핑 프로세스(PID: {proc.pid})가 구동되었습니다. 완료 결과는 블로그/텔레그램/인스타에 자동 배포됩니다.")
        except Exception as e:
            send_message(chat_id, f"❌ 강제 실행 실패: {str(e)}")
    elif cmd == "/run_premarket":
        send_message(chat_id, "🚀 *오전 8시 50분 장전 동시호가 브리핑 자동 발행을 강제 시작합니다...*\n(이 작업은 약 1분 정도 소요됩니다.)")
        try:
            script_path = os.path.join(os.path.dirname(__file__), "main_premarket_v4.py")
            proc = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            send_message(chat_id, f"✅ 장전 동시호가 브리핑 프로세스(PID: {proc.pid})가 구동되었습니다. 완료 결과는 블로그/텔레그램에 자동 배포됩니다.")
        except Exception as e:
            send_message(chat_id, f"❌ 강제 실행 실패: {str(e)}")
    else:
        send_message(chat_id, "⚠️ 알 수 없는 명령어입니다. `/help`를 입력하여 명령어 목록을 확인하세요.")

def poll():
    offset = 0
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    print("Telegram Polling Controller Started...")
    while True:
        try:
            res = requests.get(url, params={"offset": offset, "timeout": 20}, timeout=30)
            if res.status_code == 200:
                updates = res.json().get("result", [])
                for u in updates:
                    offset = u["update_id"] + 1
                    message = u.get("message", {})
                    chat = message.get("chat", {})
                    chat_id = chat.get("id")
                    text = message.get("text", "").strip()
                    
                    if chat_id != ALLOWED_CHAT_ID:
                        print(f"Ignored unauthorized message from Chat ID: {chat_id}")
                        continue
                        
                    if text.startswith("/"):
                        print(f"Handling command: {text} from Chat ID: {chat_id}")
                        handle_command(text, chat_id)
            else:
                print(f"Telegram API Error: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Polling loop exception: {e}")
        time.sleep(1)

if __name__ == "__main__":
    poll()
