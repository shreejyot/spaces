import streamlit as st
import pandas as pd
from datetime import date
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Load ticker data
ticker_df = pd.read_csv('../data/nifty_100_tickers.csv')
ticker_options = ticker_df['yfinance Ticker'].tolist()
ticker_names = ticker_df['Name'].tolist()
ticker_dict = dict(zip(ticker_names, ticker_df['yfinance Ticker']))

# Sidebar inputs
with st.sidebar:
    st.header('Select Parameters')
    start_date = st.date_input('Start Date', value=date(2025, 1, 1), key='start_date')
    end_date = st.date_input('End Date', value=date(2026, 1, 1), key='end_date')
    ticker_name = st.selectbox('Select Ticker', ticker_names, key='ticker_name')
    fetch_data = st.button('Fetch & Plot Data', key='fetch_button')

ticker = ticker_dict[ticker_name]

# Main area
st.title('Nifty 100 Stock Data Explorer')
st.write(f'Selected Ticker: {ticker} ({ticker_name})')
st.write(f'Date Range: {start_date} to {end_date}')

if fetch_data:
    with st.spinner('Fetching data...'):
        data = yf.download(ticker, start=start_date, end=end_date)
        data['Close'] = data['Close'].astype(float)
        data = data[data['Close']>0]
    if not data.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        data['Close'].plot(ax=ax)
        ax.set_title(f'{ticker_name} ({ticker}) Closing Price')
        ax.set_xlabel('Date')
        ax.set_ylabel('Close Price (INR)')
        
        # Use 75% width for the plot
        col1, col2 = st.columns([3, 1])
        with col1:
            st.pyplot(fig)
    else:
        st.warning('No data found for the selected range and ticker.')
