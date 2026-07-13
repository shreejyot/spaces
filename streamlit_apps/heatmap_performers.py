import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

st.set_page_config(layout="wide")

# Dataset files mapping (kept consistent with stock_data_explorer)
DATASET_FILES = {
    'US Watchlist': './data/us_watchlist.csv',
    'Nifty 100 tickers': './data/nifty_100_tickers.csv',
    'India indices': './data/indian_indices_list.csv',
    'US indices': './data/us_indices_data.csv',
}

def load_ticker_df(ticker_file=DATASET_FILES['Nifty 100 tickers']):
    df = pd.read_csv(ticker_file)
    # Ensure expected columns exist
    # Expect at least: Ticker, Name, optional Category
    if 'Ticker' not in df.columns:
        raise ValueError('Ticker column not found in dataset')
    return df

def batch_get_close_series(tickers, start, end, interval):
    # Use yf.download in batch; handle single vs multiple tickers
    if not tickers:
        return {}
    raw = yf.download(tickers, start=start, end=end, interval=interval, progress=False)
    series_map = {}
    # If only one ticker, raw['Close'] is a Series or DataFrame with single column
    try:
        cols = raw.columns
    except Exception:
        return {}

    if isinstance(cols, pd.MultiIndex):
        # MultiIndex: top level ticker, then field
        for tk in tickers:
            try:
                s = raw[tk]['Close'].dropna()
                if not s.empty:
                    series_map[tk] = s.sort_index()
            except Exception:
                continue
    else:
        # Single ticker or simple columns
        if 'Close' in raw.columns:
            s = raw['Close'].dropna()
            if isinstance(s, pd.Series):
                series_map[tickers[0]] = s.sort_index()
            else:
                # DataFrame with multiple columns (unlikely here), try per-column
                for col in s.columns:
                    series_map[col] = s[col].dropna().sort_index()

    return series_map

def build_matrix_for_heatmap(series_map, tickers, rescale=True, rescale_date=None):
    # Build common date index as union of all dates
    index = pd.Index(sorted({d for s in series_map.values() for d in s.index}))
    if index.empty:
        return None, None
    matrix = []
    labels = []
    for tk in tickers:
        s = series_map.get(tk)
        if s is None or s.empty:
            continue
        # reindex to common index
        s2 = s.reindex(index)
        # choose rescale base
        if rescale:
            base_val = None
            if rescale_date is not None:
                # pick first non-nan on or after rescale_date
                try:
                    idx = pd.to_datetime(rescale_date)
                    mask = s2.index >= idx
                    vals = s2[mask].dropna()
                    if not vals.empty:
                        base_val = vals.iloc[0]
                except Exception:
                    base_val = None
            if base_val is None:
                base_val = s2.dropna().iloc[0] if not s2.dropna().empty else np.nan
            row = (s2 / base_val * 100).values
        else:
            row = s2.values
        matrix.append(row)
        labels.append(tk)

    if not matrix:
        return None, None
    arr = np.vstack(matrix)
    return arr, (labels, index)

