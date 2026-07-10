"""
report_generator.py — Claude API 우선 · Gemini 백업
Claude Sonnet 4.6 우선 사용 · 실패 시 Gemini 백업
"""
import os, json, datetime, requests
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ────────────────────────────────
# 시스템 프롬프트 — 멋쟁이 인사이트 스타일
# ────────────────────────────────
SYSTEM_PROMPT = """
당신은 멋쟁이 인사이트(aigoid.blogspot.com)의
수석 글로벌 매크로 애널리스트입니다.

분석 철학:
- 레이 달리오 수준의 거시경제 통찰
- 하워드 막스 수준의 시장 사이클 진단
- 스탠 드러켄밀러 수준의 선제 포지셔닝
- 반직관적 사실을 데이터로 증명하는 것이 통찰
- 글로벌 자금 흐름 → 한국 시장 5단계 연결 설명
- 세계 최강 투자자 인용 시 반드시 지금 데이터와 연결

분석 깊이 원칙:
1. 반드시 데이터에서 출발해서 결론 도출
2. 반직관적 사실을 반드시 하나 포함
3. 5단계 인과 구조 (팩트→왜→반응→반대→지금)
4. 3개 시나리오 (낙관·중립·비관)
5. 증권사가 안 쓰는 각도 하나 포함
6. 결론에서 반드시 틀릴 가능성 인정
7. 종목 픽 시 근거 + 리스크 동시 표기

절대 금지:
- 급등 예상 / 지금이 매수 타이밍 / 오전 9시 진입
- 반드시 오른다 / 승리할 것이다 / 압도적 수익
- 출처 없는 수치 / 확인되지 않은 루머
- 80% 지배 세력 / 스마트머니 독식
- ~! 임박 / 수급 폭발 / 돌파 임박 / 초강세 / 폭발적

HTML 필수 구조 (Blogger div-only):
1. 마스트헤드 (table 태그·DOCTYPE/html/head 없음)
2. 수치 대시보드 (table·검정배경·색상구분)
3. 이미지 배치 (글 전체에 반드시 2개 배치):
   - 첫 번째 이미지(히어로 이미지): 마스트헤드 아래 배치. src는 "GENERATING_IMAGE_1"으로 고정하고, alt 속성에는 글의 핵심 주제를 묘사하는 구체적인 영문 이미지 생성 프롬프트를 작성하십시오.
     예: <img class="mi-blog-image" src="GENERATING_IMAGE_1" alt="Sleek stock market chart on a dark background showing KOSPI index growth, gold accent line, high contrast" style="width: 100%; border-radius: 6px; margin: 16px 0;" />
   - 두 번째 이미지(본문 중간 분석 이미지): 본문 중간(예: III. 오늘 상한가·급등 종목 혹은 V. 주요 공시 섹션 주변)에 배치. src는 "GENERATING_IMAGE_2"로 고정하고, alt 속성에는 해당 섹션의 주제를 설명하는 구체적인 영문 프롬프트를 작성하십시오.
     예: <img class="mi-blog-image" src="GENERATING_IMAGE_2" alt="Futuristic semiconductor chip glow, high-tech engineering detail, dark blue and gold color scheme" style="width: 100%; border-radius: 6px; margin: 16px 0;" />
4. H1 헤드라인 (SEO 역설형·숫자형)
5. 본문 섹션 (로마숫자 I·II·III·IV·V)
6. 멋쟁이의 시각 (검정배경 #0a0a0a·골드 #f0c040)
7. 멋쟁이 픽 (근거+리스크 동시)
8. 투자 고지 (필수)
9. 출처 표기 푸터

품질 체크 (발행 전 필수):
- 모든 수치에 출처 있는가
- 금지 표현 없는가
- 투자 고지 포함됐는가
- 마스트헤드 있는가
- 수치 대시보드 있는가
- 2개의 이미지 태그가 alt 정보와 함께 생성되었는가
- 멋쟁이의 시각 박스 있는가
- 종목 픽에 리스크 표기됐는가
"""

