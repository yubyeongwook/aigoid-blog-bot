import yfinance as yf
t = yf.Ticker("000660.KS")
hist = t.history(period="1d")
print("SK하이닉스 yfinance raw:")
print(hist)
print("Previous Close info:", t.info.get("previousClose"))
