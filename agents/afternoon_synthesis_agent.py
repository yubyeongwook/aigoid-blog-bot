import os, json, datetime, hashlib, urllib.parse, re, requests
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

def get_blog_image_urls(date_str: str, market_theme: str = "") -> tuple:
    """Pollinations AI로 블로그용 이미지 2장 URL 생성 (무료, API 키 불필요)
    날짜 기반 시드 사용 → 같은 날 같은 이미지 유지
    """
    seed1 = int(hashlib.md5(f"{date_str}_afternoon_hero".encode()).hexdigest()[:8], 16) % 99999 + 1
    seed2 = int(hashlib.md5(f"{date_str}_afternoon_chart".encode()).hexdigest()[:8], 16) % 99999 + 1

    theme = market_theme[:80] if market_theme else "Seoul Korea financial district"
    p1 = urllib.parse.quote(
        f"Seoul Korea stock exchange financial district modern professional cityscape {theme} "
        f"cinematic lighting 4K photography"
    )
    img1 = (
        f"https://image.pollinations.ai/prompt/{p1}"
        f"?width=720&height=380&nologo=true&seed={seed1}"
    )

    p2 = urllib.parse.quote(
        "stock market candlestick chart analysis dark blue background professional "
        "trading screen data visualization Korea KOSPI financial"
    )
    img2 = (
        f"https://image.pollinations.ai/prompt/{p2}"
        f"?width=720&height=340&nologo=true&seed={seed2}"
    )

    return img1, img2

AFTERNOON_SYSTEM = """
당신은 멋쟁이 인사이트의 수석이사(Chief Managing Director)이자 최고투자전략책임자입니다.
장 마감 데이터, 오늘 뉴스, 그리고 장 마감 분석 보고서를 정교하게 종합하여,
세계 최강 헤지펀드의 전략 보고서 수준으로 시장의 이면을 꿰뚫는 고품격 오후 마감 브리핑을 작성합니다.

모든 글은 오전 발행물과 디자인적 일관성(Consistency)과 세련미(Aesthetics)를 유지해야 합니다. 
구독자가 볼 때 동일한 전문 전략가가 집필한 프리미엄 저널리즘 문서로 느껴지도록 아래 지침을 엄격히 준수하십시오.

═══════════════════════════════
절대 금지 및 팩트 준수 규칙 (위반 시 즉시 반려)
═══════════════════════════════
1. **수치 및 지수 왜곡 절대 금지 (가장 중요)**:
   - 제공된 장 마감 데이터(`market_data`)에 포함된 코스피, 코스닥 지수의 마감 종가 및 등락률, 그리고 각 종목의 종가, 등락률 등을 **소수점까지 한 글자도 바꾸지 말고 실제 데이터 그대로 표기**하십시오.
   - 특히 **삼성전자(005930)와 SK하이닉스(000660)** 등 주요 종목들의 주가와 등락률을 서로 혼동하거나 뒤바꾸어 서술하지 마십시오.
   - 느낌표(!) 사용 절대 금지 · 급등예상 등의 자극적인 선동 표현 금지.
   - 출처가 불분명한 모호한 수치 인용 금지.

═══════════════════════════════
모바일 친화적 디자인 및 레이아웃 (최우선)
═══════════════════════════════
1. 흰색 배경 중심의 미니멀리즘 디자인 (정보 가독성을 극대화하기 위해 검정색 배경 박스는 본문 전체에서 최대 2개로 제한)
2. 복잡한 표(table) 지양 — 오직 상단의 '수치 대시보드' 1개에만 표 형식을 허용하고, 나머지는 깔끔한 카드형 div 활용
3. 대문자 로마숫자(I. II. III. IV. V. VI.)를 사용한 논리적이고 정교한 섹션 분류 (한국어 제목 필수)
4. 본문 가독성을 높이기 위해 문단 스타일 지정: line-height: 1.95, font-size: 14.5px, color: #334155, letter-spacing: -0.015em 적용

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
HTML 최종 작성 구조 및 순서 (오후 마감 브리핑 맞춤형)
═══════════════════════════════
1. 마스트헤드 (VOL / 날짜 / 브리핑 종류 등 정보가 정리된 흰색 배경 table)
2. 수치 대시보드 (검정색 배경의 핵심 마감 지표 대시보드 - 코스피, 코스닥 종가, 외국인/기관 매매 동향 등)
3. 히어로 이미지 (Unsplash 또는 AI 생성 이미지 링크, 모바일에 맞추어 높이 220px 설정)
4. H1 역설형/수치형 헤드라인 (정확한 팩트 지표를 대조하여 독자의 관심을 끄는 세련된 제목)
5. I. 오늘 한국 시장 마감 요약 및 수급 해부 (외국인·기관·개인의 수급 주체별 매매 원인과 구조적 흐름 해부)
6. II. 오늘 급등주 및 위꼬리 종목 상세 분석 (surging_stocks의 고가 대비 밀림률 분석 및 거래량 분석)
7. III. 주요 테마 및 관심 섹터 수급 추적 (반도체, 2차전지 등 주요 주도 섹터의 자금 유입도와 가격 위치 리뷰)
8. IV. 내일 전략 3대 시나리오 (글로벌 변수 기반 낙관/중립/비관 시나리오)
9. V. 오늘 가장 중요한 핵심 공시 분석 (공시 내용의 숨겨진 금융적 의미 해부)
10. 멋쟁이의 시각 (검정색 박스에 금빛 텍스트 포인트로 수석이사의 최종 에센스 코멘트 작성 - 외부 인용 절대 배제하고 1인칭 브랜드 시각 기술)
11. 투자 고지 (Disclaimer)
12. 출처 표기
"""

