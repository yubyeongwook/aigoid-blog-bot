"""
멋쟁이 인사이트 — 실시간 트렌드 키워드 블로그 자동 발행
네이버 DataLab API로 실시간 트렌드 수집 → Claude로 블로그 글 작성 → Blogger 발행
"""

import os
import json
import re
import requests
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone, timedelta
import anthropic
import agents.patch_anthropic


NAVER_DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def get_trending_keywords(client_id: str, client_secret: str) -> list[str]:
    """네이버 DataLab에서 실시간 트렌드 키워드 수집"""
    # 인기 검색어 카테고리들
    keywords = [
        ["주식", "코스피", "코스닥"],
        ["반도체", "SK하이닉스", "삼성전자"],
        ["환율", "달러", "금리"],
        ["에코프로", "2차전지", "배터리"],
        ["부동산", "아파트", "금리인하"],
    ]

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json",
    }

    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [{"groupName": k[0], "keywords": k} for k in keywords],
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(NAVER_DATALAB_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        # 최근 트렌드 상위 키워드 추출
        results = result.get("results", [])
        sorted_results = sorted(
            results,
            key=lambda x: sum(d.get("ratio", 0) for d in x.get("data", [])),
            reverse=True
        )
        return [r["title"] for r in sorted_results[:5]]
    except Exception as e:
        print(f"트렌드 키워드 수집 실패: {e}")
        return ["주식", "코스피", "달러", "반도체", "금리"]


TREND_BLOG_PROMPT = """당신은 '멋쟁이 인사이트 SMART MONEY INTELLIGENCE'의 수석이사(Chief Managing Director)이자 최고투자전략책임자입니다.
실시간 인기 트렌드 키워드를 바탕으로, 투자자들이 시장의 이면을 꿰뚫어 볼 수 있는 고품격 분석 보고서 수준의 블로그 글을 작성합니다.

# 작성 규칙
1. **전문적이고 격조 있는 톤 앤 매너**:
   - 느낌표(!) 사용을 절대 금지합니다.
   - '급등 예상', '대박', '폭발' 등 자극적인 선동적 표현이나 가벼운 구어체는 배제하고, 차분하고 객관적인 애널리스트 톤으로 작성하십시오.
   - 가볍고 저급한 이모지(🔥, 🚀, 💰, 🎢, 🔑, 🔮 등)의 무분별한 사용을 엄격히 금지합니다. 필요한 경우 차분한 문단 마커(📈, 📉, 📊 등)만 본문 타이틀에 한해 절제해서 사용하십시오.
2. **날짜 및 팩트 준수**:
   - 제공된 오늘 날짜를 기준으로 작성하며, 과거 연도를 잘못 언급하지 않도록 주의하십시오.
   - 키워드와 관련된 최신 정보를 검색 도구로 명확하게 리서치하여 팩트 기반으로 서술하십시오.
3. **가독성 높은 HTML 레이아웃**:
   - 제목(`title`)은 키워드를 자연스럽게 녹여낸 정교하고 매력적인 수치형/분석형 헤드라인으로 뽑으십시오.
   - 본문(`content_html`)은 모바일 가독성을 극대화하기 위해 `<h2>`, `<p>` 태그 위주로 구성하십시오.
   - 본문 텍스트 스타일: 모든 `<p>` 태그에 `style="line-height: 1.95; font-size: 14.5px; color: #334155; letter-spacing: -0.015em; margin-bottom: 16px;"` 속성을 부여하여 줄간격과 가독성을 확보하십시오.
4. **분량**: 1000자 내외로 풍부하고 전문성 있게 작성하십시오.

# 출력 형식 (JSON)
{"title": "글 제목", "content_html": "<h2>...</h2><p style='...'>...</p>..."}
"""


def generate_trend_image(keyword: str) -> str:
    print(f"[Image] Generating trend image for keyword: {keyword}...")
    prompt = f"{keyword} stock trading corporate financial style, dark background, obsidian black and gold accents, high contrast, clean minimalist design, no text, no words, no letters"
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&private=true"
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=40) as resp:
            img_bytes = resp.read()
            
        upload_url = "https://catbox.moe/user/api.php"
        upload_data = {"reqtype": "fileupload"}
        files = {"fileToUpload": ("image.png", img_bytes, "image/png")}
        print("🤖 Catbox 이미지 호스팅 업로드 중 (Trending)...")
        upload_res = requests.post(upload_url, data=upload_data, files=files, timeout=30)
        if upload_res.status_code == 200 and upload_res.text.startswith("https"):
            url_hosted = upload_res.text.strip()
            print(f"✅ Trending Image + Catbox 성공: {url_hosted}")
            return url_hosted
        else:
            print(f"⚠️ Catbox 업로드 실패: {upload_res.text}")
    except Exception as e:
        print(f"⚠️ 이미지 생성 및 업로드 오류: {e}")
    return ""


