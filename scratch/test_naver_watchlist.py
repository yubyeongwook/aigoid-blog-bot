import requests
from bs4 import BeautifulSoup
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def check_item(code, name):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    res = requests.get(url, headers=HEADERS, timeout=10)
    # Naver Finance is euc-kr encoded
    soup = BeautifulSoup(res.content, "html.parser", from_encoding="euc-kr")
    
    price_el = soup.select_one(".no_today")
    if price_el:
        print(f"=== {name} ({code}) ===")
        print("Raw price_el text:")
        print(repr(price_el.text.strip()))
        print("Raw price_el HTML:")
        print(price_el.prettify())
        
        blind_el = price_el.select_one(".blind")
        if blind_el:
            print("Blind element text:", repr(blind_el.text.strip()))
            
        # Check no_exday
        exday_el = soup.select_one(".no_exday")
        if exday_el:
            print("Exday element text:", repr(exday_el.text.strip()))
            print("Exday HTML:")
            print(exday_el.prettify())
            
check_item("005930", "삼성전자")
check_item("000660", "SK하이닉스")
