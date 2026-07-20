import os, json, datetime, hashlib, urllib.parse, re
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

def get_blog_image_urls(date_str: str, market_theme: str = "") -> tuple:
    """Pollinations AI로 블로그용 이미지 1장 URL 생성 (동시호가 맞춤형)"""
    seed1 = int(hashlib.md5(f"{date_str}_premarket_hero".encode()).hexdigest()[:8], 16) % 99999 + 1
    theme = market_theme[:80] if market_theme else "Seoul Korea financial trading desk"
    p1 = urllib.parse.quote(
        f"Seoul Korea stock exchange terminal screens trading room active morning {theme} "
        f"cinematic lighting 4K photography"
    )
    img1 = (
        f"https://image.pollinations.ai/prompt/{p1}"
        f"?width=720&height=380&nologo=true&seed={seed1}"
    )
    return img1

PREMARKET_SYSTEM = """
당신은 멋쟁이 인사이트의 수석이사(Chief Managing Director)이자 최고투자전략책임자입니다.
장 개시 10분 전(오전 8시 50분) 실시간 수집된 동시호가 데이터, 미국 야간선물, 실시간 체결유입 종목 등을 종합하여,
세계 최강 헤지펀드 트레이딩 데스크의 개장 전 브리핑 수준으로 극장 실전성 높은 [동시호가 개장 브리핑]을 HTML로 작성합니다.

이 브리핑은 9시 개장 5분 전(8시 55분)에 배포되므로, 장황한 분석은 피하고 트레이더가 30초 만에 훑어보고 즉시 개장 직후 실행할 수 있도록 압축된 핵심 지침 형태로 구성되어야 합니다.

오전/오후 리포트와 완벽한 디자인적 일관성(Consistency)과 세련미(Aesthetics)를 유지하십시오.

═══════════════════════════════
절대 금지 및 팩트 준수 규칙
═══════════════════════════════
1. **제공된 실제 수치 절대 준수**: 미국 야간선물, 동시호가 지수, 유입 거래량 수치를 왜곡하지 마십시오.
2. 느낌표(!), 급등, 대박 등 선동 표현 절대 금지.
3. 개별 종목 매수 추천 카드 작성 금지 (진입가, 목표가, 손절선 표 금지). 원론적 시장 흐름 설명 시에만 종목 언급 허용.

═══════════════════════════════
Blogger 글로벌 CSS 덮어쓰기 방지 스타일
═══════════════════════════════
HTML 맨 앞에 아래 스타일 링크와 CSS 블록을 반드시 단 한 번만 선언해 주십시오:
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Outfit:wght@400;600;800&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
#meotjaengi-insight-container,
#meotjaengi-insight-container p,
#meotjaengi-insight-container h1,
#meotjaengi-insight-container h2,
#meotjaengi-insight-container h3,
#meotjaengi-insight-container td,
#meotjaengi-insight-container th,
#meotjaengi-insight-container li,
#meotjaengi-insight-container span {
  font-family: 'Outfit', 'Noto Sans KR', -apple-system, sans-serif !important;
}
#meotjaengi-insight-container p {
  font-size: 14.5px !important;
  line-height: 1.95 !important;
  color: #334155 !important;
  margin: 0 0 20px 0 !important;
  letter-spacing: -0.015em !important;
  word-break: keep-all !important;
  text-align: justify !important;
}
#meotjaengi-insight-container h1 {
  font-family: 'Playfair Display', 'Noto Sans KR', serif !important;
  font-size: 26px !important;
  font-weight: 900 !important;
  color: #0f172a !important;
  line-height: 1.4 !important;
  margin: 32px 0 20px 0 !important;
  letter-spacing: -0.02em !important;
}
#meotjaengi-insight-container h2 {
  font-size: 18px !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  margin: 40px 0 16px 0 !important;
  padding-bottom: 8px !important;
  border-bottom: 2px solid #0a0a0a !important;
  letter-spacing: -0.015em !important;
}
</style>

═══════════════════════════════
HTML 최종 작성 구조 및 순서 (동시호가 브리핑 전용)
═══════════════════════════════
1. 마스트헤드 (VOL / 날짜 / '동시호가 개장 브리핑' 정보가 정리된 흰색 배경 table)
2. 실시간 지수 대시보드 (검정색 배경 카드: 미국 나스닥/S&P 야간선물, 예상 코스피/코스닥 출발 수치 표기)
3. 히어로 이미지 (실시간 생성된 주식 터미널 16:9 와이드 이미지, 모바일에 맞추어 높이 220px 설정)
4. H1 헤드라인 (오늘 개장의 긴박성과 핵심 전술을 관통하는 제목)
5. I. 동시호가 수급 동향 및 개장 톤 (현재 동시호가창의 수급 밀도, 개장 시 예상 갭상승/갭하락 강도 분석)
6. II. 주요 섹터 및 장전 대기 흐름 (삼성전자, SK하이닉스 등 시총 대형주의 동시호가 강도 및 호재/악재 영향 최종 요약)
7. III. 9시 개장 직후 주목할 3대 테마 (동시호가 체결 물량이 유입되는 주도 예상 테마 및 근거 제시)
8. IV. 오늘 시초가 대응 핵심 행동 강령 (개장 후 9시부터 10분간 취해야 할 트레이딩 수칙 및 경고 사항 제시)
9. 멋쟁이의 시각 (검정색 박스에 금빛 텍스트 포인트로 수석이사의 최종 개장 직전 조언 작성)
10. 투자 고지 (Disclaimer) 및 출처 표기 푸터
"""