def generate_trend_blog(api_key: str, keyword: str, current_date_str: str) -> tuple[str, str] | None:
    primary_ai = os.getenv("PRIMARY_AI", "claude").lower()
    
    def clean_and_add_image(title: str, content_html: str) -> tuple[str, str]:
        # Strip out any <cite> tags but preserve the text inside them
        clean_html = re.sub(r"<cite[^>]*>(.*?)</cite>", r"\1", content_html, flags=re.DOTALL)
        
        # Get image
        img_url = generate_trend_image(keyword)
        
        # Premium CSS and layout wrap
        wrapped_html = f"""<style>
  body {{ font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif; background: #f8fafc; color: #334155; line-height: 1.95; font-size: 14.5px; letter-spacing: -0.015em; }}
  .container {{ max-width: 780px; margin: 0 auto; padding: 0 16px 40px; }}
  h1 {{ font-size: 22px; font-weight: 800; color: #0f172a; line-height: 1.4; margin: 20px 0 8px; }}
  h2 {{ font-size: 17px; font-weight: 700; color: #1e293b; margin: 28px 0 12px; padding-bottom: 6px; border-bottom: 2px solid #e2e8f0; }}
  p {{ margin-bottom: 12px; }}
  .section-card {{ background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
  .disclaimer {{ font-size: 11.5px; color: #94a3b8; background: #f1f5f9; border-radius: 8px; padding: 14px 16px; margin-top: 28px; line-height: 1.7; }}
</style>

<div class="container">
  <!-- ═══ 마스트헤드 ═══ -->
  <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px 18px;margin:16px 0 0;display:flex;flex-wrap:wrap;gap:8px;justify-content:space-between;align-items:center;">
    <div>
      <div style="font-size:11px;color:#64748b;font-weight:600;letter-spacing:0.05em;">멋쟁이 인사이트 TREND BRIEF</div>
      <div style="font-size:18px;font-weight:800;color:#0f172a;">VOL.TREND-{current_date_str.replace("년 ", ".").replace("월 ", ".").replace("일", "").replace(" ", "")}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px;color:#64748b;">{current_date_str}</div>
      <div style="font-size:11px;font-weight:700;color:#1e40af;">실시간 키워드: {keyword}</div>
    </div>
  </div>
"""

        if img_url:
            wrapped_html += f"""
  <!-- ═══ 히어로 이미지 ═══ -->
  <img src="{img_url}" style="width:100%;height:220px;object-fit:cover;border-radius:10px;margin:14px 0 20px;display:block" alt="{keyword} 분석" loading="lazy">
"""

        # Prepend H1 Title inside the body container
        wrapped_html += f"""
  <!-- ═══ H1 헤드라인 ═══ -->
  <h1 style="font-size: 22px; font-weight: 800; color: #0f172a; line-height: 1.4; margin: 20px 0 8px;">{title}</h1>
  <p style="font-size:13px;color:#64748b;margin-bottom:20px;">멋쟁이 인사이트 실시간 트렌드 분석 보고서</p>
"""

        # Wrap content in a section card per H2 block
        sections = re.split(r'(<h2>.*?</h2>)', clean_html)
        content_wrapped = ""
        current_section = ""
        for part in sections:
            if not part.strip():
                continue
            if part.startswith("<h2>"):
                if current_section:
                    content_wrapped += f'<div class="section-card">\n{current_section}\n</div>\n'
                current_section = part
            else:
                current_section += part
        if current_section:
            content_wrapped += f'<div class="section-card">\n{current_section}\n</div>\n'

        wrapped_html += content_wrapped

        # Add Disclaimer and Sources at the bottom
        wrapped_html += f"""
  <!-- ═══ 투자 고지 ═══ -->
  <div class="disclaimer">
    <p style="font-weight:700;color:#475569;margin-bottom:6px;">투자 고지 (Investment Disclaimer)</p>
    <p>본 보고서는 멋쟁이 인사이트의 분석팀이 실시간 트렌드 키워드를 바탕으로 작성한 정보 제공 목적의 콘텐츠입니다. 특정 종목의 매수·매도를 권유하거나 투자 수익을 보장하지 않습니다. 모든 투자 결정은 독자 본인의 판단과 책임하에 이루어져야 하며, 본 보고서의 내용은 투자자의 개별적인 투자 목표, 재무 상황 및 필요에 맞지 않을 수 있습니다.</p>
  </div>
  
  <!-- ═══ 출처 표기 ═══ -->
  <div style="margin-top:20px;font-size:11px;color:#94a3b8;line-height:1.8;">
    <p style="font-weight:700;color:#64748b;">출처 (Sources)</p>
    <p>· 네이버 DataLab 실시간 검색어 트렌드 분석 데이터<br/>
    · Anthropic Claude Web Search 실시간 리서치<br/>
    · 멋쟁이 인사이트 트렌드 분석팀</p>
  </div>
</div>
"""
        return title, wrapped_html

    def run_gemini():
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            raise RuntimeError("GEMINI_API_KEY not found in environment")
        
        gemini_model = "gemini-3.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
        
        combined_text = f"{TREND_BLOG_PROMPT}\n\n오늘 날짜는 {current_date_str}입니다. 오늘 실시간 트렌드 키워드 '{keyword}'에 대한 블로그 글을 작성해줘."
        body = {
            "contents": [{"parts": [{"text": combined_text}]}],
            "tools": [{"googleSearch": {}}],
            "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3}
        }
        
        print(f"[Gemini] 트렌드 블로그 생성 시도 ({keyword})...")
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            
        candidates = res_data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini content empty")
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise RuntimeError("Gemini content parts empty")
        text = parts[0].get("text", "").strip()
        
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            parsed = json.loads(text[start:end+1], strict=False)
            print(f"[Gemini] 트렌드 블로그 생성 성공 ({keyword})")
            return clean_and_add_image(parsed["title"], parsed["content_html"])
        raise RuntimeError("Failed to parse JSON from Gemini response")

    if primary_ai == "gemini":
        try:
            return run_gemini()
        except Exception as e:
            print(f"⚠️ [Gemini] 트렌드 블로그 생성 실패 ({keyword}): {e}. Claude로 백업 시도...")

    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=TREND_BLOG_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}],
            messages=[{"role": "user", "content": f"오늘 날짜는 {current_date_str}입니다. 오늘 실시간 트렌드 키워드 '{keyword}'에 대한 블로그 글을 작성해줘."}],
        )
        text = "\n".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()

        # Robust JSON extraction
        json_str = None
        if "```json" in text:
            try:
                json_str = text.split("```json")[1].split("```")[0].strip()
            except Exception:
                pass
        elif "```" in text:
            try:
                json_str = text.split("```")[1].split("```")[0].strip()
            except Exception:
                pass
                
        if not json_str:
            start, end = text.find("{"), text.rfind("}")
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                
        if json_str:
            data = json.loads(json_str, strict=False)
            print(f"[Claude] 트렌드 블로그 생성 성공 ({keyword})")
            return clean_and_add_image(data["title"], data["content_html"])
        else:
            print(f"⚠️ [Claude] 파싱 실패 원본 텍스트: {text}")
            raise RuntimeError("JSON markers not found in Claude response")
    except Exception as e:
        print(f"⚠️ [Claude] 트렌드 블로그 생성 실패 ({keyword}): {e}")
        if primary_ai != "gemini":
            print("🔄 Gemini 백업 호출 시도...")
            try:
                return run_gemini()
            except Exception as ge:
                print(f"⚠️ [Gemini 백업] 트렌드 블로그 생성 실패 ({keyword}): {ge}")
    return None


