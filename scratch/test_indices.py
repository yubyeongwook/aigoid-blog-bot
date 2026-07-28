import sys
import os
import json
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from collectors.market_collector import get_index_pykrx, get_index_naver

def main():
    print("get_index_naver():")
    print(json.dumps(get_index_naver(), indent=2))
    print("\nget_index_pykrx():")
    print(json.dumps(get_index_pykrx(), indent=2))

if __name__ == "__main__":
    main()
