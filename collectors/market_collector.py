"""
market_collector.py — 시장 데이터 수집
pykrx + 네이버 금융 (장 마감 여부 자동 감지 및 셀렉터 보정 완료)
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from pykrx import stock
import requests, pandas as pd, datetime, os, json
import yfinance as yf
import FinanceDataReader as fdr
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

def get_premarket_active_stocks():
    print("📈 장전 체결물량 유입 상위 종목 수집...")
    target_urls = [
        "https://finance.naver.com/sise/sise_quant.naver?sosok=0", # KOSPI 거래량
        "https://finance.naver.com/sise/sise_quant.naver?sosok=1", # KOSDAQ 거래량
        "https://finance.naver.com/sise/sise_low_up.naver?sosok=0", # KOSPI 상승률
        "https://finance.naver.com/sise/sise_low_up.naver?sosok=1"  # KOSDAQ 상승률
    ]
    
    codes = []
    seen = set()
    
    for url in target_urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            res.encoding = "euc-kr"
            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.select_one("table.type_2")
            if table:
                count = 0
                for row in table.select("tr"):
                    a_tag = row.select_one("td a.tltle")
                    if a_tag:
                        code = a_tag['href'].split('code=')[-1].strip()
                        if code not in seen:
                            seen.add(code)
                            codes.append(code)
                        count += 1
                        if count >= 8:
                            break
        except Exception as e:
            print(f"⚠️ Active stock list fetch failed for {url}: {e}")
            
    result = []
    # 최대 25개 종목만 실시간 API 조회 진행 (레이턴시 및 차단 방지)
    for code in codes[:25]:
        try:
            api_url = f"https://polling.finance.naver.com/api/realtime/domestic/stock/{code}"
            res = requests.get(api_url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if "datas" in data and len(data["datas"]) > 0:
                    item = data["datas"][0]
                    
                    volume = item.get("accumulatedTradingVolumeRaw", "0")
                    over_info = item.get("overMarketPriceInfo")
                    over_volume = "0"
                    if over_info:
                        over_volume = over_info.get("accumulatedTradingVolumeRaw", "0")
                        
                    price = item.get("closePriceRaw", "0")
                    change_pct = item.get("fluctuationsRatioRaw", "0.0")
                    
                    result.append({
                        "code": code,
                        "name": item.get("stockName", "알 수 없음"),
                        "price": price,
                        "change_pct": f"{float(change_pct):+.2f}%" if change_pct else "0.00%",
                        "volume": int(volume) if volume else 0,
                        "over_volume": int(over_volume) if over_volume else 0,
                        "market_type": item.get("stockExchangeType", {}).get("name", "KOSPI")
                    })
        except Exception as e:
            print(f"⚠️ Error fetching realtime data for code {code}: {e}")
            
    # 거래량 및 시간외 거래량 중 큰 값 기준으로 내림차순 정렬
    result.sort(key=lambda x: max(x["volume"], x["over_volume"]), reverse=True)
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
        "popular_search_indicative": get_premarket_popular_search_naver(),
        "active_volume_stocks": get_premarket_active_stocks()
    }
    print("✅ 장전 동시호가 데이터 수집 완료")
    return data

# ────────────────────────────────
# 미국 업종별 ETF 수집
# ────────────────────────────────
def get_us_etfs():
    symbols = [
        ("SOXX", "Semiconductor"),
        ("XLK", "Technology"),
        ("XBI", "Biotech"),
        ("XLE", "Energy"),
        ("XLF", "Financial"),
        ("QQQ", "Nasdaq_ETF"),
        ("SPY", "SP500_ETF")
    ]
    etfs = {}
    for symbol, name in symbols:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=10)
            data = res.json()
            result = data['chart']['result'][0]
            meta = result['meta']
            
            # Extract closing prices
            closes = result['indicators']['quote'][0]['close']
            closes = [c for c in closes if c is not None]
            
            if len(closes) >= 2:
                price = closes[-1]
                prev_close = closes[-2]
                chg = price - prev_close
                chg_pct = round(chg / prev_close * 100, 2)
                etfs[name] = {
                    "symbol": symbol,
                    "price": round(price, 2),
                    "change": round(chg, 2),
                    "change_pct": f"{chg_pct:+.2f}%" if chg_pct >= 0 else f"{chg_pct:.2f}%",
                    "raw_change_pct": chg_pct
                }
            else:
                price = meta.get('regularMarketPrice')
                prev_close = meta.get('chartPreviousClose')
                if price and prev_close:
                    chg = price - prev_close
                    chg_pct = round(chg / prev_close * 100, 2)
                    etfs[name] = {
                        "symbol": symbol,
                        "price": round(price, 2),
                        "change": round(chg, 2),
                        "change_pct": f"{chg_pct:+.2f}%" if chg_pct >= 0 else f"{chg_pct:.2f}%",
                        "raw_change_pct": chg_pct
                    }
                else:
                    etfs[name] = {"symbol": symbol, "error": "No price data"}
        except Exception as e:
            etfs[name] = {"symbol": symbol, "error": str(e)}
    return etfs

# ────────────────────────────────
# 장중 15% 이상 급등한 종목 수집 (FDR + yfinance)
# ────────────────────────────────
def get_intraday_surging_stocks():
    print("📈 장중 15% 이상 급등 종목 수집 중 (yfinance)...")
    try:
        df_krx = fdr.StockListing('KRX')
        df_krx = df_krx[df_krx['MarketId'].isin(['STK', 'KSQ'])]
        df_krx = df_krx.dropna(subset=['Marcap'])
        # 상위 500개 종목으로 제한 (시총 기준)
        df_krx = df_krx.sort_values(by='Marcap', ascending=False).head(500)
        
        tickers = []
        ticker_to_name = {}
        for idx, row in df_krx.iterrows():
            code = row['Code']
            name = row['Name']
            suffix = ".KS" if row['MarketId'] == 'STK' else ".KQ"
            yf_ticker = f"{code}{suffix}"
            tickers.append(yf_ticker)
            ticker_to_name[yf_ticker] = name
            
        # 5일 데이터 조회 (안전하게 5일치를 가져와 당일과 전일 비교)
        df = yf.download(" ".join(tickers), period="5d", group_by="ticker", progress=False)
        
        dates = df.index.tolist()
        if len(dates) < 2:
            return []
            
        today_idx = -1
        prev_idx = -2
        
        results = []
        available_tickers = df.columns.levels[0] if isinstance(df.columns, pd.MultiIndex) else [df.name]
        
        for ticker in available_tickers:
            try:
                ticker_data = df[ticker] if isinstance(df.columns, pd.MultiIndex) else df
                close_today = ticker_data['Close'].iloc[today_idx]
                prev_close = ticker_data['Close'].iloc[prev_idx]
                high_today = ticker_data['High'].iloc[today_idx]
                volume_today = ticker_data['Volume'].iloc[today_idx]
                prev_volume = ticker_data['Volume'].iloc[prev_idx]
                
                if pd.isna(close_today) or pd.isna(prev_close) or pd.isna(high_today) or prev_close == 0:
                    continue
                    
                high_rate = (high_today - prev_close) / prev_close * 100
                close_rate = (close_today - prev_close) / prev_close * 100
                volume_ratio = volume_today / prev_volume if prev_volume > 0 else 0
                
                if high_rate >= 15.0:
                    name = ticker_to_name.get(ticker, ticker)
                    pull_back = high_rate - close_rate
                    results.append({
                        "ticker": ticker.split(".")[0],
                        "name": name,
                        "high_rate": round(high_rate, 2),
                        "close_rate": round(close_rate, 2),
                        "pull_back_rate": round(pull_back, 2),
                        "volume_today": int(volume_today),
                        "volume_ratio": round(volume_ratio, 2)
                    })
            except Exception:
                pass
                
        # 고가 등락률 기준 내림차순 정렬 후 상위 30개만 반환
        results = sorted(results, key=lambda x: x['high_rate'], reverse=True)[:30]
        return results
    except Exception as e:
        print(f"⚠️ 급등 종목 수집 오류: {e}")
        return []

# ────────────────────────────────
# 글로벌 매크로 데이터 수집 (yfinance)
# 나스닥·S&P500·다우·DXY 달러인덱스·미 10년 국채금리·WTI 유가·금
# ────────────────────────────────
def get_global_macro():
    """
    글로벌 매크로 핵심 지표 수집:
    - 미국 주요 지수: 나스닥(^IXIC), S&P500(^GSPC), 다우(^DJI), SOXX(반도체ETF)
    - 달러: DXY 달러인덱스(DX-Y.NYB), 원달러 환율(KRW=X)
    - 금리: 미국 10년 국채(^TNX), 2년 국채(^IRX)
    - 원자재: WTI 원유(CL=F), 금(GC=F)
    """
    result = {}
    tickers = {
        "nasdaq": "^IXIC",
        "sp500": "^GSPC",
        "dow": "^DJI",
        "soxx": "SOXX",          # 필라델피아 반도체 ETF
        "dxy": "DX-Y.NYB",       # 달러 인덱스
        "usd_krw": "KRW=X",      # 원달러 환율
        "us10y": "^TNX",          # 미 10년 국채금리
        "us2y": "^IRX",           # 미 2년 국채금리
        "wti": "CL=F",            # WTI 원유
        "gold": "GC=F",           # 금
        "vix": "^VIX",            # 공포지수
    }
    try:
        for key, sym in tickers.items():
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="2d")
                if hist.empty:
                    result[key] = {"error": "no data"}
                    continue
                close = round(float(hist["Close"].iloc[-1]), 4)
                prev  = round(float(hist["Close"].iloc[-2]), 4) if len(hist) >= 2 else close
                chg_pct = round((close - prev) / prev * 100, 2) if prev != 0 else 0
                result[key] = {
                    "close": close,
                    "prev_close": prev,
                    "change_pct": chg_pct
                }
            except Exception as e:
                result[key] = {"error": str(e)}
    except Exception as e:
        result["error"] = str(e)
    return result

# ────────────────────────────────
# 전체 수집
# ────────────────────────────────
def collect_all():
    print("📊 시장 데이터 수집 시작...")
    today, week_ago, last_trading = get_dates()

    print("  [글로벌] 해외 매크로 지표 수집 중...")
    global_macro = get_global_macro()
    
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "last_trading_day": last_trading,
        "is_weekend": datetime.datetime.now().weekday() >= 5,
        "index": get_index_pykrx(),
        "investor": get_investor_naver(),
        "upper_limit": get_upper_limit_naver(),
        "watchlist": get_watchlist_naver(),
        "us_etfs": get_us_etfs(),
        "surging_stocks": get_intraday_surging_stocks(),
        "global_macro": global_macro,   # ← 신규: 글로벌 매크로 데이터
    }
    print("✅ 시장 데이터 수집 완료")
    return data

if __name__ == "__main__":
    data = collect_all()
    print(json.dumps(data, ensure_ascii=False, indent=2))