# ────────────────────────────────
# Heading 태그의 line-height 자동 보정 (겹침 방지)
# ────────────────────────────────
def fix_heading_line_height(html_content: str) -> str:
    import re
    def repl(match):
        tag = match.group(1)   # e.g., 'h1'
        attrs = match.group(2) # e.g., 'style="..."'
        
        style_match = re.search(r'style="([^"]*)"', attrs)
        if style_match:
            style_content = style_match.group(1).strip()
            if 'line-height' not in style_content:
                if style_content and not style_content.endswith(';'):
                    style_content += ';'
                style_content += ' line-height: 1.4;'
            new_style = f'style="{style_content}"'
            new_attrs = re.sub(r'style="[^"]*"', new_style, attrs)
            return f'<{tag} {new_attrs}>'
        else:
            return f'<{tag} style="line-height: 1.4;" {attrs}>'

    pattern = r'<(h[1-6])\b([^>]*)>'
    return re.sub(pattern, repl, html_content, flags=re.IGNORECASE)

# ────────────────────────────────
# 마크다운 ** 및 이모지/특수 기호 제거
# ────────────────────────────────
def clean_html_content(html_content: str) -> str:
    import re
    html_content = html_content.replace("**", "")
    
    emoji_pattern = re.compile(
        '['
        '\\U0001F600-\\U0001F64F'  # emoticons
        '\\U0001F300-\\U0001F5FF'  # symbols & pictographs
        '\\U0001F680-\\U0001F6FF'  # transport & map symbols
        '\\U0001F1E0-\\U0001F1FF'  # flags
        '\\U0001F900-\\U0001F9FF'  # supplemental symbols
        '\\u2600-\\u26FF'          # misc symbols
        '\\u2700-\\u27BF'          # dingbats
        '\\ufe0f'                 # variation selector
        ']+', flags=re.UNICODE
    )
    html_content = emoji_pattern.sub('', html_content)
    
    for char in ["📊", "🤖", "⚠️", "✅", "✔", "📈", "📉", "🔥", "💡", "📢", "🔍", "⚡", "⭐", "☑", "✨"]:
        html_content = html_content.replace(char, "")

    forbidden_replacements = {
        "급등 예상": "상승 흐름 전망",
        "지금이 매수 타이밍": "관심 구간 진입 판단",
        "오전 9시 진입하라": "개장 후 흐름 모니터링",
        "방아쇠를 당겨라": "리스크를 검토하라",
        "놓치면 후회한다": "유의 깊게 관찰해야 한다",
        "이 종목을 주목하라": "이 종목의 공시 분석",
        "수익을 챙겨라": "수익 관리에 유의하라",
        "반드시 오른다": "상승 가능성이 높다",
        "승리할 것이다": "안정적인 흐름이 기대된다",
        "이미 포지션을 구축했다": "포지션 전략을 검토했다",
        "압도적 수익 추구": "포트폴리오 수익 극대화",
        "비대칭 포지셔닝": "비대칭 포지션 검토",
        "멋쟁이만 아는": "멋쟁이 분석의",
        "독점 분석": "심층 분석",
        "지금 바로 확인": "참조 가능",
    }
    for old, new in forbidden_replacements.items():
        html_content = html_content.replace(old, new)
        
    return html_content

