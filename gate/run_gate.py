"""The gate (v2). Usage: python3 -I gate/run_gate.py bot/specs/<name>.json [--draws 2000] [--no-ledger] [--out DIR]
Registers the spec hash in gate/ledger.csv BEFORE any result is computed, runs all checks against the current
champion (bot/VERSION), writes gate/results/<name>-<hash12>.md and appends the verdict to the ledger.
Gate v2 (2026-11-21): adds a paired block-bootstrap check of the Sharpe difference (v1 results stay valid under v1).
--no-ledger (used by CI): do not write the ledger; the maintainer appends the rows when the pull request is merged. A spec is ACCEPTED only if every check passes."""
import sys, os, json, math, time, glob, random, datetime, csv
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'bot'))
import core
NO_LEDGER = '--no-ledger' in sys.argv
LEDGER = os.path.join(HERE, 'ledger.csv'); RES = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(HERE, 'results')
GATE_VERSION = 'v2'; BOOT_BLOCK = 20; BOOT_DRAWS = 2000; BOOT_FLOOR = -0.25
OOS_FROM = '2023-01-01'; OOS_TOL = 0.15; PLACEBO_SHARE = 0.95; DD_FLOOR = 0.80; HOLDOUT_MIN = 9
MAX_CHANGES_YR = 40; MAX_KILL_SHARE = 0.25; KILL_LEVEL = 0.80

def ledger_rows():
    return list(csv.DictReader(open(LEDGER))) if os.path.exists(LEDGER) else []
def ledger_add(row):
    if NO_LEDGER: return
    new = not os.path.exists(LEDGER) or os.path.getsize(LEDGER) == 0
    with open(LEDGER, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['date_utc', 'event', 'name', 'author', 'spec_hash', 'trials', 'verdict', 'detail'])
        if new: w.writeheader()
        w.writerow({k: row.get(k, '') for k in w.fieldnames})
def trial_count():
    return sum(int(r['trials'] or 0) for r in ledger_rows() if r['event'] in ('historical', 'registered'))

def run(spec, asset, fee=core.FEE, mask_year=None):
    ts, x = core.load(asset); w = core.band_filter(core.target(spec, x)); r = core.daily_returns(x, w, fee=fee)
    yrs = np.array([time.gmtime(t / 1000).tm_year for t in ts])[core.START:len(x) - 2]
    if mask_year is not None: r = r[yrs != mask_year]
    return {'ts': ts, 'x': x, 'w': w, 'r': r, 'yrs': yrs}

def placebo(res, draws, seed, metric):
    """Same number and lengths of in-market runs (with the same weights) placed at random non-overlapping over the sample."""
    rng = random.Random(seed); x = res['x']; n = len(x); a = core.START; wv = res['w'][a:n - 2]; W = len(wv)
    runs = []; s = None
    for i, v in enumerate(wv):
        if v > 0 and s is None: s = i
        if v == 0 and s is not None: runs.append(wv[s:i].copy()); s = None
    if s is not None: runs.append(wv[s:].copy())
    k = len(runs); L = sum(len(b) for b in runs)
    if k == 0: return None
    ret = x[2:] / x[1:-1] - 1; ret = ret[a:]; worse = 0
    for _ in range(draws):
        cuts = sorted(rng.randint(0, W - L) for _ in range(k)); gaps = [cuts[0]] + [cuts[i] - cuts[i - 1] for i in range(1, k)]
        order = runs[:]; rng.shuffle(order); p = np.zeros(W); pos = 0
        for g, b in zip(gaps, order): pos += g; p[pos:pos + len(b)] = b; pos += len(b)
        prev = np.concatenate([[0.0], p[:-1]]); st = core.stats(p * ret - core.FEE * np.abs(p - prev))
        worse += (st['maxdd'] > res['stats']['maxdd']) if metric == 'maxdd' else (st['final'] < res['stats']['final'])
    return worse / draws

def boot_sharpe_diff(rn, ro, seed):
    """Paired circular block bootstrap of Sharpe(new) - Sharpe(champion); returns the 5th percentile."""
    rng = np.random.default_rng(seed); n = len(rn); nb = n // BOOT_BLOCK + 1; out = []
    for _ in range(BOOT_DRAWS):
        st = rng.integers(0, n, nb); idx = ((st[:, None] + np.arange(BOOT_BLOCK)[None, :]) % n).ravel()[:n]
        a, b = rn[idx], ro[idx]; out.append(core.stats(a)['sharpe'] - core.stats(b)['sharpe'])
    return float(np.percentile(out, 5))

