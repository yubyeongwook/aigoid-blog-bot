# -*- coding: utf-8 -*-
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

# Read dummy or real agent data if we have it, or we can mock it
# Actually, let's just make a dummy call to see what Claude outputs in raw_text

def test_synthesis_raw():
    # Let's read from the latest run's inputs or mock
    # To be quick, let's mock the inputs
    macro = {"key_insight": "매크로 인사이트"}
    supply = {"market_supply": {"smart_money_signal": "수급 신호"}}
    earnings = {"hidden_gems": []}
    technical = {"momentum_stocks": []}
    market_data = {}
    
    from agents.synthesis_agent import SYNTHESIS_SYSTEM
    
    prompt = f"""
오늘: 2026년 07월 11일 토요일 (KST)

=== 매크로 전문가 분석 ===
{json.dumps(macro, ensure_ascii=False, indent=2)}

=== 수급 전문가 분석 ===
{json.dumps(supply, ensure_ascii=False, indent=2)}

=== 실적·공시 전문가 분석 ===
{json.dumps(earnings, ensure_ascii=False, indent=2)}

=== 기술적 전문가 분석 ===
{json.dumps(technical, ensure_ascii=False, indent=2)}

=== 원본 시장 데이터 ===
{json.dumps(market_data, ensure_ascii=False, indent=2)}

위 4개 전문가 분석을 종합해서 독서 편의성과 세련미를 극대화한 세계 최고 헤지펀드 수준의 블로그 리포트를 HTML 형식으로 작성하라.
본문은 <div> 태그만을 사용하고 명시된 인라인 CSS 스타일 가이드를 철저히 따를 것.
"""
    print("Calling Claude...")
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYNTHESIS_SYSTEM,
        messages=[{"role":"user","content":prompt}]
    )
    raw_text = resp.content[0].text
    with open("scratch/synthesis_raw_response.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)
    print("Saved to scratch/synthesis_raw_response.txt")
    print("Raw text length:", len(raw_text))

if __name__ == "__main__":
    test_synthesis_raw()
