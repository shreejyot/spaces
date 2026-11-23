import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, timedelta

from sector_config import load_sectors_dataframe

st.set_page_config(page_title="US Sector Trend Monitor", layout="wide")
SECTOR_DATA = load_sectors_dataframe()
SECTORS = dict(zip(SECTOR_DATA["Ticker"], SECTOR_DATA["Description"]))
ASSET_CLASS_BY_TICKER = dict(zip(SECTOR_DATA["Ticker"], SECTOR_DATA["AssetClass"]))
TICKERS = list(SECTORS) + ["SPY"]
DATA_SOURCE = "yfinance"

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
:root{--bg:#071321;--panel:#102238;--line:#233c55;--muted:#9aafc8;--text:#edf3ff;--teal:#4bd8c5;--red:#ff5967}
html,body,[class*="css"]{font-family:Inter,sans-serif}.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1600px;padding-top:1rem}section[data-testid="stSidebar"]{background:#0a1929}
.brand{display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:12px}
.brand-left{font-size:28px;font-weight:900}.mark{color:var(--teal);font-size:34px;padding-right:10px}
.eyebrow,.subline{color:var(--muted)}h1{color:var(--text)!important;font-size:clamp(30px,4vw,56px)!important;font-weight:900!important}
.subline{font-size:17px;margin:5px 0 18px}.metric{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:14px 18px;height:108px}
.ml{color:#a6b8cf;font-weight:700;font-size:14px}.mv{color:var(--teal);font-size:43px;font-weight:800;white-space:nowrap}.ms{color:var(--muted);font-size:14px}
table.trend{width:100%;border-collapse:collapse;table-layout:fixed;font-size:16px}
table.trend th{background:#0c1d30;color:#a6b8cf;font-size:13px;padding:14px 8px;text-align:left;border-bottom:1px solid var(--line)}
table.trend td{padding:8px;color:var(--text)}table.trend tr:nth-child(odd){background:#102238}table.trend tr:nth-child(even){background:#0d1d30}
table.trend .num{text-align:right;font-weight:800;white-space:nowrap;font-size:18px}.rank{color:var(--muted)}.ticker{font-size:20px;font-weight:900}
.pos{color:var(--teal)!important}.neg{color:var(--red)!important}.neutral{color:#a6b8cf!important}
.track{height:18px;border-left:1px dashed #8398ae;position:relative}.bar{height:16px;position:absolute;top:1px;background:var(--teal)}
.bench{border-top:1px solid #91a7bf}.foot{color:var(--muted);font-size:12px;line-height:1.4;margin-top:8px}
@media(max-width:850px){table.trend{font-size:11px}table.trend td{padding:5px 3px}table.trend th{font-size:9px;padding:7px 3px}table.trend .num{font-size:11px}.mv{font-size:28px}}
</style>
''', unsafe_allow_html=True)

def fetch_yfinance_prices(tickers, start, end):
    raw = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    if raw.empty:
        raise RuntimeError("No data returned by Yahoo Finance.")
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"] if "Close" in raw.columns.get_level_values(0) else raw.xs("Close", axis=1, level=1)
    else:
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})
    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    return prices.sort_index()

def fetch_price_data(source, tickers, start, end):
    providers = {
        "yfinance": fetch_yfinance_prices,
    }
    if source not in providers:
        raise ValueError(f"Unsupported market data source: {source}")
    return providers[source](tickers, start, end)

def download(end_date, tickers):
    start = pd.Timestamp(end_date) - pd.DateOffset(months=24) - pd.Timedelta(days=15)
    end = pd.Timestamp(end_date) + pd.Timedelta(days=1)
    return fetch_price_data(
        DATA_SOURCE,
        tickers,
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
    )

def at(series, dt):
    x = series.dropna()
    x = x.loc[x.index <= pd.Timestamp(dt)]
    return float(x.iloc[-1]) if len(x) else np.nan

def period_offset(period):
    if period == "2w":
        return pd.Timedelta(weeks=2)
    return pd.DateOffset(months=int(period[:-1]))

def trend_strength(series, asof, periods):
    last = at(series, asof)
    returns = []
    for period in periods:
        old = at(series, asof - period_offset(period))
        returns.append((last / old - 1) * 100 if pd.notna(old) and old else np.nan)
    return np.nanmean(returns)

def period_return(series, asof, period):
    last = at(series, asof)
    old = at(series, asof - period_offset(period))
    return (last / old - 1) * 100 if pd.notna(old) and old else np.nan

def period_label(period):
    if period == "2w":
        return "2 WEEK"
    months = int(period[:-1])
    return "1 YEAR" if months == 12 else f"{months} MONTH"

def calculate(prices, chosen, strength_periods, use_current_week=True):
    p = prices.loc[prices.index <= pd.Timestamp(chosen)].dropna(how="all")
    if p.empty: raise RuntimeError("No trading session on or before the selected date.")
    asof = p.index[-1]
    prior_dates = p.index[p.index < asof]
    if use_current_week:
        calculation_asof = asof
    elif len(prior_dates) >= 5:
        calculation_asof = prior_dates[-5]
    else:
        raise RuntimeError("Not enough trading sessions to exclude the current week.")
    out=[]
    for t,name in SECTORS.items():
        s=prices[t].dropna(); last=at(s,asof)
        hist=s.loc[s.index<asof]; base=float(hist.iloc[-5]) if len(hist)>=5 else np.nan
        ybase=at(s,pd.Timestamp(asof.year,1,1))
        selected_returns = {
            f"period_{index}": period_return(s, calculation_asof, period)
            for index, period in enumerate(strength_periods, start=1)
        }
        out.append({"ticker":t,"sector":name,"asset_class":ASSET_CLASS_BY_TICKER[t],"trend":trend_strength(s,calculation_asof,strength_periods),"week":(last/base-1)*100 if pd.notna(base) and base else np.nan,**selected_returns,"ytd":(last/ybase-1)*100 if pd.notna(ybase) and ybase else np.nan})
    df=pd.DataFrame(out)
    df["rank"]=df.groupby("asset_class",sort=False)["trend"].rank(method="first",ascending=False,na_option="bottom").astype(int)
    df=df.sort_values(["asset_class","rank"]).reset_index(drop=True)
    rank_prior_dates=prices.index[prices.index<calculation_asof]
    if len(rank_prior_dates)>=5:
        prior=rank_prior_dates[-5]; ranks=[]
        for asset_class, class_rows in df.groupby("asset_class",sort=False):
            class_ranks=[]
            for t in class_rows.ticker:
                s=prices[t].dropna()
                class_ranks.append((t,asset_class,trend_strength(s,prior,strength_periods)))
            class_rank_df=pd.DataFrame(class_ranks,columns=["ticker","asset_class","prior_trend"])
            class_rank_df["prank"]=class_rank_df["prior_trend"].rank(method="first",ascending=False,na_option="bottom").astype(int)
            ranks.append(class_rank_df[["ticker","asset_class","prank"]])
        q=pd.concat(ranks,ignore_index=True)
        df=df.merge(q,on=["ticker","asset_class"],validate="one_to_one"); df["delta"]=df.prank-df["rank"]
    else: df["delta"]=np.nan
    s=prices["SPY"].dropna(); last=at(s,asof)
    hist=s.loc[s.index<asof]; wb=float(hist.iloc[-5]) if len(hist)>=5 else np.nan; yb=at(s,pd.Timestamp(asof.year,1,1))
    benchmark_returns = {
        f"period_{index}": period_return(s, calculation_asof, period)
        for index, period in enumerate(strength_periods, start=1)
    }
    b={"trend":trend_strength(s,calculation_asof,strength_periods),"week":(last/wb-1)*100 if pd.notna(wb) and wb else np.nan,**benchmark_returns,"ytd":(last/yb-1)*100 if pd.notna(yb) and yb else np.nan}
    return df,b,asof

def f(x): return "—" if pd.isna(x) else f"{x:+.1f}%"
def cc(x): return "pos" if pd.notna(x) and x>=0 else "neg"

def render_asset_class_tab(asset_class, df, benchmark, strength_periods, asof, short_term, medium_term, long_term):
    class_df=df.loc[df.asset_class==asset_class].reset_index(drop=True)
    if class_df.empty:
        st.info("No tickers are configured for this asset class.")
        return

    best=class_df.iloc[0]
    positive=int((class_df.trend>0).sum())
    a,bcol,ccol=st.columns([1,1,1.08],gap="medium")
    with a:
        st.markdown(f'<div class="metric"><div class="ml">TICKERS IN POSITIVE TREND</div><div class="mv">{positive} / {len(class_df)}</div></div>',unsafe_allow_html=True)
    with bcol:
        st.markdown(f'<div class="metric"><div class="ml">STRONGEST TREND</div><div class="mv" style="font-size:38px;color:#edf3ff">{best.ticker} <span style="color:#4bd8c5">{f(best.trend)}</span></div><div class="ms">{best.sector}</div></div>',unsafe_allow_html=True)
    with ccol:
        if asset_class=="Equity":
            st.markdown(f'<div class="metric"><div class="ml">S&amp;P 500 TREND</div><div class="mv">{f(benchmark["trend"])}</div><div class="ms">SPY benchmark</div></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric"><div class="ml">TICKERS IN ASSET CLASS</div><div class="mv">{len(class_df)}</div><div class="ms">{asset_class}</div></div>',unsafe_allow_html=True)

    max_trend=class_df.trend.abs().max()
    scale=max(float(max_trend) if pd.notna(max_trend) else 0,1)
    rows=[]
    for _,r in class_df.iterrows():
        if pd.isna(r.trend):
            bar=""
        else:
            w=abs(r.trend)/scale*100
            bar=f'<div class="bar" style="left:0;width:{w:.2f}%"></div>' if r.trend>=0 else f'<div class="bar" style="right:0;width:{w:.2f}%;background:#ff5967"></div>'
        d="—" if pd.isna(r.delta) or r.delta==0 else (f"↑{int(r.delta)}" if r.delta>0 else f"↓{abs(int(r.delta))}")
        dc="pos" if pd.notna(r.delta) and r.delta>0 else ("neg" if pd.notna(r.delta) and r.delta<0 else "neutral")
        period_cells="".join(
            f'<td class="num {cc(r[f"period_{index}"])}">{f(r[f"period_{index}"])}</td>'
            for index in range(1,4)
        )
        rows.append(f'<tr><td class="rank">{int(r["rank"]):02d}</td><td class="ticker">{r.ticker}</td><td>{r.sector}</td><td class="num {cc(r.week)}">{f(r.week)}</td><td class="num {cc(r.ytd)}">{f(r.ytd)}</td>{period_cells}<td><div class="track">{bar}</div></td><td class="num {cc(r.trend)}">{f(r.trend)}</td><td class="num {dc}">{d}</td></tr>')

    if asset_class=="Equity":
        bw=abs(benchmark["trend"])/scale*100
        benchmark_period_cells="".join(
            f'<td class="num {cc(benchmark[f"period_{index}"])}">{f(benchmark[f"period_{index}"])}</td>'
            for index in range(1,4)
        )
        rows.append(f'<tr class="bench"><td class="rank">—</td><td class="ticker">SPY</td><td>S&amp;P 500 (benchmark)</td><td class="num {cc(benchmark["week"])}">{f(benchmark["week"])}</td><td class="num {cc(benchmark["ytd"])}">{f(benchmark["ytd"])}</td>{benchmark_period_cells}<td><div class="track"><div class="bar" style="left:0;width:{bw:.2f}%;background:#9bb8e3"></div></div></td><td class="num neutral">{f(benchmark["trend"])}</td><td class="num neutral">—</td></tr>')

    period_headers="".join(
        f'<th style="text-align:right">{term} {period_label(period)}</th>'
        for term,period in zip(("[SHORT-TERM]","[MEDIUM-TERM]","[LONG-TERM]"),strength_periods)
    )
    html=f'<table class="trend"><colgroup><col style="width:3%"><col style="width:5%"><col style="width:17%"><col style="width:8.5%"><col style="width:8.5%"><col style="width:8.5%"><col style="width:8.5%"><col style="width:8.5%"><col style="width:15%"><col style="width:7.5%"><col style="width:10%"></colgroup><thead><tr><th>#</th><th colspan="2">SECTOR ETF</th><th style="text-align:right">1 WEEK</th><th style="text-align:right">YTD</th>{period_headers}<th colspan="2">TREND STRENGTH = Avg[Short, Mid & Long]</th><th style="text-align:right">RANK Δ<br>vs. prior week</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
    st.markdown('<div style="border:1px solid #233c55;border-radius:8px;overflow:hidden;margin-top:16px">'+html+'</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="foot">Trend Strength = average of trailing {short_term}, {medium_term}, and {long_term} adjusted-price total returns.<br>Tickers ranked within {asset_class} by Trend Strength. Rank Δ = change from five trading sessions earlier.<br>For informational purposes only. Historical rankings are not investment advice. Past performance is not indicative of future results.<br>Source: Yahoo Finance, accessed via yfinance.</div>',unsafe_allow_html=True)
    with st.expander("View underlying data"):
        display_data=class_df[["rank","ticker","sector","week","ytd","period_1","period_2","period_3","trend","delta"]].rename(
            columns={
                "period_1":f"short_term_{short_term}",
                "period_2":f"medium_term_{medium_term}",
                "period_3":f"long_term_{long_term}",
            }
        )
        st.dataframe(display_data,hide_index=True)

with st.sidebar:
    st.markdown("## Dashboard controls")
    chosen=st.date_input("As of end-date",value=date.today()-timedelta(days=1),min_value=date(2000,1,1),max_value=date.today(),help="Uses the latest available market session on or before this date.")

    refresh=st.button("↻ Refresh data")
    st.caption("Yahoo Finance adjusted prices via yfinance.")
    st.markdown("---")
    use_current_week=st.checkbox(
        "Use current week return",
        value=True,
        help="When unchecked, the period returns and Trend Strength end at the previous weekly close. 1 Week and YTD still use the selected date.",
    )
    short_term=st.selectbox("Short-term",["2w","1m","2m","3m","6m"],index=1)
    medium_term=st.selectbox("Medium-term",["1m","3m","6m"],index=1)
    long_term=st.selectbox("Long-term",["3m","6m","9m","12m","18m","24m"],index=1)
    strength_periods=(short_term,medium_term,long_term)
    
    st.caption("1 Week = five trading sessions, YTD = year-to-date return.")
    st.caption("Rank Δ compares ranks five trading sessions earlier.")

@st.cache_data(ttl=3600,show_spinner=False)
def cached(d, tickers): return download(d, list(tickers))

st.markdown('<div class="eyebrow">WEEKLY MARKET INTELLIGENCE</div></div>',unsafe_allow_html=True)
st.markdown("<h1>US SECTOR TREND MONITOR</h1>",unsafe_allow_html=True)
try:
    with st.spinner("Downloading adjusted ETF prices..."):
        if refresh: cached.clear()
        prices=cached(chosen,tuple(TICKERS)); df,b,asof=calculate(prices,chosen,strength_periods,use_current_week)
    st.markdown(f'<div class="subline">WEEK ENDING {asof.strftime("%d %b %Y").upper()}　 /　 ADJUSTED TOTAL RETURNS</div>',unsafe_allow_html=True)
    asset_classes=SECTOR_DATA["AssetClass"].drop_duplicates().tolist()
    tabs=st.tabs(asset_classes)
    for asset_class,tab in zip(asset_classes,tabs):
        with tab:
            render_asset_class_tab(
                asset_class,
                df,
                b,
                strength_periods,
                asof,
                short_term,
                medium_term,
                long_term,
            )
except Exception as e:
    st.error(f"Unable to build dashboard: {e}")
    st.info("Check internet access and click Refresh data. Yahoo Finance may rate-limit requests.")
