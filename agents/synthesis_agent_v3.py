"""
synthesis_agent_v3.py — 통합 판단 에이전트 v3
6개 전문가 분석 + 픽 성과 추적 통합
모바일 친화적 · 픽 섹션 최상단 · 손절선 필수
"""
import os, json, datetime, hashlib, urllib.parse, re, requests

from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()



def get_blog_image_urls(date_str: str, market_theme: str = "") -> tuple:
    """Pollinations AI로 블로그용 이미지 2장 URL 생성 (무료, API 키 불필요)
    날짜 기반 시드 사용 → 같은 날 같은 이미지 유지
    """
    seed1 = int(hashlib.md5(f"{date_str}_hero".encode()).hexdigest()[:8], 16) % 99999 + 1
    seed2 = int(hashlib.md5(f"{date_str}_chart".encode()).hexdigest()[:8], 16) % 99999 + 1

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

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

SYNTHESIS_V3_SYSTEM = """
당신은 멋쟁이 인사이트의 수석이사(Chief Managing Director)이자 최고투자전략책임자입니다.
6개 분야 수석 분석가(매크로·수급·실적·기술적·공시NLP·감성)의 분석 보고서를 정교하게 종합하여,
세계 최강 헤지펀드의 전략 보고서 수준으로 시장의 이면을 꿰뚫는 고품격 블로그 포스트를 작성합니다.

★ 월요일 오전 특별 지침:
- 한국 시간 기준 월요일 오전의 경우, 밤사이(일요일 밤) 미국 정규장이 열리지 않았으므로 전주 금요일 마감 종가 및 주말 동안의 주요 경제 이슈를 기준으로 한국 시장 개장 대비용 브리핑을 작성하십시오.

★ 주말(토요일·일요일) 발행 특별 지침 (매우 중요):
- 주말(토요일/일요일)에는 한국 주식 시장이 열리지 않으므로, 본문 섹션 제목 및 내용에서 "오늘 개장 영향" 또는 "오늘 장중 대응"이라는 표현을 절대 사용하지 마십시오.
- 대신 다음 섹션 구조를 적용하고, '오늘'이 아닌 '차주 월요일 개장 및 다음 주 시장 흐름'을 기준으로 서술하십시오:
  - II. 차주 월요일 한국 시장 개장 영향 (KOSPI/KOSDAQ 갭상승·갭하락 시나리오)
  - III. 주말 및 차주 대응 프로토콜 (다음 주 월요일 집중 추적 포인트 및 VIX 대비 전략)

★ 전일 한국장 연계 지침 (연결성 극대화):
- 전일 오후 마감 브리핑(`prev_afternoon_report`) 내용을 확인하고, 전날 오후 한국 시장의 수급 변화, 특징적 급등 테마/섹터 정보를 활용하십시오.
- 밤사이 미국 마켓의 핵심 섹터 등락 요인(예: 미국 반도체 하락, AI 전력 인프라 급등 등)이 전날 한국장에서 주도적이었던 테마들과 어떻게 충돌하거나 탄력을 주며 연결되는지 인과관계를 매끄럽고 설득력 있게 서술하여 분석의 영속성을 부여하십시오.



═══════════════════════════════
절대 금지 및 팩트 준수 규칙 (위반 시 즉시 반려)
═══════════════════════════════
1. **수치 및 지수 왜곡 절대 금지 (가장 중요)**:
   - 제공된 원본 데이터(`market_data`) 및 각 분석기에서 제공된 코스피(KOSPI), 코스닥(KOSDAQ) 지수 및 개별 종목의 종가, 등락률 수치를 **반드시 소수점까지 한 글자도 틀리지 않고 그대로 적용**하십시오.
   - 특히 **삼성전자(005930)와 SK하이닉스(000660)** 등 주요 종목들의 주가와 등락률을 서로 혼동하거나 뒤바꾸어 서술하지 마십시오. (예: 시뮬레이션 환경 데이터에서 삼성전자의 주가가 255,000원이고 SK하이닉스의 주가가 1,842,000원이라면, 절대로 'SK하이닉스가 25만원대로 추락했다'고 적거나 두 종목의 가격을 뒤섞어 작성해서는 안 됩니다.)
   - 글의 극적인 연출이나 흥미를 위해 KOSPI가 9,000선을 돌파했다거나, 특정 종목이 역대 최대 폭락을 기록했다는 등의 **허구의 수치나 가짜 역사적 사건을 가공·창조하는 행위를 엄격히 금지**합니다. 모든 수치는 입력된 `market_data`와 1:1로 엄격하게 일치해야 합니다.
   - 팩트에 기반한 정교하고 신뢰성 높은 서술만 허용됩니다.


2. 느낌표(!) 사용 절대 금지 · 급등예상 등의 자극적인 선동 표현 금지
3. JSON-LD 및 SVG 태그 본문 내 삽입 금지
4. 출처가 불분명한 모호한 수치 인용 금지
5. 투자 유인 및 특정 종목에 대한 확정적 추천 표현 금지

═══════════════════════════════
모바일 친화적 디자인 및 레이아웃 (최우선)
═══════════════════════════════
1. 흰색 배경 중심의 미니멀리즘 디자인 (정보 가독성을 극대화하기 위해 검정색 배경 박스는 본문 전체에서 최대 2개로 제한)
2. 복잡한 표(table) 지양 — 오직 상단의 '수치 대시보드' 1개에만 표 형식을 허용하고, 나머지는 깔끔한 카드형 div 활용
3. ★ 개별 종목 매수 추천(단타/스윙 픽 카드 등)은 절대 작성하지 마십시오. (매우 중요)
4. 대문자 로마숫자(I. II. III. IV. V.)를 사용한 논리적이고 정교한 섹션 분류 (한국어 제목 필수)
5. 본문 가독성을 높이기 위해 문단 스타일 지정: line-height: 1.95, font-size: 14.5px, color: #334155, letter-spacing: -0.015em 적용

═══════════════════════════════
HTML 최종 작성 구조 및 순서 (오전 7시 개장 전 브리핑 맞춤형)
═══════════════════════════════
1. 마스트헤드 (VOL / 날짜 / 브리핑 종류 등 정보가 정리된 흰색 배경 table)
2. [성과 트래커 HTML 삽입 지점] ← 여기에 반드시 {{PERFORMANCE_HTML}} 플레이스홀더를 위치시킬 것
3. 수치 대시보드 (검정색 배경의 핵심 지표 대시보드 - 미국 나스닥, S&P500, SOXX, DXY 달러, 원달러 환율, 미10년 금리, 유가 등 글로벌 매크로 중심 구성)
4. 히어로 이미지 (Unsplash 금융/주식 이미지 링크, 모바일에 맞추어 높이 220px 설정)
5. H1 역설형/수치형 헤드라인 (정확한 팩트 지표를 대조하여 독자의 관심을 끄는 세련된 제목)
6. I. 글로벌 마감 바이트 (미국 시장 요약)
   - 전일 미국 3대 지수(나스닥·S&P500·SOXX 반도체 ETF) 마감 수치 인용 분석
   - 미국 반도체/빅테크주 급등락 현황과 원인 분석
7. II. 오늘 한국 시장 개장 영향 (KOSPI/KOSDAQ 갭상승·갭하락 시나리오)
   - DXY 달러인덱스 및 원달러 환율 추이 기반 외국인 수급 방향 예측
   - 미국 반도체주 변동에 따른 삼성전자·SK하이닉스 시초가 개장 영향 예상
8. III. 오늘 장중 대응 프로토콜
   - 오늘 장중에 집중 추적해야 할 주요 가격선/지지선 및 외국인 수급 분기점
   - 시장 공포 수준(VIX 지수, 변동성 등)을 감안한 투자 강도 제안
9. IV. 3대 조건부 시나리오 (글로벌 변수 기반)
    - 낙관: 미국 야간선물 반등 및 외인 선물 매수 유입 시 지수 회복 경로
    - 중립: 환율 강보합 및 수급 눈치보기 국면 시 박스권 횡보 경로
    - 비관: 환율 추가 급등 및 외인 패닉 셀링 지속 시 지수 추가 붕괴 경로
10. 멋쟁이의 시각 (검정색 박스에 금빛 텍스트 포인트로 수석이사의 최종 에센스 코멘트 작성 - 외부 인용 절대 배제하고 1인칭 브랜드 시각 기술)
11. 투자 고지 (Disclaimer)
12. 출처 표기

"""


