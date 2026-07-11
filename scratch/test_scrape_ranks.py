import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def test_scrape():
    # Test sise_quant (Volume ranking)
    url_quant = "https://finance.naver.com/sise/sise_quant.naver?sosok=0"
    res = requests.get(url_quant, headers=HEADERS, timeout=10)
    res.encoding = "euc-kr"
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.select_one("table.type_2")
    print("=== KOSPI Volume Ranking ===")
    if table:
        count = 0
        for row in table.select("tr"):
            a_tag = row.select_one("td a.tltle")
            if a_tag:
                name = a_tag.text.strip()
                code = a_tag['href'].split('code=')[-1].strip()
                print(f"{count+1}. {name} ({code})")
                count += 1
                if count >= 5:
                    break
    
    # Test sise_low_up (Surging ranking)
    url_low_up = "https://finance.naver.com/sise/sise_low_up.naver?sosok=0"
    res = requests.get(url_low_up, headers=HEADERS, timeout=10)
    res.encoding = "euc-kr"
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.select_one("table.type_2")
    print("\n=== KOSPI Surging Ranking ===")
    if table:
        count = 0
        for row in table.select("tr"):
            a_tag = row.select_one("td a.tltle")
            if a_tag:
                name = a_tag.text.strip()
                code = a_tag['href'].split('code=')[-1].strip()
                print(f"{count+1}. {name} ({code})")
                count += 1
                if count >= 5:
                    break

if __name__ == "__main__":
    test_scrape()
