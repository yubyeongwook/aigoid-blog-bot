import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import datetime

def test_intraday_high():
    print("1. Fetching KRX Stock Listing...")
    df_krx = fdr.StockListing('KRX')
    
    # Filter stocks with MarketId in STK (KOSPI) or KSQ (KOSDAQ)
    df_krx = df_krx[df_krx['MarketId'].isin(['STK', 'KSQ'])]
    
    # Sort by Marcap (Market Cap) to get the top 500 stocks
    # This filters out small-cap illiquid penny stocks.
    df_krx = df_krx.dropna(subset=['Marcap'])
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
        
    print(f"2. Downloading 5-day historical data for {len(tickers)} stocks via yfinance...")
    # download data
    df = yf.download(" ".join(tickers), period="5d", group_by="ticker", progress=False)
    
    print("3. Analyzing intraday high fluctuations...")
    results = []
    
    # Get available dates
    # We want to compare the last day (today) with the second-to-last day (yesterday)
    dates = df.index.tolist()
    if len(dates) < 2:
        print("Not enough date data.")
        return
        
    today_idx = -1
    prev_idx = -2
    
    # Iterate through all tickers in yf download
    available_tickers = df.columns.levels[0] if isinstance(df.columns, pd.MultiIndex) else [df.name]
    
    for ticker in available_tickers:
        try:
            ticker_data = df[ticker] if isinstance(df.columns, pd.MultiIndex) else df
            
            # Extract close and high values
            close_today = ticker_data['Close'].iloc[today_idx]
            prev_close = ticker_data['Close'].iloc[prev_idx]
            high_today = ticker_data['High'].iloc[today_idx]
            volume_today = ticker_data['Volume'].iloc[today_idx]
            prev_volume = ticker_data['Volume'].iloc[prev_idx]
            
            # Check for NaN
            if pd.isna(close_today) or pd.isna(prev_close) or pd.isna(high_today) or prev_close == 0:
                continue
                
            # Intraday High Rate = (high_today - prev_close) / prev_close * 100
            high_rate = (high_today - prev_close) / prev_close * 100
            close_rate = (close_today - prev_close) / prev_close * 100
            
            # Volume ratio (today's volume vs yesterday's volume)
            volume_ratio = volume_today / prev_volume if prev_volume > 0 else 0
            
            # If high_rate is 15% or more
            if high_rate >= 15.0:
                name = ticker_to_name.get(ticker, ticker)
                # Calculate pull back rate: (high_today - close_today) / prev_close * 100
                pull_back = high_rate - close_rate
                
                results.append({
                    "ticker": ticker.split(".")[0],
                    "name": name,
                    "prev_close": int(prev_close),
                    "high_today": int(high_today),
                    "close_today": int(close_today),
                    "high_rate": round(high_rate, 2),
                    "close_rate": round(close_rate, 2),
                    "pull_back_rate": round(pull_back, 2),
                    "volume_today": int(volume_today),
                    "volume_ratio": round(volume_ratio, 2)
                })
        except Exception as e:
            # print(f"Error parsing {ticker}: {e}")
            pass
            
    # Sort results by high_rate descending
    results = sorted(results, key=lambda x: x['high_rate'], reverse=True)
    
    print(f"\nFound {len(results)} stocks that surged >= 15% during the day:")
    for idx, r in enumerate(results, 1):
        print(f"{idx}. {r['name']} ({r['ticker']}) | High: {r['high_rate']}% | Close: {r['close_rate']}% | Pullback: {r['pull_back_rate']}% | Vol Ratio: {r['volume_ratio']}x")

if __name__ == "__main__":
    test_intraday_high()
