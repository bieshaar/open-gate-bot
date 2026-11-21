# Gate v2 result: momentum-45 (64be1e6524c7)
Run 2026-11-21T15:08:39Z. Champion: baseline-55-20 (4035b257aa95). Verdict: **REJECTED**.

Hypothesis: Long while the close is above the close 45 days earlier (the rule our dry-run bot used) lowers max drawdown versus 55/20 on BTC and ETH.
Null: Random placement of the same in-market runs gives the same drawdown.
Primary metric (declared in advance): maxdd

Trials in ledger (all variants ever registered, incl. historical): 124. Information only: zero-skill best-of-124 Sharpe hurdle ~1.21 over 6.6 years.

| Check | Result | Detail |
|---|---|---|
| 1 regression BTC-EUR | FAIL | maxDD 55.0% vs 37.6% | final x8.84 vs x6.67 (need >= 80% of champion) |
| 2 placebo BTC-EUR | FAIL | maxdd: beats 83.9% of 2000 block placebos (need 95%) |
| 3 out-of-sample BTC-EUR | PASS | Sharpe from 2023-01-01: 0.99 vs champion 0.80 (tolerance 0.15) |
| 3b bootstrap Sharpe difference BTC-EUR | FAIL | 5th percentile of Sharpe(new)-Sharpe(champion) over 2000 paired 20-day block resamples: -0.35 (floor -0.25) |
| 5 robustness ex-2022 BTC-EUR | FAIL | maxDD 41.5% vs 37.6% | final x15.78 vs x8.14 |
| 5 robustness fees x2 BTC-EUR | FAIL | maxDD 57.4% vs 39.8% | final x6.16 vs x5.89 |
| 6 turnover and kill-switch BTC-EUR | FAIL | 21.8 exposure changes/yr (cap 40); -20% stop would fire in 39% of 365-day windows (cap 25%) |
| 1 regression ETH-EUR | FAIL | maxDD 52.5% vs 41.7% | final x20.36 vs x12.98 (need >= 80% of champion) |
| 2 placebo ETH-EUR | PASS | maxdd: beats 98.3% of 2000 block placebos (need 95%) |
| 3 out-of-sample ETH-EUR | PASS | Sharpe from 2023-01-01: 0.84 vs champion 0.71 (tolerance 0.15) |
| 3b bootstrap Sharpe difference ETH-EUR | FAIL | 5th percentile of Sharpe(new)-Sharpe(champion) over 2000 paired 20-day block resamples: -0.30 (floor -0.25) |
| 5 robustness ex-2022 ETH-EUR | FAIL | maxDD 49.9% vs 41.7% | final x26.99 vs x16.10 |
| 5 robustness fees x2 ETH-EUR | FAIL | maxDD 55.9% vs 41.7% | final x15.15 vs x11.62 |
| 6 turnover and kill-switch ETH-EUR | FAIL | 17.8 exposure changes/yr (cap 40); -20% stop would fire in 31% of 365-day windows (cap 25%) |
| 4 holdout vs constant exposure | FAIL | lower maxDD than the constant-exposure comparator on 2 of 16 coins (need 9) |
| 7 pre-registration | PASS | hypothesis, null and primary_metric present; hash written to ledger before results |

Holdout detail:
- ADA-EUR: new 80.8% vs constant-scale 58.3%
- ATOM-EUR: new 81.0% vs constant-scale 67.1%
- AVAX-EUR: new 74.6% vs constant-scale 53.3%
- BCH-EUR: new 85.7% vs constant-scale 76.5%
- DOGE-EUR: new 78.4% vs constant-scale 78.7%
- DOT-EUR: new 83.8% vs constant-scale 58.1%
- ETC-EUR: new 72.0% vs constant-scale 61.9%
- LINK-EUR: new 94.6% vs constant-scale 84.7%
- LTC-EUR: new 93.5% vs constant-scale 83.8%
- LUNA-EUR: new 91.3% vs constant-scale 77.7%
- NEAR-EUR: new 85.4% vs constant-scale 75.2%
- SOL-EUR: new 83.6% vs constant-scale 64.7%
- TRX-EUR: new 63.3% vs constant-scale 68.9%
- UNI-EUR: new 66.1% vs constant-scale 52.0%
- XLM-EUR: new 85.1% vs constant-scale 84.5%
- XRP-EUR: new 83.7% vs constant-scale 66.9%

Limits: BTC/ETH count as about 1.3 independent observations; only coins alive today; Bitvavo EUR daily closes; no slippage; the champion and the new spec were both chosen with knowledge of this history. A pass is a reason to forward-paper-test, not evidence of an edge.
