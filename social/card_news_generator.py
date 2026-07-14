import os, json, datetime, re
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

CARD_SYSTEM = """
당신은 소셜미디어 콘텐츠 전문가입니다.
주식 분석 내용을 바탕으로 인스타그램·유튜브·트위터용 핵심 요약 콘텐츠를 만듭니다.

# 인스타그램 카드뉴스 생성 규칙:
1. 슬라이드 목록("slides")은 4~5개 내외로 작성하세요.
2. 마지막 슬라이드는 반드시 **"멋쟁이의 한줄생각"** 또는 **"멋쟁이 전망/전략"**으로 지정하여, 이번 이슈나 지표를 마주하는 투자자들을 위한 날카롭고 유니크한 통찰이나 액션 플랜을 한 줄로 요약해 작성해 주세요. (단순 기사 요약이 아닌, 분석가로서의 주관적인 조언이 들어가야 합니다.)
3. 모든 슬라이드는 간결하고 모바일에서 한눈에 들어오도록 문장을 압축하세요.

# 중요 JSON 출력 규칙
- 반드시 순수 JSON으로만 출력하세요. 설명이나 마크다운 코드 블록(```json 등)을 포함하지 마세요.
- JSON 내부의 모든 문자열 값에는 이중 따옴표(")를 절대 사용하지 마세요. 강조나 인용이 필요한 경우 반드시 홀따옴표(')나 백틱(`)을 사용하세요.
- 예: "headline": "삼성전자 '급등'의 이유" (O) | "headline": "삼성전자 \"급등\"의 이유" (X)
- 절대 문자열이 도중에 끊기거나(Unterminated string) 구문 오류가 발생하지 않도록 JSON 문법을 완벽히 준수하세요.

# 출력 형식 (JSON)
{
  "instagram_card": {
    "title": "카드뉴스 제목",
    "slides": [
      {"slide_num": 1, "headline": "20자이내 핵심요약", "sub_text": "30자이내 디테일설명"},
      {"slide_num": 2, "headline": "20자이내 핵심요약", "sub_text": "30자이내 디테일설명"},
      {"slide_num": 3, "headline": "20자이내 핵심요약", "sub_text": "30자이내 디테일설명"},
      {"slide_num": 4, "headline": "멋쟁이의 한줄생각", "sub_text": "30자이내 날카로운 투자 통찰/전략"}
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
