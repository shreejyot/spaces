# US Sector Trend Monitor

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
ADMIN_PASSWORD=admin streamlit run app.py
```

The sidebar **As of end-date** selector recalculates the dashboard using the latest market session on or before the chosen date. The dashboard creates one tab per distinct `AssetClass` in `sectors.csv`; each tab displays and ranks only its assigned tickers. The default sector rows use `Equity`, and SPY appears as the benchmark on the Equity tab.

The **Admin** page edits the `Ticker`, `Description`, and `AssetClass` columns in `sectors.csv`. Saving requires the configured admin password; do not store production passwords in source control.

**Methodology**
- Trend Strength: arithmetic average of three trailing adjusted-price returns, using the Short-term, Medium-term, and Long-term periods selected in the sidebar. Defaults are 1m, 3m, and 6m; the available choices are 2w/1m/2m/3m/6m, 1m/3m/6m, and 3m/6m/9m/12m/18m/24m, respectively.
- 1 Week: five trading sessions.
- Short-, medium-, and long-term return columns: each shows the trailing return for the corresponding sidebar selection. Defaults are 1m, 3m, and 6m; the available choices are 2w/1m/2m/3m/6m, 1m/3m/6m, and 3m/6m/9m/12m/18m/24m, respectively.
- Use current week return: when unchecked, the three selected-period returns and Trend Strength use the previous weekly close as their end date; 1 Week and YTD remain based on the selected date.
- YTD: return from the first available trading session of the calendar year.
- Rank Δ: rank change versus five trading sessions earlier.

`yfinance` downloads with `auto_adjust=True`, so Close prices are adjusted for splits and distributions. This is a practical adjusted-return proxy. Yahoo Finance data availability and rate limits are outside the app's control. Data is cached for one hour; use Refresh data to clear the cache.
