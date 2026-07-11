import os, requests, json

KAKAO_TOKEN = os.getenv("KAKAO_ACCESS_TOKEN", "")

def send_kakao_message(picks: list, blog_url: str, performance: dict = None) -> bool:
    if not KAKAO_TOKEN:
        print("KAKAO_ACCESS_TOKEN 없음")
        return False

    pick_lines = ""
    for i, p in enumerate(picks[:3]):
        emoji = ["🎯", "📈", "💡"][i] if i < 3 else "•"
        ptype = p.get("type", "")
        name = p.get("name", "")
        entry = p.get("entry_price", 0)
        stop = p.get("stop_loss", 0)
        target = p.get("target_1", 0)
        pick_lines += f"\n{emoji} {ptype}: {name}"
        if entry:
            pick_lines += f"\n   진입 {entry:,} / 손절 {stop:,} / 목표 {target:,}"

    perf_line = ""
    if performance:
        wr = performance.get("win_rate", 0)
        avg = performance.get("avg_return", 0)
        perf_line = f"\n\n📊 누적 승률 {wr}% | 평균 수익 +{avg}%"

    text = f"""멋쟁이 인사이트 — 오늘의 픽
{'='*30}{pick_lines}{perf_line}

🔗 전체 분석: {blog_url}

⚠️ 투자 책임은 본인에게 있습니다"""

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {KAKAO_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    template = {
        "object_type": "text",
        "text": text,
        "link": {"web_url": blog_url, "mobile_web_url": blog_url}
    }
    try:
        res = requests.post(url, headers=headers,
            data={"template_object": json.dumps(template)})
        if res.status_code == 200:
            print("✅ 카카오톡 알림 전송 완료")
            return True
        print(f"카카오톡 오류: {res.text}")
        return False
    except Exception as e:
        print(f"카카오톡 예외: {e}")
        return False

def send_telegram_message(picks: list, blog_url: str, performance: dict = None) -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "")
    if not bot_token or not chat_id:
        print("텔레그램 설정 없음")
        return False

    pick_lines = ""
    for i, p in enumerate(picks[:4]):
        emoji = ["🎯", "📈", "💡", "🔄"][i] if i < 4 else "•"
        name = p.get("name", "")
        ptype = p.get("type", "")
        entry = p.get("entry_price", 0)
        stop = p.get("stop_loss", 0)
        target = p.get("target_1", 0)
        pick_lines += f"\n{emoji} *{ptype}*: {name}"
        if entry:
            pick_lines += f"\n   진입 `{entry:,}` | 손절 `{stop:,}` | 목표 `{target:,}`"

    perf_line = ""
    if performance and performance.get("total", 0) > 0:
        wr = performance.get("win_rate", 0)
        avg = performance.get("avg_return", 0)
        total = performance.get("total", 0)
        color = "🟢" if wr >= 60 else "🟡" if wr >= 50 else "🔴"
        perf_line = f"\n\n{color} *누적 성과* {total}픽 | 승률 {wr}% | 평균 +{avg}%"

    text = f"""*멋쟁이 인사이트* — 오늘의 분석
━━━━━━━━━━━━━━━━━━{pick_lines}{perf_line}

[📊 전체 분석 보기]({blog_url})

_⚠️ 투자 책임은 본인에게 있습니다_
_본 정보는 투자 참고용이며 특정 종목의 매수·매도를 권유하지 않습니다._"""

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        res = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }, timeout=10)
        if res.status_code == 200:
            print("✅ 텔레그램 알림 전송 완료")
            
            if channel_id:
                try:
                    requests.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={
                            "chat_id": channel_id,
                            "text": text,
                            "parse_mode": "Markdown"
                        },
                        timeout=10
                    )
                    print("✅ 텔레그램 채널 전송 완료")
                except Exception as e:
                    print(f"채널 전송 오류: {e}")
            
            return True
        print(f"텔레그램 오류: {res.text}")
        return False
    except Exception as e:
        print(f"텔레그램 예외: {e}")
        return False
