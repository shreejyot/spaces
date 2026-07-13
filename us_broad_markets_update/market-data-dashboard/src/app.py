import streamlit as st
import pandas as pd
from datetime import datetime
from utils.fetch_data import fetch_data

# Load indices data
indices_df = pd.read_csv('data/us_indices_data.csv')

# Sidebar inputs for date selection
st.sidebar.header("Select Date Range")
year_end_date = (datetime.today().replace(day=1, month=1) - pd.DateOffset(days=1)).strftime('%Y-%m-%d')
cob_date = datetime.today().strftime('%Y-%m-%d')

start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime(year_end_date))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(cob_date))

# Prepare index ticker map
index_types_list = indices_df['Category'].unique().tolist()
index_ticker_map = {index_type: indices_df[indices_df['Category'] == index_type]['Ticker'].tolist() for index_type in index_types_list}

# Fetch data for selected date range
dashboard_data = {}
for asset_class, tickers in index_ticker_map.items():
    dashboard_data[asset_class] = fetch_data(tickers, start_dt=start_date, end_dt=end_date)

# Display data and charts
for asset_class, df in dashboard_data.items():
    st.subheader(f"Asset Class: {asset_class}")
    for ticker in df.columns:
        series = df[ticker].dropna()
        if series.empty:
            st.write(f"No data available for {ticker}")
            continue

        # Compute percent return
        start_val = series.iloc[0]
        end_val = series.iloc[-1]
        pct_return = (end_val / start_val - 1) * 100

        # Plotting
        st.line_chart(series, use_container_width=True)
        st.write(f"{ticker} —> {pct_return:.2f}%")