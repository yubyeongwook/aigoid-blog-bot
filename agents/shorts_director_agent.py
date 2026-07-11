import os, json, re
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

SHORTS_DIRECTOR_SYSTEM = """
당신은 유튜브 쇼츠(YouTube Shorts) 전문 총괄 편집장(Director)입니다.
오늘 발행된 블로그 포스팅 본문과 픽 추천 종목들을 분석하여 1분(60초) 이내의 임팩트 있는 쇼츠 기획서(스토리보드)를 작성합니다.
반드시 JSON 형식으로만 응답해야 합니다.

출력 포맷 스키마:
{
  "title": "쇼츠 제목",
  "scenes": [
    {
      "scene_num": 1,
      "narration": "성우가 읽을 씬 나레이션 멘트 (자연스러운 한국어 구어체, 20자~40자 내외)",
      "visual_concept": "화면에 띄울 시각 이미지의 상세 프롬프트 및 컨셉 (예: 'KOSPI chart', 'Samsung Electronics stock price graph', 'soaring chart with bullish arrows')",
      "text_overlay": "화면에 크게 표시할 자막 (15자 이내, 임팩트 있는 문구)"
    }
  ]
}
씬은 4~5개 정도로 나누어 총 재생 시간이 45~55초 사이가 되도록 설계해 주세요.
"""

def generate_shorts_script(blog_html: str, picks: list) -> dict:
    print("🎬 쇼츠 총괄 편집장 에이전트 기획서 제작 시작...")
    
    # HTML 태그 제거 및 텍스트 간소화
    text_content = re.sub(r'<[^>]+>', ' ', blog_html)
    text_content = ' '.join(text_content.split())[:1200]
    
    picks_summary = "\n".join([
        f"- {p.get('type','단타')}: {p.get('name','')} (진입가 {p.get('entry_price', 0):,})"
        for p in picks[:3]
    ])

    prompt = f"""
[블로그 본문 요약]
{text_content}

[추천 픽 정보]
{picks_summary}

위 정보를 활용하여 개인 투자자들의 흥미를 자극하고 블로그 유입을 유도할 수 있는 쇼츠 대본(기획서)을 작성해라.
반드시 제공한 JSON 스키마로만 정밀하게 응답하라.
"""

    model_name = "claude-3-5-sonnet-20241022"  # 실제 유효한 모델명 사용
    try:
        resp = client.messages.create(
            model=model_name,
            max_tokens=2000,
            system=SHORTS_DIRECTOR_SYSTEM,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip()
        
        # JSON 블록 추출 파싱
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        script_data = json.loads(text)
        print(f"✅ 쇼츠 기획서 생성 완료: {script_data.get('title', '제목 없음')}")
        return script_data
    except Exception as e:
        print(f"쇼츠 편집장 에이전트 기획 오류: {e}")
        # 기본 기획서 반환 fallback
        return {
            "title": "오늘 주목해야 할 급등 추천 종목",
            "scenes": [
                {
                    "scene_num": 1,
                    "narration": "오늘 주식시장에서 반드시 체크해야 할 종목들을 빠르게 전해드립니다.",
                    "visual_concept": "Bullish financial chart with upward arrows",
                    "text_overlay": "오늘 급등 후보 종목"
                },
                {
                    "scene_num": 2,
                    "narration": "첫 번째 종목은 시장 수급이 유입되고 있는 이 종목입니다.",
                    "visual_concept": "Stock analysis bar graph",
                    "text_overlay": "수급 유입 포착"
                },
                {
                    "scene_num": 3,
                    "narration": "보다 상세한 차트 분석과 대응 전략은 댓글 링크를 참조해 주세요.",
                    "visual_concept": "Laptop displaying a stock blog article",
                    "text_overlay": "전체 분석 링크 확인"
                }
            ]
        }