def plot_heatmap(arr, labels, dates, title):
    fig, ax = plt.subplots(figsize=(12, max(3, 0.4 * len(labels))))
    # imshow with NaN masked
    cmap = plt.get_cmap('RdYlGn')
    im = ax.imshow(arr, aspect='auto', cmap=cmap, interpolation='nearest')
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    # show only a subset of date labels
    ncols = arr.shape[1]
    if ncols > 0:
        step = max(1, ncols // 12)
        xticks = np.arange(0, ncols, step)
        ax.set_xticks(xticks)
        ax.set_xticklabels([pd.to_datetime(dates[i]).strftime('%Y-%m-%d') for i in xticks], rotation=45, ha='right')
    ax.set_title(title)
    cbar = fig.colorbar(im, ax=ax)
    return fig

def main():
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

    with st.sidebar:
        st.header('Heatmap - Top/Bottom Performers')
        ticker_file = st.selectbox('Select Dataset', list(DATASET_FILES.keys()), key='hm_ticker_file')
        df = load_ticker_df(DATASET_FILES[ticker_file])

        st.markdown('')
        st.markdown('---')
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input('Start', value=date.today() - timedelta(days=365), key='hm_start_date')
        with col2:
            end_date = st.date_input('End', value=date.today(), key='hm_end_date')

        # Category filter (if available)
        categories = []
        if 'Category' in df.columns:
            categories = sorted(df['Category'].dropna().unique().tolist())
            sel_cats = st.multiselect('Filter Category', ['All'] + categories, default=['All'], key='hm_cats')
        else:
            sel_cats = ['All']

        interval = st.selectbox('Data Interval', ['1d', '5d', '1wk', '1mo'], index=0, key='hm_interval')
        st.text('For universe returns, daily intervals are recommended')
        st.markdown('---')
        st.checkbox('Rescale to 100', value=True, key='hm_rescale')
        rescale_date = st.date_input('Rescale Date', value=start_date, key='hm_rescale_date')
        st.markdown('')
        st.text('Top/Bottom count fixed to 10. Adjustable on request.')
        st.markdown('')
        fetch = st.button('Compute Heatmaps', key='hm_fetch')

    st.title('Top/Bottom Performers Heatmaps')
    if fetch:
        # filter universe
        if 'Category' in df.columns and sel_cats and 'All' not in sel_cats:
            df_filt = df[df['Category'].isin(sel_cats)].copy()
        else:
            df_filt = df.copy()

        tickers = df_filt['Ticker'].astype(str).tolist()
        names = dict(zip(df_filt['Ticker'].astype(str), df_filt.get('Name', df_filt['Ticker']).astype(str)))

        if not tickers:
            st.warning('No tickers in the selected universe.')
            return

        with st.spinner('Fetching data for universe (this may take a while)...'):
            series_map = batch_get_close_series(tickers, start_date, end_date + timedelta(days=1), interval)

        # compute total returns
        results = []
        for tk in tickers:
            s = series_map.get(tk)
            if s is None or s.dropna().empty:
                continue
            first = s.dropna().iloc[0]
            last = s.dropna().iloc[-1]
            pct = float((last / first - 1) * 100)
            results.append({'Ticker': tk, 'Name': names.get(tk, tk), 'Return': pct, 'DataPoints': len(s.dropna())})

        if not results:
            st.warning('No valid price data found for the selected tickers/dates.')
            return

        res_df = pd.DataFrame(results).sort_values('Return', ascending=False).reset_index(drop=True)
        top_n = res_df.head(10)
        bottom_n = res_df.tail(10).sort_values('Return')

        st.subheader('Summary')
        colA, colB = st.columns(2)
        with colA:
            st.write('Top 10 by Return')
            st.dataframe(top_n)
        with colB:
            st.write('Bottom 10 by Return')
            st.dataframe(bottom_n)

        # Prepare heatmaps
        top_tickers = top_n['Ticker'].tolist()
        bottom_tickers = bottom_n['Ticker'].tolist()

        arr_top, meta_top = build_matrix_for_heatmap(series_map, top_tickers, rescale=st.session_state.get('hm_rescale', True), rescale_date=rescale_date)
        arr_bot, meta_bot = build_matrix_for_heatmap(series_map, bottom_tickers, rescale=st.session_state.get('hm_rescale', True), rescale_date=rescale_date)

        if arr_top is not None:
            labels, dates = meta_top
            fig_top = plot_heatmap(arr_top, labels, dates, 'Top 10 Performers (Rescaled to 100)')
            st.pyplot(fig_top)
        else:
            st.info('Not enough data to plot Top 10 heatmap.')

        if arr_bot is not None:
            labels, dates = meta_bot
            fig_bot = plot_heatmap(arr_bot, labels, dates, 'Bottom 10 Performers (Rescaled to 100)')
            st.pyplot(fig_bot)
        else:
            st.info('Not enough data to plot Bottom 10 heatmap.')

if __name__ == '__main__':
    main()