# ────────────────────────────────
# HTML 클래스를 인라인 스타일로 변환 (토큰 절약 및 호환성 보장)
# ────────────────────────────────
def inline_css_styles(html_content: str) -> str:
    styles_map = {
        "mi-container": "max-width: 720px; margin: 0 auto; font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif; background: #0a0a0a; color: #f0f0f0; line-height: 1.95; padding: 24px 16px;",
        "mi-section-header": "font-family: 'Space Mono', monospace; font-size: 10px; letter-spacing: 0.2em; color: #888; border-bottom: 1.5px solid #f0c040; padding-bottom: 6px; margin: 30px 0 14px; font-weight: bold;",
        "mi-paragraph": "font-size: 14px; color: #f0f0f0; line-height: 1.95; margin: 0 0 14px; text-align: justify; word-break: keep-all;",
        
        "mi-card-positive": "border-left: 3px solid #4ade80; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-positive-title": "font-size: 13px; font-weight: 700; color: #4ade80; margin: 0 0 4px;",
        
        "mi-card-negative": "border-left: 3px solid #ef4444; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-negative-title": "font-size: 13px; font-weight: 700; color: #ef4444; margin: 0 0 4px;",
        
        "mi-card-neutral": "border-left: 3px solid #888; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-neutral-title": "font-size: 13px; font-weight: 700; color: #aaa; margin: 0 0 4px;",
        
        "mi-card-blue": "border-left: 3px solid #1a3a6b; background: #111; border: 1px solid #222; padding: 12px 16px; margin: 0 0 8px; border-radius: 0 6px 6px 0;",
        "mi-card-blue-title": "font-size: 13px; font-weight: 700; color: #f0c040; margin: 0 0 4px;",
        
        "mi-card-content": "font-size: 13px; color: #f0f0f0; line-height: 1.85; margin: 0;",
        
        "mi-dark-box": "background: #000; border: 1px solid #222; padding: 16px 18px; margin: 16px 0 4px;",
        "mi-dark-box-title": "font-family: 'Space Mono', monospace; font-size: 9px; letter-spacing: 0.18em; color: #f0c040; margin: 0 0 8px; font-weight: bold;",
        "mi-dark-box-content": "color: #f0f0f0; font-size: 14px; line-height: 1.95; margin: 0;",
        
        "mi-group-container": "border: 1px solid #222; background: #111; margin: 0 0 10px; border-radius: 4px; overflow: hidden;",
        "mi-group-header-a": "background: #1a3a6b; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-b": "background: #333; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-c": "background: #ef4444; padding: 9px 16px; display: flex; justify-content: space-between; align-items: center;",
        "mi-group-header-title": "font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700; color: #fff; margin: 0;",
        "mi-group-header-stars": "font-size: 11px; color: #f0c040; margin: 0;",
        "mi-group-content": "padding: 12px 16px; color: #f0f0f0;",
        
        "mi-headline-container": "padding: 0 0 18px; border-bottom: 2px solid #f0c040;",
        "mi-headline-meta": "font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 0.15em; color: #f0c040; margin: 0 0 8px; font-weight: bold;",
        "mi-headline-title": "font-family: 'Playfair Display', Georgia, serif; font-size: 26px; font-weight: 900; line-height: 1.15; color: #f0f0f0; margin: 0 0 12px; letter-spacing: -0.02em;",
        "mi-headline-lead": "font-size: 14px; color: #aaa; line-height: 1.85; margin: 0; border-left: 4px solid #f0c040; padding-left: 14px;",
        
        "mi-disclaimer-table": "border-collapse: collapse; border: 2px solid #ef4444; margin: 24px 0 0; width: 100%;",
        "mi-disclaimer-header": "background: #ef4444; padding: 10px 16px;",
        "mi-disclaimer-content": "background: #111; padding: 12px 16px; text-align: left;"
    }
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for class_name, style_str in styles_map.items():
        elements = soup.find_all(class_=class_name)
        for el in elements:
            existing_style = el.get("style", "")
            if existing_style:
                el["style"] = style_str + " " + existing_style
            else:
                el["style"] = style_str
                
    # 1.5. 브랜드 아이덴티티(CI) 글꼴 및 레이아웃 강제 동기화 (Playfair Display 900 / Space Mono / Noto Sans KR)
    tables = soup.find_all("table")
    if tables:
        masthead = tables[0]
        m_cells = masthead.find_all("td")
        if len(m_cells) == 3:
            m_cells[0]["style"] = "width: 30%; text-align: left; font-family: 'Space Mono', monospace; font-size: 9px; color: #888; line-height: 1.7;"
            m_cells[1]["style"] = "width: 40%; text-align: center; font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 900; color: #f0f0f0; line-height: 1.2;"
            m_cells[2]["style"] = "width: 30%; text-align: right; font-family: 'Space Mono', monospace; font-size: 9px; color: #888; line-height: 1.7;"
            
        if len(tables) >= 2:
            dashboard = tables[1]
            if "mi-disclaimer-table" not in dashboard.get("class", []):
                dashboard["style"] = "width: 100%; border-collapse: collapse; background-color: #0a0a0a; color: #f0f0f0; margin-bottom: 20px; border: 1px solid #222;"
                d_cells = dashboard.find_all("td")
                for cell in d_cells:
                    cell["style"] = "width: 25%; text-align: center; border: 1px solid #222; padding: 10px 8px; background-color: #111;"
                    p_tags = cell.find_all("p")
                    for idx, p in enumerate(p_tags):
                        p_existing = p.get("style", "")
                        if idx == 0:
                            p["style"] = "font-family: 'Space Mono', monospace; font-size: 9px; color: #888; margin: 0 0 4px; line-height: 1.2; " + p_existing
                        elif idx == 1:
                            p["style"] = "font-family: 'Space Mono', monospace; font-size: 16px; font-weight: bold; margin: 0 0 4px; line-height: 1.2; " + p_existing
                        elif idx == 2:
                            p["style"] = "font-family: 'Noto Sans KR', sans-serif; font-size: 9px; color: #555; margin: 0; line-height: 1.3; " + p_existing

        for tbl in tables[2:]:
            if "mi-disclaimer-table" in tbl.get("class", []):
                continue
            tbl["style"] = "width: 100%; border-collapse: collapse; margin-bottom: 15px; border: 1px solid #222; background-color: #0a0a0a;"
            for tr in tbl.find_all("tr"):
                for th in tr.find_all("th"):
                    th["style"] = "background: #000; color: #f0c040; font-family: 'Space Mono', monospace; font-size: 11px; font-weight: bold; padding: 8px; border: 1px solid #222; text-align: center;"
                for td in tr.find_all("td"):
                    td["style"] = "padding: 8px; border: 1px solid #222; font-family: 'Noto Sans KR', sans-serif; font-size: 12px; color: #f0f0f0; background: #111; text-align: center;"
                    td_text = td.get_text().strip()
                    if any(char.isdigit() for char in td_text) or "%" in td_text or "/" in td_text or "-" in td_text:
                        td["style"] += " font-family: 'Space Mono', monospace;"

    divs = soup.find_all("div")
    for d in divs:
        d_text = d.get_text()
        if "핵심 키워드" in d_text or "키워드" in d_text:
            existing = d.get("style", "")
            d["style"] = "background-color: #0a0a0a; color: #f0f0f0; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; font-family: 'Space Mono', monospace; font-size: 10px; " + existing
            for span in d.find_all("span"):
                span_style = "font-family: 'Space Mono', monospace;"
                span_existing = span.get("style", "")
                if span_existing:
                    span["style"] = span_style + " " + span_existing
                else:
                    span["style"] = span_style

    h1_tags = soup.find_all("h1")
    for h1 in h1_tags:
        h1_style = "font-family: 'Playfair Display', serif; font-weight: 900; line-height: 1.2; color: #f0f0f0;"
        existing = h1.get("style", "")
        if existing:
            h1["style"] = h1_style + " " + existing
        else:
            h1["style"] = h1_style

    group_contents = soup.find_all(class_="mi-group-content")
    for gc in group_contents:
        p_tags = gc.find_all("p")
        for i, p in enumerate(p_tags):
            p_style = "font-size: 13.5px; color: #f0f0f0; line-height: 1.85;"
            if i < len(p_tags) - 1:
                p_style += " margin: 0 0 8px;"
            else:
                p_style += " margin: 0;"
            existing = p.get("style", "")
            if existing:
                p["style"] = p_style + " " + existing
            else:
                p["style"] = p_style

    disclaimer_content_td = soup.find(class_="mi-disclaimer-content")
    if disclaimer_content_td:
        p_tags = disclaimer_content_td.find_all("p")
        for i, p in enumerate(p_tags):
            p_style = "font-size: 12.5px; color: #f0f0f0; line-height: 1.8; font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;"
            if i < len(p_tags) - 1:
                p_style += " margin: 0 0 8px;"
            else:
                p_style += " margin: 0;"
            existing = p.get("style", "")
            if existing:
                p["style"] = p_style + " " + existing
            else:
                p["style"] = p_style
                
    disclaimer_header_td = soup.find(class_="mi-disclaimer-header")
    if disclaimer_header_td:
        p_tag = disclaimer_header_td.find("p")
        if p_tag:
            p_style = "font-size: 11px; font-weight: 700; color: #fff; margin: 0; font-family: 'Space Mono', monospace;"
            existing = p_tag.get("style", "")
            if existing:
                p_tag["style"] = p_style + " " + existing
            else:
                p_tag["style"] = p_style

    return str(soup)