def synthesize_and_write(
    macro: dict,
    supply: dict,
    earnings: dict,
    technical: dict,
    dart_nlp: dict = None,
    foreign_tracker: dict = None,
    sentiment: dict = None,
    market_data: dict = None,
    performance_html: str = "",
    report_type: str = "daily"
) -> str:
    today = datetime.datetime.now()
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]
    date_str = today.strftime("%Y년 %m월 %d일")

    # 이미지 URL 생성
    market_theme = ""
    if market_data:
        kospi = market_data.get("kospi", {}).get("close", "")
        market_theme = f"KOSPI {kospi} Korean stock market" if kospi else ""
    img1_url, img2_url = get_blog_image_urls(today.strftime("%Y%m%d"), market_theme)
    print(f"🖼️ 이미지1: {img1_url[:60]}...")
    print(f"🖼️ 이미지2: {img2_url[:60]}...")

    print("🧠 통합 판단 v3 에이전트 작동 중...")

    prompt = f"""
오늘: {date_str} {weekday}요일 (KST)

=== 전일 한국 시장 마감 브리핑 요약 ===
{json.dumps(market_data.get("prev_afternoon_report", {}) if market_data else {}, ensure_ascii=False, indent=2)}

=== 글로벌 매크로 분석 ===
{json.dumps(macro, ensure_ascii=False, indent=2)}

=== 수급 분석 ===
{json.dumps(supply, ensure_ascii=False, indent=2)}

=== 실적·공시 분석 ===
{json.dumps(earnings, ensure_ascii=False, indent=2)}

=== 기술적 분석 ===
{json.dumps(technical, ensure_ascii=False, indent=2)}

=== 공시 NLP 분석 ===
{json.dumps(dart_nlp or {}, ensure_ascii=False, indent=2)}

=== 외국인 종목별 추적 ===
{json.dumps(foreign_tracker or {}, ensure_ascii=False, indent=2)}

=== 시장 감성 지수 ===
{json.dumps(sentiment or {}, ensure_ascii=False, indent=2)}

=== 원본 시장 데이터 ===
{json.dumps(market_data or {}, ensure_ascii=False, indent=2)}

위 6개 전문가 분석을 종합해서 블로그를 작성하라.

=== 블로그 이미지 (반드시 사용) ===
히어로 이미지 URL: {img1_url}
분석 이미지 URL:   {img2_url}

이미지 삽입 위치:
- 히어로 이미지: 마스트헤드 div 바로 아래
- 분석 이미지: 섹션 III 또는 IV 시작 직전
삽입 형식 (반드시 이대로):
<img src="URL" style="width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block" alt="멋쟁이 인사이트 시장 분석" loading="lazy">


반드시 지킬 것:
1. ★ 개별 종목 추천 및 단타 픽은 절대 본문에 포함하지 마십시오. (진입가/목표가/손절선 카드 포함 전체 금지)
2. 마스트헤드 다음에 {{PERFORMANCE_HTML}} 텍스트를 항상 삽입하십시오.
3. 미국 시장 마감 뉴스 및 주요 이슈를 바탕으로, 해당 요인들이 한국 주식 시장(KOSPI, KOSDAQ) 및 주요 업종/섹터(반도체, 2차전지 등)에 미칠 영향성만 정성적/거시적 관점에서 분석하십시오.

div-only HTML 전체 출력.

★★★ 필수: 개별 추천 종목이 없으므로 HTML 맨 마지막 줄에 항상 아래 형식의 JSON 주석만 한 줄 그대로 추가하십시오:
<!-- PICKS_JSON: [] -->

"""

    text = ""
    try:
        try:
            print("🤖 [우선순위 1] Claude Sonnet 4.6으로 통합 분석서 생성 중...")
            resp = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=16000,
                system=SYNTHESIS_V3_SYSTEM,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text
            print("✅ Claude Sonnet 4.6 생성 성공")
        except Exception as claude_err:
            print(f"⚠️ Claude Sonnet 4.6 호출 실패 ({claude_err}) → Gemini 백업 시스템 작동...")
            
            gemini_key = os.getenv("GEMINI_API_KEY", "")
            if not gemini_key:
                print("❌ GEMINI_API_KEY가 없습니다. 폴백 불가.")
                raise claude_err
                
            # 백업 모델: gemini-2.5-pro 우선 시도 후 gemini-2.5-flash
            backup_models = ["gemini-2.5-pro", "gemini-2.5-flash"]
            gemini_success = False
            
            for model in backup_models:
                print(f"🤖 Gemini 백업 호출 시도 중: {model}...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                body = {
                    "contents": [{"parts": [{"text": SYNTHESIS_V3_SYSTEM + "\n\n" + prompt}]}],
                    "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3}
                }
                try:
                    res = requests.post(url, json=body, timeout=180)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            content = candidates[0].get("content", {})
                            parts = content.get("parts", [])
                            if parts:
                                text = parts[0].get("text", "")
                                if text:
                                    print(f"✅ Gemini 백업 생성 완료 ({model})")
                                    gemini_success = True
                                    break
                    print(f"❌ Gemini {model} 응답 실패: HTTP {res.status_code} — {res.text[:150]}")
                except Exception as gem_err:
                    print(f"❌ Gemini {model} 연결 예외 발생: {gem_err}")
                    
            if not gemini_success:
                print("❌ 모든 백업 AI 호출이 실패했습니다.")
                raise claude_err

        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # 픽 성과 HTML 삽입
        if performance_html:
            text = text.replace("{{PERFORMANCE_HTML}}", performance_html)
        else:
            text = text.replace("{{PERFORMANCE_HTML}}", "")

        # ─────────────────────────────────────────────────────
        # 이미지 강제 주입 (Claude가 임의 URL 사용 방지)
        # ─────────────────────────────────────────────────────
        img1_html = (
            f'<img src="{img1_url}" '
            f'style="width:100%;height:220px;object-fit:cover;border-radius:10px;'
            f'margin:14px 0 20px;display:block;" '
            f'alt="멋쟁이 인사이트 시장 분석 — 서울 금융가" loading="lazy">'
        )
        img2_html = (
            f'<img src="{img2_url}" '
            f'style="width:100%;height:200px;object-fit:cover;border-radius:10px;'
            f'margin:14px 0 20px;display:block;" '
            f'alt="멋쟁이 인사이트 차트 분석" loading="lazy">'
        )

        # 1) GENERATING_IMAGE 플레이스홀절 치환
        text = re.sub(r'src=["\']GENERATING_IMAGE_1["\']', f'src="{img1_url}"', text)
        text = re.sub(r'src=["\']GENERATING_IMAGE_2["\']', f'src="{img2_url}"', text)

        # 2) Unsplash/기타 임의 이미지 URL을 Pollinations URL로 교체
        #    (히어로 이미지: 첫 번째 img 태그)
        from bs4 import BeautifulSoup as _BS
        import re as _re
        soup = _BS(text, "html.parser")
        all_imgs = soup.find_all("img")
        if all_imgs:
            # 첫 번째 이미지를 img1_url로 강제 교체
            all_imgs[0]["src"] = img1_url
            all_imgs[0]["style"] = "width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block;"
            all_imgs[0]["loading"] = "lazy"
            # 두 번째 이미지가 있으면 img2_url로 강제 교체
            if len(all_imgs) >= 2:
                all_imgs[1]["src"] = img2_url
                all_imgs[1]["style"] = "width:100%;height:200px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block;"
                all_imgs[1]["loading"] = "lazy"
            text = str(soup)
        else:
            # 이미지 태그 자체가 없으면 강제 삽입
            # 히어로: H1 태그 앞에 삽입
            if "<h1" in text:
                text = text.replace("<h1", img1_html + "\n<h1", 1)
            # 분석 이미지: III 섹션 앞에 삽입
            if "III." in text or "Ⅲ." in text:
                text = _re.sub(r'(III\.|Ⅲ\.)', img2_html + r'\n\1', text, count=1)
            elif "</h1>" in text:
                text = text.replace("</h1>", "</h1>\n" + img2_html, 1)

        print(f"🖼️ 이미지 주입 완료: {img1_url[:50]}...")
        print("✅ 통합 판단 v3 완료")
        return text
    except Exception as e:
        print(f"통합 에이전트 v3 오류: {e}")
        return f"<div><p>오류: {e}</p></div>"


