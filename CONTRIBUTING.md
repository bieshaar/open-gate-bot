# Contributing
1. Add one JSON file under `bot/specs/` with `name`, `author`, `hypothesis`, `null` and `primary_metric` (`maxdd` or `return`), written **before** you look at results.
2. Run `python3 -I gate/run_gate.py bot/specs/<yourspec>.json` and commit the new `gate/results/*.md` and `gate/ledger.csv` rows. Do not edit old ledger rows.
3. One spec per pull request. Do not tune a spec until it passes: each registered variant counts as a trial, and the count is public.
4. Pull requests that change `bot/core.py` or `gate/run_gate.py` need an explanation of the bias or gap they fix; gate changes get a new version number and never apply retroactively.
5. No code execution from specs, no network access in the core or the gate, no keys, tokens or live trading code in this repository.
Negative results are welcome and count the same as passes. Recognition (Collective Kudos) is reputation only: no amounts, no value, no tokens.