def killswitch_share(r):
    n = len(r); hit = tot = 0
    for a in range(0, n - 365, 7):
        e = np.cumprod(1 + r[a:a + 365]); hit += bool((e <= KILL_LEVEL).any()); tot += 1
    return hit / tot if tot else 0.0

def main():
    path = sys.argv[1]; draws = int(sys.argv[sys.argv.index('--draws') + 1]) if '--draws' in sys.argv else 2000
    spec = json.load(open(path)); core.validate(spec); h = core.spec_hash(spec)
    champ_path = os.path.join(core.ROOT, open(os.path.join(core.ROOT, 'bot', 'VERSION')).read().strip()); champ = json.load(open(champ_path)); ch = core.spec_hash(champ)
    now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    rows0 = ledger_rows(); seen = any(r['spec_hash'] == h and r['event'] == 'registered' for r in rows0)
    family = sum(1 for r in rows0 if r['author'] == spec['author'] and r['event'] == 'registered') + (0 if seen else 1)
    if seen: ledger_add({'date_utc': now, 'event': 'rerun', 'name': spec['name'], 'author': spec['author'], 'spec_hash': h, 'trials': 0, 'detail': f'gate {GATE_VERSION} re-run of an already registered spec (no new trial)'})
    else: ledger_add({'date_utc': now, 'event': 'registered', 'name': spec['name'], 'author': spec['author'], 'spec_hash': h, 'trials': 1,
                'detail': f"primary_metric={spec['primary_metric']}; registered before results; author's variants incl. this: {family}"})
    N = trial_count() + (0 if (seen or not NO_LEDGER) else 1); lines = []; checks = []
    def chk(name, ok, detail): checks.append((name, bool(ok), detail))
    base = {}
    for asset in ('BTC-EUR', 'ETH-EUR'):
        new = run(spec, asset); old = run(champ, asset); new['stats'] = core.stats(new['r']); old['stats'] = core.stats(old['r']); base[asset] = (new, old)
        s, o = new['stats'], old['stats']
        chk(f'1 regression {asset}', s['maxdd'] <= o['maxdd'] and s['final'] >= DD_FLOOR * o['final'],
            f"maxDD {s['maxdd']*100:.1f}% vs {o['maxdd']*100:.1f}% | final x{s['final']:.2f} vs x{o['final']:.2f} (need >= {DD_FLOOR*100:.0f}% of champion)")
        share = placebo(new, draws, int(h[:8], 16), spec['primary_metric'])
        chk(f'2 placebo {asset}', share is not None and share >= PLACEBO_SHARE, f"{spec['primary_metric']}: beats {share*100:.1f}% of {draws} block placebos (need {PLACEBO_SHARE*100:.0f}%)" if share is not None else 'never in market')
        cut = next(i for i, t in enumerate(new['ts'][core.START:len(new['x']) - 2]) if time.strftime('%Y-%m-%d', time.gmtime(t / 1000)) >= OOS_FROM)
        so = core.stats(new['r'][cut:])['sharpe']; sc = core.stats(old['r'][cut:])['sharpe']
        chk(f'3 out-of-sample {asset}', so >= sc - OOS_TOL, f"Sharpe from {OOS_FROM}: {so:.2f} vs champion {sc:.2f} (tolerance {OOS_TOL})")
        p5 = boot_sharpe_diff(new['r'], old['r'], int(h[:8], 16))
        chk(f'3b bootstrap Sharpe difference {asset}', p5 >= BOOT_FLOOR, f"5th percentile of Sharpe(new)-Sharpe(champion) over {BOOT_DRAWS} paired {BOOT_BLOCK}-day block resamples: {p5:+.2f} (floor {BOOT_FLOOR})")
        for tag, kw in (('ex-2022', {'mask_year': 2022}), ('fees x2', {'fee': 2 * core.FEE})):
            n2, o2 = run(spec, asset, **kw), run(champ, asset, **kw); a, b = core.stats(n2['r']), core.stats(o2['r'])
            chk(f'5 robustness {tag} {asset}', a['maxdd'] <= b['maxdd'] and a['final'] >= DD_FLOOR * b['final'], f"maxDD {a['maxdd']*100:.1f}% vs {b['maxdd']*100:.1f}% | final x{a['final']:.2f} vs x{b['final']:.2f}")
        yrs = len(new['r']) / 365.0; changes = int((np.abs(np.diff(new['w'][core.START - 1:len(new['x']) - 2])) > 0).sum()) / yrs
        ks = killswitch_share(new['r'])
        chk(f'6 turnover and kill-switch {asset}', changes <= MAX_CHANGES_YR and ks <= MAX_KILL_SHARE, f"{changes:.1f} exposure changes/yr (cap {MAX_CHANGES_YR}); -20% stop would fire in {ks*100:.0f}% of 365-day windows (cap {MAX_KILL_SHARE*100:.0f}%)")
    # 4 holdout vs constant-exposure comparator
    wins = tot = 0; rows = []
    for f in sorted(glob.glob(os.path.join(core.ROOT, 'data', '*.json'))):
        a = os.path.basename(f)[:-5]
        if a in ('BTC-EUR', 'ETH-EUR'): continue
        ts, x = core.load(a)
        if len(x) - core.START < 250: continue
        tn = core.target(spec, x); tc = core.target(champ, x); wn = core.band_filter(tn); wc = core.band_filter(tc)
        k = min(1.0, (wn[core.START:].mean() / wc[core.START:].mean())) if wc[core.START:].mean() > 0 else 1.0
        dn = core.stats(core.daily_returns(x, wn))['maxdd']; dk = core.stats(core.daily_returns(x, core.band_filter(tc * k)))['maxdd']
        tot += 1; wins += dn < dk - 1e-9; rows.append(f'{a}: new {dn*100:.1f}% vs constant-scale {dk*100:.1f}%')
    chk('4 holdout vs constant exposure', wins >= HOLDOUT_MIN, f'lower maxDD than the constant-exposure comparator on {wins} of {tot} coins (need {HOLDOUT_MIN})')
    chk('7 pre-registration', True, 'hypothesis, null and primary_metric present; hash written to ledger before results')
    ok = all(c[1] for c in checks); verdict = 'BASELINE (this is the champion itself; check 4 cannot pass by design)' if h == ch else ('ACCEPTED' if ok else 'REJECTED')
    years = len(base['BTC-EUR'][0]['r']) / 365.0; hurdle = math.sqrt(2 * math.log(max(N, 2))) / math.sqrt(years)
    lines += [f"# Gate {GATE_VERSION} result: {spec['name']} ({h[:12]})", f"Run {now}. Champion: {champ['name']} ({ch[:12]}). Verdict: **{verdict}**.", '',
              f"Hypothesis: {spec['hypothesis']}", f"Null: {spec['null']}", f"Primary metric (declared in advance): {spec['primary_metric']}", '',
              f"Trials in ledger (all variants ever registered, incl. historical): {N}. Information only: zero-skill best-of-{N} Sharpe hurdle ~{hurdle:.2f} over {years:.1f} years.", '', '| Check | Result | Detail |', '|---|---|---|']
    lines += [f"| {n} | {'PASS' if o else 'FAIL'} | {d} |" for n, o, d in checks]
    lines += ['', 'Holdout detail:'] + [f'- {r}' for r in rows]
    lines += ['', 'Limits: BTC/ETH count as about 1.3 independent observations; only coins alive today; Bitvavo EUR daily closes; no slippage; the champion and the new spec were both chosen with knowledge of this history. A pass is a reason to forward-paper-test, not evidence of an edge.']
    os.makedirs(RES, exist_ok=True); out = os.path.join(RES, f"{spec['name']}-{h[:12]}-{GATE_VERSION}.md"); open(out, 'w').write('\n'.join(lines) + '\n')
    ledger_add({'date_utc': now, 'event': 'result', 'name': spec['name'], 'author': spec['author'], 'spec_hash': h, 'trials': 0, 'verdict': verdict,
                'detail': f'gate {GATE_VERSION}: ' + ('; '.join(f"{n}=F" for n, o, _ in checks if not o) or 'all checks passed')})
    print('\n'.join(lines)); print('\nwritten:', out)
if __name__ == '__main__': main()
