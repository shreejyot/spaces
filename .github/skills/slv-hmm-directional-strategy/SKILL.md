---
name: slv-hmm-directional-strategy
description: "Build and evaluate a two-model Hidden Markov Model strategy for SLV or another stock/ETF using daily OHLC data, rolling return and realized-volatility thresholds, UP/FLAT/DOWN states, and next-day predictions. Use for HMM stock direction, SLV, state transition probabilities, and tuning k without look-ahead bias."
argument-hint: "Specify the ticker, data window, and what the two HMMs should represent; defaults are SLV and three months."
---

# HMM Direction Strategy

Create Python code that fetches daily OHLC prices, derives directional states, fits and compares two Hidden Markov Models, and reports next-day state probabilities and transition probabilities. Default to SLV and approximately three months of market data when the user does not specify otherwise.

## Procedure

1. **Resolve model and timing definitions.** Confirm what the two models are intended to compare if the user has not specified. Offer this concrete default: Model A is a discrete HMM over threshold-derived UP/FLAT/DOWN observations; Model B is a Gaussian HMM over daily OHLC-derived return/range features, with its latent states mapped to UP/FLAT/DOWN by their mean directional return. Do not present two differently named copies of the same model as independent models. Establish whether the requested “current state” is yesterday's completed candle and whether the forecast target is the next session.

2. **Check the threshold's units before coding.** The requested expression compares `Close - Open` (currency per share) with `k * average_daily_return / annualized_volatility` (dimensionless). Flag this mismatch and use the candle return `(Close - Open) / Open` for state assignment unless the user explicitly requests another compatible price-unit threshold. Use close-to-close returns for realized volatility and rolling average daily return unless the user chooses another definition. Define the threshold as `k * rolling_mean_daily_return / rolling_annualized_volatility`; apply the specified greater-than / less-than / otherwise rules and explain that the threshold can be signed or close to zero.

3. **Fetch and prepare data.** Use `yfinance` for the ticker with daily interval and a three-month period. Keep Open, High, Low, and Close, use a consistent adjusted-price convention, sort by session, remove missing/duplicate rows, and exclude an incomplete current session. State the data source and date range. If fetching or the symbol fails, report the issue rather than silently substituting data.

4. **Build leakage-free rolling inputs.** Treat one month as 21 trading sessions unless the user specifies calendar-month logic. Compute daily returns, rolling 21-session mean daily return, and rolling 21-session realized volatility annualized by `sqrt(252)`. Shift rolling statistics by one session before applying them to that session's candle, so the candle being classified and any future bars do not influence its own threshold. Require enough history for each window; do not fill unavailable initial values with future-informed values.

5. **Tune `k` and compare models chronologically.** Search a documented, configurable grid of `k` values. Use expanding or rolling walk-forward validation to predict the next session; fit preprocessing and model parameters only on each training fold. Never shuffle time-series rows, use future-smoothed HMM states for a live prediction, or tune on the final reported test period. Score next-day states using balanced accuracy (and provide the confusion matrix); compare against a simple persistence baseline. Report the selected `k`, validation dates, sample counts, and limitations. With only three months of OHLC, warn that the effective sample is small and estimates can be unstable; do not claim a robust optimum.

6. **Fit and report the two HMMs.** Use a maintained HMM package such as `hmmlearn`, with reproducible random seeds and documented feature scaling. For Model A, encode the three observed categories and fit a categorical-emission HMM when supported by the installed package; otherwise explain the compatible implementation choice. For Model B, derive causal features from OHLC (for example close-to-close return, open-to-close return, and intraday range), standardize using training data only, and fit a Gaussian-emission HMM. Use three latent states unless data limitations or convergence make that unsuitable. Map latent states consistently to UP/FLAT/DOWN using training-fold directional-return means; state labels are not inherently ordered by an HMM.

7. **Calculate probabilities and deliver usable code.** Report each model's next-session UP/FLAT/DOWN probability distribution, the selected model's prediction, and a 3-by-3 row-normalized transition matrix in UP, FLAT, DOWN order. Self-transitions must remain allowed; do not zero the diagonal. Derive the matrix from training/observed transitions or the fitted HMM transition matrix as appropriate, and label which one is shown. For today's signal, use only the latest completed candle and filtered (past-only) probabilities. Include install/run instructions and concise comments where needed.

## Completion Checks

- OHLC data is daily, ordered, and limited to the requested lookback.
- Rolling calculations use 21 prior observations and no same-day/future leakage.
- State comparisons use compatible units and preserve the requested UP/FLAT/DOWN rule.
- `k` selection is walk-forward; final evaluation is kept separate from tuning.
- Both models are meaningfully distinct, their state mapping is documented, and both return next-day probabilities.
- Transition probabilities are finite, row-normalized, ordered consistently, and include self-transitions.
- Report convergence/data-quality issues, validation metrics, baselines, and the short-history caveat.