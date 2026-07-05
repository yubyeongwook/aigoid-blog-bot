"""
market_collector.py — 시장 데이터 수집
pykrx + 네이버 금융 (장 마감 여부 자동 감지 및 셀렉터 보정 완료)
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from pykrx import stock
import requests, pandas as pd, datetime, os, json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def get_dates():
    today = datetime.datetime.now()
    # 최근 거래일 찾기 (주말 제외)
    d = today
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    last_trading = d.strftime("%Y%m%d")
    week_ago = (d - datetime.timedelta(days=7)).strftime("%Y%m%d")
    return today, week_ago, last_trading

# ────────────────────────────────
# 네이버 금융으로 지수 수집 (안정적)
# ────────────────────────────────
def get_index_naver():
    result = {}
    try:
        for code, name in [("KOSPI", "kospi"), ("KOSDAQ", "kosdaq")]:
            url = f"https://finance.naver.com/sise/sise_index.naver?code={code}"
            res = requests.get(url, headers=HEADERS, timeout=10)
            res.encoding = "euc-kr"
            soup = BeautifulSoup(res.text, "html.parser")
            now = soup.select_one("#now_value")
            val_rate_el = soup.select_one("#change_value_and_rate")
            
            if now:
                close_val = now.text.strip().replace(",","")
                change_val = "0"
                rate_val = "0%"
                
                if val_rate_el:
                    diff_span = val_rate_el.select_one("span")
                    change_val = diff_span.text.strip() if diff_span else "0"
                    
                    full_text = val_rate_el.text.strip()
                    parts = full_text.split()
                    if len(parts) >= 2:
                        rate_val = parts[1]
                        
                    direction = ""
                    blind_span = val_rate_el.select_one(".blind")
                    if blind_span:
                        dir_text = blind_span.text.strip()
                        rate_val = rate_val.replace(dir_text, "").strip()
                        if "하락" in dir_text or "하한" in dir_text:
                            direction = "-"
                        elif "상승" in dir_text or "상한" in dir_text:
                            direction = "+"
                            
                    if not rate_val.startswith("-") and not rate_val.startswith("+"):
                        rate_val = direction + rate_val
                
                result[name] = {
                    "close": close_val,
                    "change": change_val,
                    "change_pct": rate_val
                }
    except Exception as e:
        result["error"] = str(e)
    return result

# ────────────────────────────────
# pykrx로 지수 수집 (보조)
# ────────────────────────────────
def get_index_pykrx():
    today, week_ago, last_trading = get_dates()
    result = {}
    try:
        import warnings
        warnings.filterwarnings('ignore')
        
        kospi = stock.get_index_ohlcv(week_ago, last_trading, "1001")
        kosdaq = stock.get_index_ohlcv(week_ago, last_trading, "2001")

        if kospi.empty or kosdaq.empty:
            raise ValueError("pykrx returned empty index data")

        if not kospi.empty:
            lk = kospi.iloc[-1]
            pk = kospi.iloc[-2] if len(kospi) >= 2 else lk
            chg = lk["종가"] - pk["종가"]
            result["kospi"] = {
                "close": round(lk["종가"], 2),
                "change": round(chg, 2),
                "change_pct": round(chg/pk["종가"]*100, 2),
                "volume": int(lk["거래량"]),
                "date": last_trading
            }
            if len(kospi) >= 5:
                ws = kospi.iloc[-5]["종가"]
                we = kospi.iloc[-1]["종가"]
                result["kospi"]["weekly_pct"] = round((we-ws)/ws*100, 2)
                result["kospi"]["weekly_start"] = round(ws, 2)

        if not kosdaq.empty:
            lq = kosdaq.iloc[-1]
            pq = kosdaq.iloc[-2] if len(kosdaq) >= 2 else lq
            chg_q = lq["종가"] - pq["종가"]
            result["kosdaq"] = {
                "close": round(lq["종가"], 2),
                "change": round(chg_q, 2),
                "change_pct": round(chg_q/pq["종가"]*100, 2)
            }
    except Exception as e:
        result["pykrx_error"] = str(e)
        # 네이버로 대체
        result.update(get_index_naver())
    return result

# ────────────────────────────────
# 투자자별 수급 (네이버)
# ────────────────────────────────
def get_investor_naver():
    result = {"daily": {}, "weekly": {}}
    try:
        today, week_ago, last_trading = get_dates()
        url = f"https://finance.naver.com/sise/investorDealTrendDay.nhn?bizdate={last_trading}&sosok=&page=1"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        
        table = soup.select_one("table.type_1")
        if not table:
            return result
            
        rows = table.select("tr")
        daily_done = False
        foreign_w = inst_w = indiv_w = 0
        count = 0
        
        for row in rows:
            tds = row.select("td")
            if len(tds) >= 4:
                date = tds[0].text.strip()
                if date and len(date) == 8 and date[2] == '.' and date[5] == '.':
                    try:
                        p = int(tds[1].text.strip().replace(",","").replace("+",""))
                        f = int(tds[2].text.strip().replace(",","").replace("+",""))
                        i = int(tds[3].text.strip().replace(",","").replace("+",""))
                        
                        if not daily_done:
                            result["daily"] = {"foreign": f, "institution": i, "individual": p, "date": date}
                            daily_done = True
                            
                        if count < 5:
                            foreign_w += f
                            inst_w += i
                            indiv_w += p
                            count += 1
                    except: pass
        result["weekly"] = {"foreign": foreign_w, "institution": inst_w, "individual": indiv_w}
    except Exception as e:
        result["error"] = str(e)
    return result

# ────────────────────────────────
# 상한가·급등 종목 (네이버)
# ────────────────────────────────
def get_upper_limit_naver():
    result = {"kospi": [], "kosdaq": []}
    try:
        # 1. 상한가 종목 수집 (sise_upper.naver)
        url_upper = "https://finance.naver.com/sise/sise_upper.naver?sosok=0"
        res = requests.get(url_upper, headers=HEADERS, timeout=10)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        tables = soup.select("table.type_5")
        
        # 코스피 상한가
        if len(tables) > 0:
            for row in tables[0].select("tr"):
                a_tag = row.select_one("td a")
                tds = row.select("td")
                if a_tag and len(tds) >= 7:
                    result["kospi"].append({
                        "name": a_tag.text.strip(),
                        "price": tds[4].text.strip(),
                        "change_pct": tds[6].text.strip(),
                        "type": "상한가"
                    })
        # 코스닥 상한가
        if len(tables) > 1:
            for row in tables[1].select("tr"):
                a_tag = row.select_one("td a")
                tds = row.select("td")
                if a_tag and len(tds) >= 7:
                    result["kosdaq"].append({
                        "name": a_tag.text.strip(),
                        "price": tds[4].text.strip(),
                        "change_pct": tds[6].text.strip(),
                        "type": "상한가"
                    })
                    
        # 2. 급등 종목 수집 (sise_rise.naver)
        for sosok, key in [("0", "kospi"), ("1", "kosdaq")]:
            url_rise = f"https://finance.naver.com/sise/sise_rise.naver?sosok={sosok}"
            res_rise = requests.get(url_rise, headers=HEADERS, timeout=10)
            res_rise.encoding = "euc-kr"
            soup_rise = BeautifulSoup(res_rise.text, "html.parser")
            table_rise = soup_rise.select_one("table.type_2")
            if table_rise:
                count = 0
                for row in table_rise.select("tr"):
                    a_tag = row.select_one("td a.tltle")
                    tds = row.select("td")
                    if a_tag and len(tds) >= 5:
                        name = a_tag.text.strip()
                        # 중복 제거
                        if any(item["name"] == name for item in result[key]):
                            continue
                            
                        price = tds[2].text.strip()
                        rate = tds[4].text.strip()
                        
                        result[key].append({
                            "name": name,
                            "price": price,
                            "change_pct": rate,
                            "type": "급등"
                        })
                        count += 1
                        if count >= 10:
                            break
    except Exception as e:
        result["error"] = str(e)
    return result

# ────────────────────────────────
# 관심 종목 (네이버)
# ────────────────────────────────
WATCHLIST = [
    ("005930", "삼성전자"), ("000660", "SK하이닉스"),
    ("042700", "한미반도체"), ("089030", "테크윙"),
    ("007660", "이수페타시스"), ("010120", "LS ELECTRIC"),
    ("267260", "HD현대일렉트릭"), ("298040", "효성중공업"),
    ("042660", "한화오션"), ("003490", "대한항공"),
    ("272450", "진에어"), ("105560", "KB금융"),
    ("086790", "하나금융지주"), ("058470", "리노공업"),
    ("307750", "국전약품"),
]

def get_watchlist_naver():
    result = []
    for code, name in WATCHLIST:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={code}"
            res = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.content, "html.parser", from_encoding="euc-kr")
            
            price_el = soup.select_one(".no_today")
            if price_el:
                price_val = price_el.select_one(".blind").text.strip().replace(",", "")
                
                no_exday = soup.select_one(".no_exday")
                rate_val = "0%"
                if no_exday:
                    blind_elements = no_exday.select(".blind")
                    if len(blind_elements) >= 2:
                        rate_val = blind_elements[1].text.strip()
                        if no_exday.select_one(".ico.minus") or no_exday.select_one(".no_down"):
                            rate_val = "-" + rate_val
                        else:
                            rate_val = "+" + rate_val
                        rate_val = rate_val + "%"
                
                result.append({
                    "ticker": code,
                    "name": name,
                    "price": price_val,
                    "change_pct": rate_val
                })
        except: pass
    return result

# ────────────────────────────────
# 장전 동시호가 데이터 수집
# ────────────────────────────────
def get_us_futures():
    futures = {}
    for symbol, name in [("NQ=F", "nasdaq_futures"), ("ES=F", "sp_futures")]:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=10)
            data = res.json()
            meta = data['chart']['result'][0]['meta']
            price = meta.get('regularMarketPrice')
            prev_close = meta.get('previousClose')
            if price and prev_close:
                chg = price - prev_close
                chg_pct = round(chg / prev_close * 100, 2)
                futures[name] = {
                    "price": price,
                    "change": round(chg, 2),
                    "change_pct": f"{chg_pct:+.2f}%" if chg_pct >= 0 else f"{chg_pct:.2f}%"
                }
        except Exception as e:
            futures[name] = {"error": str(e)}
    return futures

def get_premarket_popular_search_naver():
    result = []
    try:
        url = "https://finance.naver.com/sise/lastsearch2.naver"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.select_one("table.type_5")
        if table:
            count = 0
            for row in table.select("tr"):
                a_tag = row.select_one("td a.tltle")
                tds = row.select("td")
                if a_tag and len(tds) >= 6:
                    name = a_tag.text.strip()
                    code = a_tag['href'].split('code=')[-1].strip()
                    price = tds[3].text.strip()
                    
                    # 상승/하락 기호 파악
                    change_pct = "0%"
                    rate_td = tds[5]
                    if rate_td:
                        raw_rate = rate_td.text.strip()
                        direction = ""
                        blind = rate_td.select_one(".blind")
                        if blind:
                            dir_text = blind.text.strip()
                            raw_rate = raw_rate.replace(dir_text, "").strip()
                            if "하락" in dir_text or "하한" in dir_text:
                                direction = "-"
                            elif "상승" in dir_text or "상한" in dir_text:
                                direction = "+"
                        if not raw_rate.startswith("-") and not raw_rate.startswith("+"):
                            raw_rate = direction + raw_rate
                        change_pct = raw_rate
                        
                    result.append({
                        "code": code,
                        "name": name,
                        "price": price,
                        "change_pct": change_pct
                    })
                    count += 1
                    if count >= 10:
                        break
    except Exception as e:
        print(f"인기 검색어 수집 실패: {e}")
    return result

def collect_premarket_data():
    print("📊 장전 동시호가 데이터 수집 시작...")
    today, week_ago, last_trading = get_dates()
    
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "is_weekend": datetime.datetime.now().weekday() >= 5,
        "us_futures": get_us_futures(),
        "index_indicative": get_index_naver(),
        "watchlist_indicative": get_watchlist_naver(),
        "popular_search_indicative": get_premarket_popular_search_naver()
    }
    print("✅ 장전 동시호가 데이터 수집 완료")
    return data

# ────────────────────────────────
# 전체 수집
# ────────────────────────────────
def collect_all():
    print("📊 시장 데이터 수집 시작...")
    today, week_ago, last_trading = get_dates()
    
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "last_trading_day": last_trading,
        "is_weekend": datetime.datetime.now().weekday() >= 5,
        "index": get_index_pykrx(),
        "investor": get_investor_naver(),
        "upper_limit": get_upper_limit_naver(),
        "watchlist": get_watchlist_naver()
    }
    print("✅ 시장 데이터 수집 완료")
    return data

if __name__ == "__main__":
    data = collect_all()
    print(json.dumps(data, ensure_ascii=False, indent=2))
