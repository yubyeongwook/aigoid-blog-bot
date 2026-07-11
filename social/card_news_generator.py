import os, json, datetime, re
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

CARD_SYSTEM = """
당신은 소셜미디어 콘텐츠 전문가입니다.
주식 분석을 인스타그램·유튜브·트위터용으로 변환합니다.
반드시 JSON으로만 출력:
{
  "instagram_card": {
    "title": "카드뉴스 제목",
    "slides": [
      {"slide_num": 1, "headline": "20자이내", "sub_text": "30자이내"}
    ],
    "hashtags": ["#코스피", "#주식", "#멋쟁이인사이트"]
  },
  "youtube_shorts": {
    "title": "쇼츠 제목",
    "hook": "첫 3초 멘트",
    "script": "60초 스크립트",
    "thumbnail_text": "썸네일 텍스트"
  },
  "twitter_thread": ["트윗1", "트윗2", "트윗3"]
}
"""

def generate(blog_html, picks, key_insight, blog_url) -> dict:
    print("📱 소셜 콘텐츠 생성 중...")
    text = re.sub(r'<[^>]+>', ' ', blog_html)
    text = ' '.join(text.split())[:1000]
    pick_summary = "\n".join([
        f"- {p.get('type','')}: {p.get('name','')} 진입{p.get('entry_price',0):,}/손절{p.get('stop_loss',0):,}"
        for p in picks[:3] if p.get('entry_price', 0) > 0
    ])
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=CARD_SYSTEM,
            messages=[{"role":"user","content":f"인사이트: {key_insight}\n픽: {pick_summary}\n블로그: {blog_url}\n내용: {text}"}]
        )
        text = resp.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(text)
    except Exception as e:
        print(f"소셜 생성 오류: {e}")
        return {"error": str(e)}

def save_social_content(content, date_str=None):
    if not date_str:
        date_str = datetime.datetime.now().strftime("%Y%m%d")
    os.makedirs("social_content", exist_ok=True)
    filepath = f"social_content/{date_str}_social.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print(f"✅ 소셜 콘텐츠 저장: {filepath}")
    return filepath