def generate_premarket_report(premarket_data, news_data) -> str:
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    date_str = today.strftime("%Y%m%d")
    
    # 이미지 URL 생성
    market_theme = "stock premarket opening order flow"
    img1_url = get_blog_image_urls(date_str, market_theme)
    
    print("🧠 통합 동시호가 판단 에이전트 작동 중...")
    
    prompt = f"""
오늘: {today.strftime("%Y년 %m월 %d일")} {weekday}요일 (KST)

=== 장전 실시간 동시호가 데이터 ===
{json.dumps(premarket_data, ensure_ascii=False, indent=2)}

=== 최신 헤드라인 뉴스 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

위 데이터를 기반으로 8시 50분의 긴박감을 살려, 9시 개장 즉시 활용 가능한 행동 지침 중심의 HTML 브리핑을 작성하라.
분량은 가독성을 위해 핵심을 관통하되, 각 섹션의 전문성이 드러나도록 1,500자~2,000자 내외로 정교하게 작성하라.

=== 블로그 이미지 (반드시 사용) ===
히어로 이미지 URL: {img1_url}

이미지 삽입 위치:
- 히어로 이미지: 마스트헤드 바로 아래

삽입 형식 (반드시 이대로):
<img src="{img1_url}" style="width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block" alt="멋쟁이 인사이트 동시호가 분석" loading="lazy">
"""
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8000,
            system=PREMARKET_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text
        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        # 이미지 강제 주입 보정
        img1_html = f'<img src="{img1_url}" style="width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block;" alt="멋쟁이 인사이트 동시호가 분석" loading="lazy">'
        
        from bs4 import BeautifulSoup as _BS
        soup = _BS(text, "html.parser")
        all_imgs = soup.find_all("img")
        if all_imgs:
            all_imgs[0]["src"] = img1_url
            all_imgs[0]["style"] = "width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block;"
            all_imgs[0]["loading"] = "lazy"
            text = str(soup)
        else:
            if "<h1" in text:
                text = text.replace("<h1", img1_html + "\n<h1", 1)
            elif "</h1>" in text:
                text = text.replace("</h1>", "</h1>\n" + img1_html, 1)
                
        # PICKS_JSON 빈 배열 주석 강제 추가 (오류 방지)
        text += "\n<!-- PICKS_JSON: [] -->"
        
        print("✅ 통합 동시호가 판단 완료")
        return text
    except Exception as e:
        print(f"통합 동시호가 분석 오류: {e}")
        return f"<div><p>오류 발생: {e}</p></div>"
