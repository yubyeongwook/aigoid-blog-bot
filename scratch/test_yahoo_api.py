import requests
import json

def get_us_etfs(symbols):
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
            # Clean None values if any
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
                # Fallback to meta
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

if __name__ == "__main__":
    symbols = [
        ("SOXX", "Semiconductor"),
        ("XLK", "Technology"),
        ("XBI", "Biotech"),
        ("XLE", "Energy"),
        ("XLF", "Financial"),
        ("QQQ", "Nasdaq_ETF"),
        ("SPY", "SP500_ETF")
    ]
    print(json.dumps(get_us_etfs(symbols), indent=2))
