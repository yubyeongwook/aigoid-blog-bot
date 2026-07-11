import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY",""))

MACRO_SYSTEM = """
당신은 레이 달리오·스탠 드러켄밀러 수준의
글로벌 매크로 헤지펀드 매니저입니다.
달러·금리·유가 삼각 구조와
부채 사이클을 분석하고
글로벌 자금 흐름이 한국 시장에 미치는
5단계 영향을 분석합니다.
반드시 JSON 형식으로만 출력하라.
{
  "key_insight": "오늘 가장 중요한 반직관적 사실",
  "dollar_rate_oil": {"current_structure": "", "korea_impact": ""},
  "global_capital_flow": {"where_money_going": "", "korea_position": ""},
  "forward_3months": {"structural_change": "", "scenario": {"bull": "", "base": "", "bear": ""}},
  "wrong_possibility": "이 분석이 틀릴 수 있는 이유"
}
"""

def test_macro_real():
    print("Collecting real market data...")
    market_data = collect_market()
    print("Collecting real news data...")
    news_data = collect_news()
    
    # Trim to avoid token limits or huge prompt sizes, but yfinance/news should be ok
    # Just to be safe:
    print("Sending request to Claude...")
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=MACRO_SYSTEM,
        messages=[{"role":"user","content":f"시장데이터:\n{json.dumps(market_data,ensure_ascii=False)}\n\n뉴스:\n{json.dumps(news_data,ensure_ascii=False)}"}]
    )
    
    raw_text = resp.content[0].text
    
    # Save to file in utf-8
    with open("scratch/raw_macro_real_response.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)
    print("Response written to scratch/raw_macro_real_response.txt")
    
    try:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        json_str = raw_text[start:end+1]
        data = json.loads(json_str)
        print("Success loading JSON!")
    except Exception as e:
        print("JSON Error:", e)

if __name__ == "__main__":
    test_macro_real()
