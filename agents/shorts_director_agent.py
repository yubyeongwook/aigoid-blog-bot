import os, json, re
from anthropic import Anthropic
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

SHORTS_DIRECTOR_SYSTEM = """
당신은 멋쟁이 인사이트의 수석 쇼츠 총괄 디렉터(Chief Shorts Director)이자 유튜브 쇼츠, 인스타그램 릴스 등 숏폼 콘텐츠 기획 및 바이럴 마케팅 최고 전문가입니다.
오늘 작성된 고품격 블로그 포스트 본문과 멋쟁이 픽 종목들을 면밀히 분석하여, 대중의 이목을 3초 만에 사로잡고 엄청난 조회수를 유도할 수 있는 1분(60초) 이내의 고품격 쇼츠 스토리보드 기획서를 완성합니다.

출력은 반드시 유효한 JSON 형식이어야 합니다.
시청 이탈을 최소화하고 높은 완성도의 자막, 비주얼, 대본을 제공하십시오.

출력 포맷 스키마:
{
  "title": "시청자의 후킹을 유도할 수 있는 쇼츠 콘텐츠 제목",
  "scenes": [
    {
      "scene_num": 1,
      "narration": "쇼츠 나레이션용 구어체 성우 대본 (자연스럽고 긴장감 넘치는 한국어 톤, 20-40자)",
      "visual_concept": "화면에 연출될 시각 이미지/동영상 상세 묘사 및 이미지 생성용 영문 프롬프트 (예: 'KOSPI chart falling down dramatically, realistic finance background, 4k')",
      "text_overlay": "화면에 눈에 띄게 배치할 모바일 세로형 핵심 자막 문구 (15자 이내, 강렬하고 직관적)"
    }
  ]
}
씬은 4~5개 정도로 구성하여 전체 분량이 45초에서 55초 사이에 최적화되도록 조절하십시오.
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
