One spec per pull request, only files under `bot/specs/`. Before opening it, write the hypothesis, null and primary metric into the spec; do not tune after seeing results (each registered variant counts as a trial).
- [ ] The spec validates (`python3 -I -c "import json,sys; sys.path.insert(0,'bot'); import core; core.validate(json.load(open('bot/specs/YOURSPEC.json')))"`)
- [ ] I did not change any other file
- [ ] Paper research only; no keys, no tokens, no live trading
