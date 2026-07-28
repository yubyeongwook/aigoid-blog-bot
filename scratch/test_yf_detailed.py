import yfinance as yf
import sys

sys.stdout.reconfigure(encoding='utf-8')

for ticker in ["005930.KS", "000660.KS"]:
    print(f"\n=================== {ticker} ===================")
    t = yf.Ticker(ticker)
    # Check history
    df = t.history(period="5d")
    print("History (5 days):")
    print(df)
    # Check info
    print("\nInfo keys:")
    info = t.info
    for key in ["previousClose", "currentPrice", "open", "currency", "financialCurrency"]:
        print(f"  {key}: {info.get(key)}")
