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

def send_telegram_message(
    picks: list,
    blog_url: str,
    performance: dict = None,
    news_data: dict = None,
    macro_result: dict = None,
) -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "")
    if not bot_token or not chat_id:
        print("텔레그램 설정 없음")
        return False

    import re as _re

    # ─── 1. 핵심 매크로 인사이트 ──────────────────────────────
    macro_line = ""
    if macro_result:
        insight = macro_result.get("key_insight", "")
        if insight:
            # 150자 이내로 자르기
            insight = insight[:150] + ("…" if len(insight) > 150 else "")
            macro_line = f"\n\n💡 *오늘의 매크로 핵심*\n{insight}"

    # ─── 2. 오늘 주요 뉴스 헤드라인 (최대 4개) ────────────────
    news_lines = ""
    if news_data:
        headlines = []
        macro_news = news_data.get("macro_news", {})
        priority_keys = [
            "미국증시_마감", "연준_금리", "반도체_HBM",
            "미국증시_특징주", "이란_호르무즈", "코스피_외국인"
        ]
        for key in priority_keys:
            articles = macro_news.get(key, [])
            for a in articles:
                title = a.get("title", "")
                if title and not a.get("error"):
                    # HTML 태그 제거
                    title = _re.sub(r"<[^>]+>", "", title).strip()
                    if title not in headlines:
                        headlines.append(title)
                    if len(headlines) >= 4:
                        break
            if len(headlines) >= 4:
                break
        if headlines:
            news_lines = "\n\n📰 *오늘 주요 뉴스*"
            for h in headlines:
                news_lines += f"\n• {h}"

    # ─── 3. 오늘의 픽 ─────────────────────────────────────────
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

    # ─── 4. 누적 성과 ─────────────────────────────────────────
    perf_line = ""
    if performance and performance.get("total", 0) > 0:
        wr = performance.get("win_rate", 0)
        avg = performance.get("avg_return", 0)
        total = performance.get("total", 0)
        color = "🟢" if wr >= 60 else "🟡" if wr >= 50 else "🔴"
        perf_line = f"\n\n{color} *누적 성과* {total}픽 | 승률 {wr}% | 평균 +{avg}%"

    # ─── 최종 메시지 조합 ─────────────────────────────────────
    text = (
        f"*멋쟁이 인사이트* — 오늘의 분석\n"
        f"━━━━━━━━━━━━━━━━━━"
        f"{macro_line}"
        f"{news_lines}"
        f"\n\n🎯 *오늘의 픽*{pick_lines}"
        f"{perf_line}"
        f"\n\n[📊 전체 분석 보기]({blog_url})"
        f"\n\n_⚠️ 투자 책임은 본인에게 있습니다_"
        f"\n_본 정보는 투자 참고용이며 특정 종목의 매수·매도를 권유하지 않습니다._"
    )

    def _send(cid):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        res = requests.post(url, json={
            "chat_id": cid,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }, timeout=10)
        return res.status_code, res.text

    try:
        status, resp = _send(chat_id)
        if status == 200:
            print("✅ 텔레그램 알림 전송 완료")
        else:
            print(f"텔레그램 오류: {resp}")
            return False

        if channel_id:
            try:
                cs, cr = _send(channel_id)
                if cs == 200:
                    print("✅ 텔레그램 채널 전송 완료")
                else:
                    print(f"❌ 텔레그램 채널 전송 실패 ({cs}): {cr}")
            except Exception as e:
                print(f"채널 전송 예외: {e}")

        return True
    except Exception as e:
        print(f"텔레그램 예외: {e}")
        return False

