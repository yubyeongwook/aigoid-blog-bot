import sys
import os
import json
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from collectors.market_collector import collect_all

def main():
    load_dotenv()
    print("Collecting market data...")
    data = collect_all()
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
