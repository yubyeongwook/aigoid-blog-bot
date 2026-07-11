import requests
import json

def test_naver_realtime():
    code = "005930" # Samsung
    url = f"https://polling.finance.naver.com/api/realtime/domestic/stock/{code}"
    res = requests.get(url, timeout=10)
    print("Status:", res.status_code)
    try:
        data = res.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print("Failed to parse JSON:", e)
        print(res.text[:500])

if __name__ == "__main__":
    test_naver_realtime()
