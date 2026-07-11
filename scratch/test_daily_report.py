import sys, os, json, datetime
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from collectors.market_collector import collect_all as collect_market
from collectors.news_collector import collect_all as collect_news
from generators.report_generator import generate_daily_report

def main():
    print("Market collecting...")
    market_data = collect_market()
    print("US ETFs collected:", json.dumps(market_data.get("us_etfs"), indent=2))
    
    print("News collecting...")
    news_data = collect_news()
    print("US features news collected:", json.dumps(news_data.get("macro_news", {}).get("미국증시_특징주"), indent=2))
    
    print("Generating report...")
    html = generate_daily_report(market_data, news_data)
    
    # Save the output HTML
    out_path = os.path.abspath(os.path.dirname(__file__) + '/test_daily_report.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Report generated successfully. Saved to: {out_path}")

if __name__ == "__main__":
    main()
