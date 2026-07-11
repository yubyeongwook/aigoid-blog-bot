import os, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from collectors.market_collector import collect_premarket_data
from generators.report_generator import generate_premarket_report

def main():
    print("=== Testing Premarket Data Collection ===")
    data = collect_premarket_data()
    
    print("\nCollected active_volume_stocks:")
    for i, stock in enumerate(data.get("active_volume_stocks", [])):
        print(f"{i+1}. {stock['name']} ({stock['code']}) - Market: {stock['market_type']}, Price: {stock['price']}, Change: {stock['change_pct']}, Volume: {stock['volume']}, Over Volume: {stock['over_volume']}")
        
    print("\n=== Testing Premarket Report Generation ===")
    # Generate draft report (won't publish)
    html = generate_premarket_report(data)
    print("Draft generated successfully! Length:", len(html))
    
    # Save a snippet of Section III to check if it's there
    with open("scratch/premarket_draft.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to scratch/premarket_draft.html")

if __name__ == "__main__":
    main()
