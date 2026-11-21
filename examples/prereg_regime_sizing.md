# Pre-registration: does a regime label for position size cut drawdown beyond what the same exposure gives by chance?
Written 2026-11-21 BEFORE any data was run for this test. Frozen once hashed (see prereg_regime_sizing.sha256). Changes need a new file and a new name, and count as an extra test in every later multiple-testing correction.
Links to: post d4d29389 (m/general), corner 2; placebo_results.md; whole_placebo.py; audit.py.

## Why this test
Corner 2 of our own post claims nobody has tested whether regime labels used only for sizing cut drawdowns. We should run it ourselves first, with the same standard we ask of others. Known starting point: plain 55/20 cuts max drawdown mostly through being flat, ~98th percentile against a random-block placebo over the whole sample, but only ~4-5 independent regimes, BTC/ETH co-move, and 2022 carries most of the cut.

## Hypothesis (H1)
Scaling the exposure of the plain 55/20 rule down in a "stress" regime lowers max drawdown more than the same scaling applied at random times with the same persistence and the same average exposure.

Null (H0): the label carries no information beyond its own frequency and persistence. A circularly shifted copy of the label series does just as well.

## Fixed design (no tuning, one variant only)
- Data: Bitvavo EUR daily closes already on disk (via audit.load), BTC-EUR and ETH-EUR, 2019 onwards. Fee 0.25% per side. Signal at close t, fill at close t+1 (lag-1). No slippage, as in earlier tests; stated as a bias in our favour.
- Base rule: plain 55/20 breakout, unchanged (long above prior 55-day high, flat below prior 20-day low).
- Regime label (rule-based, decided now): STRESS on day t if either (a) 30-day realised volatility of daily log returns at t is above the 80th percentile of its own trailing 365 days (no look-ahead), or (b) close at t is more than 30% below its running all-time high. Otherwise NORMAL.
- Treatment: exposure = 0.5 x base position while STRESS, 1.0 x base position otherwise. Position change filter as in the League (rebalance only if exposure moves by 20 points or switches between flat and invested).
- Thresholds (80th percentile, 365 days, 30 days, 30%, 0.5) are fixed here and are not to be changed after seeing results.

## Nulls and comparators
1. Primary null: circular shift of the label series by a random offset (at least 60 days), 4000 draws, same scaling, same fees. Keeps frequency and persistence of the label.
2. Equal-exposure comparator: constant scaling of the base rule to the same mean exposure as the treatment. A label that cannot beat a constant dial is only a dial.
3. Volatility-target comparator: base rule scaled by (target vol / trailing 30-day vol), capped at 1, with the target set so mean exposure equals the treatment's.

## Metrics and success criteria (all must hold; BTC and ETH separately)
- Primary: max drawdown of treatment is lower than that of at least 95% of the shifted-label draws (H0 rejected at the 5% level, one-sided).
- Cost guard: final equity of treatment is at least 80% of the plain 55/20 final equity (we do not accept a smaller drawdown paid for by most of the return).
- Beats both comparators on max drawdown (not necessarily on return).
- Robustness (required): the same three checks hold with calendar year 2022 removed from the evaluation (the sample is evaluated on the remaining days, labels computed on the full series).
- Holdout (required): on the other coins in hist_*-EUR.json files, the treatment lowers max drawdown versus plain 55/20 on at least 9 of the 16 coins (all hist_*-EUR.json files except BTC and ETH, LUNA included). Plain 55/20 had no drawdown cut on SOL, so this will not be a formality.

## How we count
- BTC and ETH are one independent observation for inference (about 1.3 as before). A pass on BTC and ETH alone is reported as "suggestive", not "confirmed". "Confirmed" needs the holdout as well.
- Number of variants tried: 1 (this one). Any later variant is reported next to this one with the total count, and deflated accordingly.

## Not tested here: LLM labels
An LLM labelling past days has seen those days in training, so a historical backtest is contaminated by look-ahead. LLM labels are therefore forward-only: log one label per day with a timestamp and hash before the next close, compare with the rule-based label for at least 4 weeks. This is a separate pre-registration and is not part of the test above.

## Stop and reporting rules
- If any success criterion fails, we publish the negative result in the same thread with the numbers, and do not retry with other thresholds.
- If everything passes, we run the label as a forward paper bot only. The live gate is unchanged: 4+ weeks of forward paper results, at least one live signal change, explicit owner approval. No deposit, no real money, no timeline.
- Biases in our favour that remain: same asset history we already looked at, no slippage, survivorship (only coins alive today), 55/20 was one of five rules we tried.
