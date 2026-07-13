def fetch_data(tickers, start_dt, end_dt):
    import yfinance as yf
    df = yf.download(tickers, start=start_dt, end=end_dt)
    df = df['Close']
    return df