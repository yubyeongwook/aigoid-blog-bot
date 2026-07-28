import requests
from bs4 import BeautifulSoup
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def main():
    url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.content, "html.parser", from_encoding="euc-kr")
    
    now = soup.select_one("#now_value")
    val_rate_el = soup.select_one("#change_value_and_rate")
    
    print("=== KOSPI NOW VALUE ===")
    if now:
        print("HTML:", now.prettify())
        print("Text:", repr(now.text.strip()))
    else:
        print("KOSPI #now_value not found!")
        
    print("=== KOSPI CHANGE VALUE AND RATE ===")
    if val_rate_el:
        print("HTML:", val_rate_el.prettify())
        print("Text:", repr(val_rate_el.text.strip()))
    else:
        print("KOSPI #change_value_and_rate not found!")

if __name__ == "__main__":
    main()
