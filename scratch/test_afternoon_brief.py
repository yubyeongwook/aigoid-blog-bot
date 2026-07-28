import sys
import os
import json
from dotenv import load_dotenv

# Ensure stdout is UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

# Import the monkeypatch first
import agents.patch_anthropic

from agents.afternoon_synthesis_agent import generate_afternoon_report
from social.card_news_generator import generate as generate_social

def main():
    print("Starting dry-run verification for afternoon brief generation...")
    
    # Dummy data
    market_data = {
        "kospi": {"close": "2600.00", "change": "+10.00", "change_rate": "+0.38%"},
        "kosdaq": {"close": "850.00", "change": "-2.00", "change_rate": "-0.23%"},
        "foreign_net": "+1500억",
        "institution_net": "-500억",
        "surging_stocks": [
            {"name": "삼성전자", "ticker": "005930", "close": 78000, "rate": 3.5, "pull_back_rate": 0.5}
        ]
    }
    news_data = {
        "market_news": ["코스피, 반도체 강세에 상승 마감", "외국인 순매수 유입 지속"],
        "disclosures": [{"title": "삼성전자 분기 실적 발표", "url": "http://example.com"}]
    }
    morning_brief_data = {
        "title": "07월 14일 화요일 멋쟁이 인사이트",
        "content": "오전 브리핑 내용 요약..."
    }
    evaluated_picks = [
        {"ticker": "005930", "name": "삼성전자", "entry": 77000, "target": 80000, "stop": 75000, "actual_high": 78500, "actual_close": 78000, "actual_rate": 1.3, "status": "수익 마감 (성공)"}
    ]
    
    # 1. Test generate_afternoon_report
    print("\n--- 1. Testing generate_afternoon_report (Should use patched Gemini) ---")
    try:
        html = generate_afternoon_report(market_data, news_data, morning_brief_data, evaluated_picks)
        print("Success! HTML Content length:", len(html))
        print("HTML starts with:\n", html[:300])
    except Exception as e:
        print("Error during generate_afternoon_report:", e)
        sys.exit(1)
        
    # 2. Test generate_social (card news)
    print("\n--- 2. Testing generate_social (Should use patched Gemini) ---")
    try:
        social = generate_social(html, [], "오늘 코스피 마감 브리핑", "http://example.com/blog-post")
        print("Success! Social Content Keys:", list(social.keys()))
        print("Social content summary:\n", json.dumps(social, ensure_ascii=False, indent=2)[:500])
    except Exception as e:
        print("Error during generate_social:", e)
        sys.exit(1)

    print("\nVerification completed successfully!")

if __name__ == "__main__":
    main()
