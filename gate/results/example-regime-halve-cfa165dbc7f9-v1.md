# Gate v1 result: example-regime-halve (cfa165dbc7f9)
Run 2026-11-21T14:59:14Z. Champion: baseline-55-20 (4035b257aa95). Verdict: **REJECTED**.

Hypothesis: Halving the exposure of plain 55/20 in a stress regime (30-day vol above its trailing 80th percentile, or price 30% below its high) lowers max drawdown more than the same scaling at random times.
Null: A circularly shifted copy of the label does just as well.
Primary metric (declared in advance): maxdd

Trials in ledger (all variants ever registered, incl. historical): 123. Information only: zero-skill best-of-123 Sharpe hurdle ~1.21 over 6.6 years.

| Check | Result | Detail |
|---|---|---|
| 1 regression BTC-EUR | FAIL | maxDD 36.7% vs 37.6% | final x4.54 vs x6.67 (need >= 80% of champion) |
| 2 placebo BTC-EUR | FAIL | maxdd: beats 84.5% of 2000 block placebos (need 95%) |
| 3 out-of-sample BTC-EUR | PASS | Sharpe from 2023-01-01: 0.68 vs champion 0.80 (tolerance 0.15) |
| 5 robustness ex-2022 BTC-EUR | FAIL | maxDD 36.7% vs 37.6% | final x5.18 vs x8.14 |
| 5 robustness fees x2 BTC-EUR | FAIL | maxDD 38.6% vs 39.8% | final x4.00 vs x5.89 |
| 6 turnover and kill-switch BTC-EUR | PASS | 11.6 exposure changes/yr (cap 40); -20% stop would fire in 16% of 365-day windows (cap 25%) |
| 1 regression ETH-EUR | FAIL | maxDD 30.9% vs 41.7% | final x7.64 vs x12.98 (need >= 80% of champion) |
| 2 placebo ETH-EUR | PASS | maxdd: beats 98.8% of 2000 block placebos (need 95%) |
| 3 out-of-sample ETH-EUR | PASS | Sharpe from 2023-01-01: 0.57 vs champion 0.71 (tolerance 0.15) |
| 5 robustness ex-2022 ETH-EUR | FAIL | maxDD 30.7% vs 41.7% | final x8.83 vs x16.10 |
| 5 robustness fees x2 ETH-EUR | FAIL | maxDD 32.3% vs 41.7% | final x6.97 vs x11.62 |
| 6 turnover and kill-switch ETH-EUR | PASS | 9.5 exposure changes/yr (cap 40); -20% stop would fire in 2% of 365-day windows (cap 25%) |
| 4 holdout vs constant exposure | FAIL | lower maxDD than the constant-exposure comparator on 3 of 16 coins (need 9) |
| 7 pre-registration | PASS | hypothesis, null and primary_metric present; hash written to ledger before results |

Holdout detail:
- ADA-EUR: new 34.3% vs constant-scale 39.8%
- ATOM-EUR: new 41.5% vs constant-scale 41.5%
- AVAX-EUR: new 30.5% vs constant-scale 30.5%
- BCH-EUR: new 49.3% vs constant-scale 46.5%
- DOGE-EUR: new 58.0% vs constant-scale 52.9%
- DOT-EUR: new 34.4% vs constant-scale 34.4%
- ETC-EUR: new 35.5% vs constant-scale 36.9%
- LINK-EUR: new 74.5% vs constant-scale 62.1%
- LTC-EUR: new 61.5% vs constant-scale 56.3%
- LUNA-EUR: new 49.1% vs constant-scale 49.1%
- NEAR-EUR: new 47.2% vs constant-scale 47.2%
- SOL-EUR: new 49.1% vs constant-scale 45.0%
- TRX-EUR: new 50.0% vs constant-scale 50.9%
- UNI-EUR: new 27.4% vs constant-scale 27.4%
- XLM-EUR: new 73.8% vs constant-scale 61.0%
- XRP-EUR: new 54.2% vs constant-scale 37.0%

Limits: BTC/ETH count as about 1.3 independent observations; only coins alive today; Bitvavo EUR daily closes; no slippage; the champion and the new spec were both chosen with knowledge of this history. A pass is a reason to forward-paper-test, not evidence of an edge.