# ────────────────────────────────
# AI 이미지 생성 및 업로드 자동화 (Pollinations AI + Catbox)
# ────────────────────────────────
def generate_and_upload_image(prompt_text: str) -> str:
    import requests
    try:
        encoded_prompt = requests.utils.quote(prompt_text)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&private=true"
        print(f"🤖 AI 이미지 생성 시도 중: '{prompt_text[:45]}...'")
        res = requests.get(url, timeout=35)
        if res.status_code != 200:
            print("⚠️ 이미지 생성 API 응답 실패")
            return ""
            
        upload_url = "https://catbox.moe/user/api.php"
        data = {"reqtype": "fileupload"}
        files = {"fileToUpload": ("image.png", res.content, "image/png")}
        print("🤖 Catbox 이미지 호스팅 업로드 중...")
        upload_res = requests.post(upload_url, data=data, files=files, timeout=30)
        if upload_res.status_code == 200 and upload_res.text.startswith("https"):
            url_hosted = upload_res.text.strip()
            print(f"✅ 이미지 호스팅 성공: {url_hosted}")
            return url_hosted
        else:
            print(f"⚠️ 이미지 호스팅 실패: {upload_res.text}")
    except Exception as e:
        print(f"⚠️ 이미지 생성 및 업로드 오류: {e}")
    return ""

