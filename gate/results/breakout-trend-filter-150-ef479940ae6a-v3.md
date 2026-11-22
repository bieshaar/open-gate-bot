# Gate v3 result: breakout-trend-filter-150 (ef479940ae6a)
Run 2026-11-22T23:27:45Z. Champion: baseline-55-20 (4035b257aa95). Verdict: **REJECTED**.

Hypothesis: AND-combining plain 55/20 breakout with a 150-day SMA trend filter (long only while close is above its 150-day SMA) cuts whipsaw turnover and improves drawdown/robustness on BTC and ETH versus plain 55/20, without needing the other 16 holdout coins to generalize as well as 55/20 does against a constant-exposure comparator.
Null: Same run structure placed at random gives the same drawdown.
Primary metric (declared in advance): maxdd

Trials in ledger (all variants ever registered, incl. historical): 125. Information only: zero-skill best-of-125 Sharpe hurdle ~1.21 over 6.6 years.

| Check | Result | Detail |
|---|---|---|
| 1 regression BTC-EUR | PASS | maxDD 34.5% (time under water 96%) vs champion 37.6% (tuw 96%) | final x5.71 vs x6.67 (need >= 80% of champion) | cash: maxDD 0.0% / final x1.00; random-entry (same trade count/lengths/exposure, same fees) median: maxDD 55.4% / final x1.86 |
| 2 placebo BTC-EUR | PASS | maxdd: beats 95.7% of 2000 block placebos (need 95%) |
| 3 out-of-sample BTC-EUR | PASS | Sharpe from 2023-01-01: 0.69 vs champion 0.80 (tolerance 0.15) |
| 3b bootstrap Sharpe difference BTC-EUR | FAIL | 5th percentile of Sharpe(new)-Sharpe(champion) over 2000 paired 20-day block resamples: -0.26 (floor -0.25) |
| 5 robustness ex-2022 BTC-EUR | FAIL | maxDD 34.5% vs 37.6% | final x6.11 vs x8.14 |
| 5 robustness fees x2 BTC-EUR | PASS | maxDD 36.8% vs 39.8% | final x5.04 vs x5.89 |
| 6 turnover and kill-switch BTC-EUR | PASS | 7.6 exposure changes/yr (cap 40); -20% stop would fire in 8% of 365-day windows (cap 25%) |
| 1 regression ETH-EUR | PASS | maxDD 41.7% (time under water 94%) vs champion 41.7% (tuw 94%) | final x14.85 vs x12.98 (need >= 80% of champion) | cash: maxDD 0.0% / final x1.00; random-entry (same trade count/lengths/exposure, same fees) median: maxDD 66.1% / final x2.01 |
| 2 placebo ETH-EUR | PASS | maxdd: beats 96.9% of 2000 block placebos (need 95%) |
| 3 out-of-sample ETH-EUR | PASS | Sharpe from 2023-01-01: 0.72 vs champion 0.71 (tolerance 0.15) |
| 3b bootstrap Sharpe difference ETH-EUR | PASS | 5th percentile of Sharpe(new)-Sharpe(champion) over 2000 paired 20-day block resamples: -0.09 (floor -0.25) |
| 5 robustness ex-2022 ETH-EUR | PASS | maxDD 41.7% vs 41.7% | final x15.65 vs x16.10 |
| 5 robustness fees x2 ETH-EUR | PASS | maxDD 41.7% vs 41.7% | final x13.37 vs x11.62 |
| 6 turnover and kill-switch ETH-EUR | PASS | 6.3 exposure changes/yr (cap 40); -20% stop would fire in 12% of 365-day windows (cap 25%) |
| 4 holdout vs constant exposure | FAIL | lower maxDD than the constant-exposure comparator on 3 of 16 coins (need 9). Universe and as-of date: see data/UNIVERSE.md -- these are coins alive on Bitvavo EUR today, applied back over their full history (survivorship bias, not a point-in-time universe). Holdout evaluated 6 times across all registered trials including this one: each look does not by itself invalidate the holdout, but a result chosen because it did well on the holdout after many looks would. |
| 7 pre-registration | PASS | hypothesis, null, primary_metric and the full decision rule were fixed and hashed to the ledger before any check ran (gate v3): gate_version=v3; dd_floor=0.8; placebo_share=0.95; oos_tol=0.15; boot_floor=-0.25; boot_block=20; boot_draws=2000; holdout_min=9; max_changes_yr=40; max_kill_share=0.25; kill_level=0.8; oos_from=2023-01-01 |

Holdout detail:
- ADA-EUR: new 52.1% vs constant-scale 51.9%
- ATOM-EUR: new 58.9% vs constant-scale 58.5%
- AVAX-EUR: new 42.8% vs constant-scale 45.6%
- BCH-EUR: new 72.3% vs constant-scale 69.6%
- DOGE-EUR: new 74.8% vs constant-scale 70.9%
- DOT-EUR: new 54.7% vs constant-scale 50.7%
- ETC-EUR: new 67.8% vs constant-scale 49.9%
- LINK-EUR: new 87.5% vs constant-scale 79.0%
- LTC-EUR: new 76.6% vs constant-scale 73.6%
- LUNA-EUR: new 70.3% vs constant-scale 65.8%
- NEAR-EUR: new 60.3% vs constant-scale 68.7%
- SOL-EUR: new 52.7% vs constant-scale 57.2%
- TRX-EUR: new 77.5% vs constant-scale 65.1%
- UNI-EUR: new 67.3% vs constant-scale 42.7%
- XLM-EUR: new 82.0% vs constant-scale 76.3%
- XRP-EUR: new 68.8% vs constant-scale 65.3%

Limits: BTC/ETH count as about 1.3 independent observations; only coins alive today; Bitvavo EUR daily closes; no slippage; the champion and the new spec were both chosen with knowledge of this history. A pass is a reason to forward-paper-test, not evidence of an edge.