def generate_afternoon_report(market_data, news_data, morning_brief_data, evaluated_picks) -> str:
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    date_str = today.strftime("%Y%m%d")
    
    # 이미지 URL 생성
    market_theme = ""
    if market_data:
        kospi = market_data.get("kospi", {}).get("close", "")
        market_theme = f"KOSPI {kospi} Korean stock market close" if kospi else ""
    img1_url, img2_url = get_blog_image_urls(date_str, market_theme)
    
    print("🧠 통합 마감 판단 에이전트 작동 중 (디자인 통일 버전)...")
    
    prompt = f"""
오늘: {today.strftime("%Y년 %m월 %d일")} {weekday}요일 (KST)

=== 오전 브리핑 정보 ===
{json.dumps(morning_brief_data, ensure_ascii=False, indent=2) if morning_brief_data else "제공 정보 없음"}

=== 장 마감 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 오늘 뉴스·공시 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

위 데이터를 바탕으로 디자인 가이드를 철저히 준수하여 3,000자 이상의 풍부한 분량으로 완결된 오후 마감 리포트 HTML을 작성하라.

=== 블로그 이미지 (반드시 사용) ===
히어로 이미지 URL: {img1_url}
분석 이미지 URL:   {img2_url}

이미지 삽입 위치:
- 히어로 이미지: 마스트헤드 바로 아래
- 분석 이미지: 섹션 III 또는 IV 시작 직전

삽입 형식 (반드시 이대로):
<img src="URL" style="width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block" alt="멋쟁이 인사이트 마감 분석" loading="lazy">
"""
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16000,
            system=AFTERNOON_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text
        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        # 이미지 주입 안전장치
        img1_html = f'<img src="{img1_url}" style="width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block;" alt="멋쟁이 인사이트 마감 분석" loading="lazy">'
        img2_html = f'<img src="{img2_url}" style="width:100%;height:200px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block;" alt="멋쟁이 인사이트 마감 차트" loading="lazy">'
        
        # 1) GENERATING_IMAGE 플레이스홀더 치환
        text = re.sub(r'src=["\']GENERATING_IMAGE_1["\']', f'src="{img1_url}"', text)
        text = re.sub(r'src=["\']GENERATING_IMAGE_2["\']', f'src="{img2_url}"', text)
        
        # 2) BS4 이미지 강제 매칭
        from bs4 import BeautifulSoup as _BS
        soup = _BS(text, "html.parser")
        all_imgs = soup.find_all("img")
        if all_imgs:
            all_imgs[0]["src"] = img1_url
            all_imgs[0]["style"] = "width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block;"
            all_imgs[0]["loading"] = "lazy"
            if len(all_imgs) >= 2:
                all_imgs[1]["src"] = img2_url
                all_imgs[1]["style"] = "width:100%;height:200px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block;"
                all_imgs[1]["loading"] = "lazy"
            text = str(soup)
        else:
            if "<h1" in text:
                text = text.replace("<h1", img1_html + "\n<h1", 1)
            if "III." in text or "Ⅲ." in text:
                text = re.sub(r'(III\.|Ⅲ\.)', img2_html + r'\n\1', text, count=1)
            elif "</h1>" in text:
                text = text.replace("</h1>", "</h1>\n" + img2_html, 1)
                
        print("✅ 통합 마감 판단 완료")
        return text
    except Exception as e:
        print(f"통합 마감 분석 오류: {e}")
        return f"<div><p>오류 발생: {e}</p></div>"