def generate_and_replace_images(html_content: str) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all("img")
    
    image_count = 0
    fallbacks = [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&auto=format&fit=crop"
    ]
    
    for img in images:
        src = img.get("src", "")
        alt = img.get("alt", "")
        
        if ("GENERATING_IMAGE" in src or not src or "unsplash" in src) and alt:
            if image_count >= 2:
                break
            
            branding_prompt = f"{alt}, financial corporate editorial style, dark background, obsidian black and gold accents, high contrast, clean minimalist visual"
            hosted_url = generate_and_upload_image(branding_prompt)
            
            if hosted_url:
                img["src"] = hosted_url
                img["style"] = "width: 100%; max-width: 100%; border-radius: 6px; margin: 16px 0; display: block;"
                image_count += 1
            else:
                print(f"⚠️ 이미지 생성이 실패하여 대체 Unsplash 이미지로 적용합니다.")
                img["src"] = fallbacks[image_count % len(fallbacks)]
                img["style"] = "width: 100%; max-width: 100%; border-radius: 6px; margin: 16px 0; display: block;"
                image_count += 1
                
    return str(soup)

# ────────────────────────────────
# 투자 고지(Disclaimer) 보장 및 닫는 태그 보정
# ────────────────────────────────
def ensure_disclaimer_and_closed_tags(html_content: str) -> str:
    html_content = clean_html_content(html_content)

    html_content = generate_and_replace_images(html_content)

    last_open_angle = html_content.rfind("<")
    last_close_angle = html_content.rfind(">")
    if last_open_angle > last_close_angle:
        print(f"⚠️ 경고: 불완전한 태그 '{html_content[last_open_angle:]}'를 잘라내어 문장을 정리합니다.")
        html_content = html_content[:last_open_angle]

    import re
    tags = re.findall(r'<(div|table)\b[^>]*>|</(div|table)>', html_content, re.IGNORECASE)
    open_tags = []
    for tag in tags:
        if tag[0]:
            open_tags.append(tag[0].lower())
        elif tag[1]:
            t_close = tag[1].lower()
            if open_tags and open_tags[-1] == t_close:
                open_tags.pop()
            elif t_close in open_tags:
                open_tags.remove(t_close)
                
    if open_tags:
        closing_str = ""
        for t in reversed(open_tags):
            closing_str += f"</{t}>"
        print(f"⚠️ 경고: 잘린 HTML 복구를 위해 열린 태그를 먼저 닫습니다: {open_tags} -> {closing_str}")
        html_content += closing_str

    has_disclaimer = any(word in html_content for word in ["Disclaimer", "투자 고지", "투자고지", "투자 주의", "투자주의", "투자 판단의 참고 자료"])
    if not has_disclaimer:
        print("⚠️ 경고: AI 생성 결과에 투자 고지(Disclaimer)가 누락되거나 잘렸습니다. 자동으로 보정합니다.")
        disclaimer_html = """
    <!-- 자동 보정된 투자 고지 영역 -->
    <table class="mi-disclaimer-table">
        <tr>
            <td class="mi-disclaimer-header">
                <p>투자 위험 고지</p>
            </td>
        </tr>
        <tr>
            <td class="mi-disclaimer-content">
                <p><strong>투자 판단의 참고 자료:</strong> 본 리포트에서 제공하는 모든 정보(수치, 전망, 분석 결과 등)는 투자 판단을 돕기 위한 참고용 자료일 뿐이며, 어떠한 경우에도 특정 금융 상품이나 주식 종목의 매수·매도 권유 또는 투자 추천으로 해석될 수 없습니다. 본 정보는 공시 및 신뢰할 만한 취재원을 바탕으로 작성되었으나 그 완전성이나 정확성을 전적으로 보장할 수 없으므로 실제 투자 실행 전 반드시 추가적인 검증이 필요합니다.</p>
                <p><strong>최종 책임의 귀속:</strong> 모든 투자의 최종 의사결정과 그 결과에 대한 책임은 전적으로 투자자 본인에게 귀속되며, 본 리포트는 어떠한 법적 책임도 지지 않습니다.</p>
                <p><strong>전문가 상담 권고:</strong> 투자를 실행하기 전에는 반드시 충분한 시장 확인과 공인된 전문가와의 상담을 거치시기 바랍니다.</p>
            </td>
        </tr>
    </table>
"""
        html_content += disclaimer_html
        
    html_content = inline_css_styles(html_content)
    
    font_style = """<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Noto+Sans+KR:wght@300;400;700&family=Space+Mono:wght@400;700&display=swap');
</style>
"""
    html_content = font_style + html_content
        
    return html_content