def refresh_google_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    payload = {
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_token, "grant_type": "refresh_token",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["access_token"]


def post_to_blogger(blog_id: str, access_token: str, title: str, content: str) -> str | None:
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/?isDraft=false"
    payload = {"title": title, "content": content}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("url")
    except Exception as e:
        print(f"Blogger 발행 실패: {e}")
        return None


def main():
    api_key = os.environ["ANTHROPIC_API_KEY"]
    naver_id = os.environ.get("NAVER_CLIENT_ID", "")
    naver_secret = os.environ.get("NAVER_CLIENT_SECRET", "")
    blog_id = os.environ["BLOG_ID"]
    google_token = refresh_google_token(
        os.environ["GOOGLE_CLIENT_ID"],
        os.environ["GOOGLE_CLIENT_SECRET"],
        os.environ["GOOGLE_REFRESH_TOKEN"]
    )

    # 트렌드 키워드 수집
    keywords = get_trending_keywords(naver_id, naver_secret)
    print(f"오늘의 트렌드 키워드: {keywords}")

    kst = timezone(timedelta(hours=9))
    current_date_str = datetime.now(kst).strftime("%Y년 %m월 %d일")

    results = []
    for keyword in keywords[:3]:  # 상위 3개 키워드만 (비용 절약)
        result = generate_trend_blog(api_key, keyword, current_date_str)
        if result:
            title, content = result
            url = post_to_blogger(blog_id, google_token, title, content)
            results.append({"keyword": keyword, "title": title, "url": url})
            print(f"✅ 발행 완료: {title}")

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
