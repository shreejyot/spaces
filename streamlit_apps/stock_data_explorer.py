import streamlit as st
import pandas as pd
from datetime import date
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Dataset files mapping
DATASET_FILES = {
    'US Watchlist': './data/us_watchlist.csv',
    'Nifty 100 tickers': './data/nifty_100_tickers.csv',
    'India indices': './data/indian_indices_list.csv',
    'US indices': './data/us_indices_data.csv',
}

def load_tickers(ticker_file = DATASET_FILES['Nifty 100 tickers']):
    df = pd.read_csv(ticker_file)
    ticker_dict = pd.Series(df.Ticker.values, index=df.Name).to_dict()
    return ticker_dict

def main():
    # Reducing whitespace on the top of the page
    st.markdown("""
                <style>

                .block-container
                {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    margin-top: 1rem;
                }

                </style>
                """, unsafe_allow_html=True)

    # Sidebar inputs
    with st.sidebar:

        st.header('Select Parameters')

        ticker_file = st.selectbox('Select Dataset', list(DATASET_FILES.keys()), key='ticker_file')
        ticker_dict = load_tickers(DATASET_FILES[ticker_file])
        st.text("")
        st.markdown("---")
        st.text("")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input('Start', value=date(2025, 1, 1), key='start_date')
        with col2:
            end_date = st.date_input('End', value=date(2026, 1, 1), key='end_date')
        ticker_names = st.multiselect('Select Tickers (max 4)', list(ticker_dict.keys()), default=[list(ticker_dict.keys())[0]], key='ticker_names')
        interval = st.selectbox('Data Interval', ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo'], index=8, key='interval',)
        st.text("Intraday data limited to last 60 days")
        st.markdown("---")
        st.text("")
        st.checkbox('Rescale to 100',   value = False,key='rescale')
        rescale_date = st.date_input('Rescale Date', value=start_date, key='rescale_date')
        st.text("")
        st.markdown("---")
        st.text("")
        fetch_data = st.button('Fetch & Plot Data', key='fetch_button')

    # Main area
    st.title('Time Series Data Explorer')
    selected_display = ', '.join([f"{ticker_dict[n]} ({n})" for n in st.session_state.get('ticker_names', [])])
    st.write(f'Selected Tickers: {selected_display}')
    st.write(f'Date Range: {start_date} to {end_date}')
    

    if fetch_data:
        # Enforce maximum of 3 tickers on the same chart
        ticker_names = st.session_state.get('ticker_names', [])
        if len(ticker_names) == 0:
            st.warning('Please select at least one ticker to fetch data for.')
        elif len(ticker_names) > 4:
            st.error('Please select at most 4 tickers to plot on the same chart.')
        else:
            with st.spinner('Fetching data...'):
                fig, ax = plt.subplots(figsize=(12, 6))
                any_plotted = False
                for name in ticker_names:
                    symbol = ticker_dict[name]
                    data = yf.download(symbol, start=start_date, end=end_date,interval=interval, progress=False)
                    if data is None or data.empty:
                        st.warning(f'No data found for {symbol} ({name})')
                        continue
                    if 'Close' not in data.columns or data['Close'].dropna().empty:
                        st.warning(f'No close price data for {symbol} ({name})')
                        continue
                    series = data['Close'].astype(float).sort_index()
                    if series.empty:
                        st.warning(f'No valid data for {symbol} ({name})')
                        continue
                    any_plotted = True
                    start_val = series.iloc[0]
                    end_val = series.iloc[-1]
                    pct_return = float((end_val / start_val - 1) * 100)
                    return_str = f"{symbol}: {pct_return:+.2f}% | "

                    # apply rescale to start at 100 if requested
                    rescale_val = 100
                    if st.session_state.get('rescale', True):
                        if rescale_date.strftime("%Y-%m-%d") not in series.index:
                            st.warning(f'Rescale date {rescale_date} not found in data for {symbol} ({name}). Rescaling to starting value as 100 instead.')
                            rescale_val = start_val
                        else:
                            rescale_val = series[series.index == rescale_date.strftime("%Y-%m-%d")].iloc[0]
                            
                    series = series.copy() / rescale_val * 100

                    # compute high/low and their dates
                    high_idx = series.idxmax().iloc[0]
                    high_val = float(series.max().iloc[0])
                    high_str =  f"High {high_val:.2f} on {high_idx:%Y-%m-%d} | "
                    print(high_str)


                    low_idx = series.idxmin().iloc[0]
                    low_val = float(series.min().iloc[0])
                    low_str =  f"Low {low_val:.2f} on {low_idx:%Y-%m-%d}"
                    print(low_str)  

                    # build a detailed legend label including pct return, high and low with dates
                    label = return_str + high_str + low_str
                    
                    ax.plot(series.index, series.values, label=label)

                    # plot high / low markers (no extra legend entries)
                    ax.plot(high_idx, high_val, marker='^', color='green', markersize=8)
                    ax.plot(low_idx, low_val, marker='v', color='red', markersize=8)

                if any_plotted:
                    ax.legend(fontsize='small')
                    ax.grid(alpha=0.3)
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Close Price')
                    st.pyplot(fig)
                else:
                    st.warning('No data found for the selected range and tickers.')

if __name__ == '__main__':
    main()