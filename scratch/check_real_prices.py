import yfinance as yf
import datetime

def main():
    print("Real Prices from yfinance:")
    for ticker, name in [("005930.KS", "삼성전자"), ("000660.KS", "SK하이닉스")]:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1d")
            if not hist.empty:
                print(f"{name}: Close={hist['Close'].iloc[-1]}, High={hist['High'].iloc[-1]}, PrevClose={t.info.get('previousClose')}")
            else:
                print(f"{name}: Empty history")
        except Exception as e:
            print(f"Error for {name}: {e}")

if __name__ == "__main__":
    main()
