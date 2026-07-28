import sys, os, json
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

# Monkeypatch first
import agents.patch_anthropic

from collectors.market_collector import collect_premarket_data as collect_market
from collectors.news_collector import collect_all as collect_news
from agents.premarket_synthesis_agent import generate_premarket_report
from publishers.blogger_publisher import get_latest_morning_brief

def main():
    print("Collecting premarket data...")
    market_data = collect_market()
    print("Collecting news...")
    news_data = collect_news()
    print("Getting latest morning brief...")
    morning_brief = get_latest_morning_brief()
    if morning_brief:
        print(f"Loaded morning brief: {morning_brief.get('title')}")
    else:
        print("No morning brief found")

    print("\nGenerating premarket report...")
    html_content = generate_premarket_report(
        premarket_data={**market_data, "morning_brief": morning_brief},
        news_data=news_data
    )
    
    print("\nResult HTML length:", len(html_content))
    with open("scratch/test_premarket_result.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Saved generated premarket report to scratch/test_premarket_result.html")

if __name__ == "__main__":
    main()