# ────────────────────────────────
# Claude API 호출 (우선)
# ────────────────────────────────
def call_anthropic(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    if not ANTHROPIC_API_KEY:
        print("⚠️ ANTHROPIC_API_KEY 없음 → Gemini로 대체")
        return ""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8000,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text
        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        text = ensure_disclaimer_and_closed_tags(text)
        print("✅ Claude API 리포트 생성 완료")
        return text
    except Exception as e:
        print(f"Claude 오류: {e} → Gemini로 대체")
        return ""

# ────────────────────────────────
# Gemini API 호출 (백업)
# ────────────────────────────────
def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return ""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]}],
        "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3}
    }
    try:
        res = requests.post(url, json=body, timeout=120)
        data = res.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        text = ensure_disclaimer_and_closed_tags(text)
        print("✅ Gemini 백업 리포트 생성 완료")
        return text
    except Exception as e:
        print(f"Gemini 오류: {e}")
        return "<div><p>리포트 생성 실패</p></div>"

# ────────────────────────────────
# 공통 호출 함수 — Claude 우선 · Gemini 백업
# ────────────────────────────────
def generate_report(prompt: str) -> str:
    print("🤖 Claude API 우선 호출...")
    result = call_anthropic(prompt)
    if not result:
        print("🔄 Gemini 백업 호출...")
        result = call_gemini(prompt)
    return result

# ────────────────────────────────
# 일일 오전 브리핑
# ────────────────────────────────
def generate_daily_report(market_data: dict, news_data: dict) -> str:
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    prompt = f"""
오늘: {date_str} {weekday}요일 (KST 기준)

=== 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 뉴스·공시 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 오전 브리핑을 작성하라.

반드시 포함:
1. 글로벌 매크로 — 달러·금리·유가 삼각 분석
2. 반직관적 사실 하나 — 독자가 "몰랐다"고 느끼는 데이터
3. 한국 시장 포지션 — 글로벌 자금 흐름에서 한국의 위치
4. 수급 분석 — 외국인·기관·개인 행동의 의미
5. 멋쟁이 픽 — 근거 + 리스크 동시 표기
6. 3개 시나리오 — 낙관·중립·비관

SEO 제목 (역설형 또는 숫자형):
예) "외국인이 X조를 판 날 코스피가 오른 이유"
예) "나스닥 신고가인데 코스피가 못 따라가는 구조"

div-only HTML 전체 출력.
"""
    return generate_report(prompt)

