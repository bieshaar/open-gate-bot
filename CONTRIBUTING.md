# Contributing
1. Add one JSON file under `bot/specs/` with `name`, `author`, `hypothesis`, `null` and `primary_metric` (`maxdd` or `return`), written **before** you look at results.
2. Open a pull request that changes **only** that file. CI runs the gate on it (code taken from `main`, never from your branch) and comments the full result. You can run the same command locally first: `python3 -I gate/run_gate.py bot/specs/<yourspec>.json --no-ledger`. Maintainers add the ledger rows and the result file on merge; nobody edits old ledger rows.
3. One spec per pull request. Do not tune a spec until it passes: each registered variant counts as a trial, and the count is public.
4. Gate changes are proposed as an issue (what bias or gap it fixes, with numbers). Maintainers implement them as a new gate version; old results keep their old version label and are never rewritten.
5. No code execution from specs, no network access in the core or the gate, no keys, tokens or live trading code in this repository.
Negative results are welcome and count the same as passes. Recognition (Collective Kudos) is reputation only: no amounts, no value, no tokens.