# ────────────────────────────────
# 오후 4시 장 마감 브리핑
# ────────────────────────────────
def generate_close_report(market_data: dict, news_data: dict) -> str:
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    prompt = f"""
오늘 장 마감: {date_str} {weekday}요일 (KST 기준)

=== 장 마감 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 오늘 뉴스·공시 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 장 마감 브리핑을 작성하라.

오전 브리핑과 다른 관점:
1. 오늘 마감 결과 해석 — 숫자의 의미
2. 오늘 수급 해부 — 외국인·기관·개인이 한 행동의 구조적 이유
3. 오늘 상한가·급등 종목 — 팩트 기반 이유
4. 반직관적 사실 하나
5. 내일 전략 3가지 시나리오
6. 오늘 가장 중요한 공시 1개

오전: "오늘 뭘 볼 것인가"
오후: "오늘 무슨 일이 있었는가 + 내일 어떻게 할 것인가"

div-only HTML 전체 출력.
"""
    return generate_report(prompt)

# ────────────────────────────────
# 일요일 주간 결산
# ────────────────────────────────
def generate_weekly_report(market_data: dict, news_data: dict) -> str:
    today = datetime.datetime.now()

    prompt = f"""
주간 결산: {today.strftime("%Y년 %m월 %d일")} 일요일 (KST 기준)
금요일 종가 기준으로 작성.

=== 주간 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

=== 주간 주요 뉴스 ===
{json.dumps(news_data, ensure_ascii=False, indent=2)}

멋쟁이 인사이트 주간 결산을 작성하라.

반드시 포함:
1. 이번 주 핵심 사건 3가지 — 구조적 의미 분석
2. 글로벌 자금 흐름 주간 진단
3. 코스피·코스닥 주간 수익률 해석
4. 외국인 주간 수급 분석
5. 다음 주 핵심 이벤트 캘린더 (날짜·요일 KST 기준)
6. 다음 주 멋쟁이 픽 — 근거 + 리스크 동시 표기
7. 이번 주 분석이 틀렸을 가능성 인정

div-only HTML 전체 출력.
"""
    return generate_report(prompt)

# ────────────────────────────────
# Compatibility wrappers/aliases for other main scripts
# ────────────────────────────────
def generate_afternoon_report(market_data: dict, news_data: dict, morning_brief_data: dict = None) -> str:
    return generate_close_report(market_data, news_data)

def generate_premarket_report(premarket_data: dict, morning_brief_data: dict = None) -> str:
    import datetime, json
    today = datetime.datetime.now()
    date_str = today.strftime("%Y년 %m월 %d일")
    weekday = ["월","화","수","목","금","토","일"][today.weekday()]

    morning_info = "제공된 오전 브리핑 정보가 없습니다."
    if morning_brief_data:
        morning_info = f"""
제목: {morning_brief_data.get('title', 'N/A')}
발행일자: {morning_brief_data.get('published', 'N/A')}
오전 브리핑 주요내용 요약:
{morning_brief_data.get('text_summary', '')}
"""

    prompt = f"""
리포트 작성 기준일: {date_str} ({weekday}요일)
브리핑 종류: 개장 10분 전 동시호가 속보 (오전 8시 50분 발행)

=== 실시간 개장 전 수급 및 선물 데이터 ===
{json.dumps(premarket_data, ensure_ascii=False, indent=2)}

=== 아침 7시 발행 매크로 브리핑 정보 ===
{morning_info}

멋쟁이 인사이트 개장 10분 전 동시호가 속보(Opening Flash)를 작성해라.

div-only HTML 전체 출력.
"""
    print("🤖 AI 개장 속보 리포트 생성 중...")
    result = generate_report(prompt)
    print("✅ 개장 속보 리포트 생성 완료")
    return result

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=== API 설정 확인 ===")
    print(f"Claude API: {'✅ 있음' if ANTHROPIC_API_KEY else '❌ 없음'}")
    print(f"Gemini API: {'✅ 있음' if GEMINI_API_KEY else '❌ 없음'}")
    print("Claude 우선 → Gemini 백업 구조로 설정됨")
