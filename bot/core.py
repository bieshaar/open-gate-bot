"""Core of the open test-gated bot. Interprets declarative JSON specs only; never executes code from a spec.
Daily closes, long/flat (fractional exposure allowed), signal at close t, fill at close t+1 (lag-1),
fee 0.25% per unit of exposure traded, exposure only changes if it moves >= 0.2 or flips flat<->invested."""
import json, os, hashlib, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEE = 0.0025; BAND = 0.2; START = 395   # evaluation starts at index 395 for every asset (labels need a year of history)
RULES = {'hold': {}, 'momentum': {'k': (5, 365)}, 'sma': {'n': (5, 400)}, 'breakout': {'n': (5, 200), 'm': (2, 200)},
         'rsi': {'n': (3, 60), 'lo': (1, 50), 'hi': (50, 99)}}
SIZING = {'none': {}, 'stress_scale': {'vol_days': (10, 60), 'pct': (50, 99), 'hist_days': (120, 365), 'dd_pct': (10, 60), 'scale_pct': (0, 90)}}
METRICS = ('maxdd', 'return')

def validate(s):
    for k in ('name', 'author', 'hypothesis', 'null'):
        assert isinstance(s.get(k), str) and 0 < len(s[k]) <= 600, f'missing or too long: {k}'
    assert s['name'].replace('-', '').replace('_', '').isalnum() and len(s['name']) <= 40, 'bad name'
    assert s.get('primary_metric') in METRICS, 'primary_metric must be maxdd or return (declared in advance)'
    rs = s.get('rules'); assert isinstance(rs, list) and 1 <= len(rs) <= 12, '1-12 rules'
    for r in rs:
        t = r.get('type'); assert t in RULES, f'unknown rule type {t}'
        for k, (lo, hi) in RULES[t].items(): assert isinstance(r.get(k), int) and lo <= r[k] <= hi, f'{t}.{k} must be int in [{lo},{hi}]'
        assert set(r) <= set(RULES[t]) | {'type'}, 'unknown keys in rule'
    assert s.get('combine', 'mean') in ('mean', 'all', 'any'), 'combine'
    z = s.get('sizing', {'type': 'none'}); t = z.get('type'); assert t in SIZING, f'unknown sizing {t}'
    for k, (lo, hi) in SIZING[t].items(): assert isinstance(z.get(k), int) and lo <= z[k] <= hi, f'sizing.{k} must be int in [{lo},{hi}]'
    assert set(z) <= set(SIZING[t]) | {'type'}, 'unknown keys in sizing'
    if t == 'stress_scale': assert z['vol_days'] + z['hist_days'] <= START, 'vol_days+hist_days too long'
    assert set(s) <= {'name', 'author', 'hypothesis', 'null', 'primary_metric', 'rules', 'combine', 'sizing'}, 'unknown top-level keys'
    return True

def canon(s): return json.dumps(s, sort_keys=True, separators=(',', ':'))
def spec_hash(s): return hashlib.sha256(canon(s).encode()).hexdigest()

def load(asset):
    d = json.load(open(os.path.join(ROOT, 'data', asset + '.json')))
    return np.array([t for t, _ in d]), np.array([p for _, p in d], float)

def _rule(x, r):
    n = len(x); out = np.zeros(n); t = r['type']; w0 = max(r.get('n', 0), r.get('k', 0), r.get('m', 0), 60)
    if t == 'hold': out[:] = 1; return out
    if t == 'momentum': out[r['k']:] = x[r['k']:] > x[:-r['k']]; out[:w0] = 0; return out
    if t == 'sma':
        c = np.cumsum(np.insert(x, 0, 0)); m = np.full(n, np.nan); m[r['n'] - 1:] = (c[r['n']:] - c[:-r['n']]) / r['n']
        out = np.nan_to_num((x > m).astype(float)); out[:w0] = 0; return out
    on = 0
    for i in range(w0, n):
        if t == 'breakout':
            if not on and x[i] > x[i - r['n']:i].max(): on = 1
            elif on and x[i] < x[i - r['m']:i].min(): on = 0
        else:
            d = np.diff(x[i - r['n']:i + 1]); g = d[d > 0].sum(); l = -d[d < 0].sum(); v = 100 if l == 0 else 100 - 100 / (1 + g / l)
            if not on and v < r['lo']: on = 1
            elif on and v > r['hi']: on = 0
        out[i] = on
    return out

def stress_label(x, z):
    n = len(x); lr = np.diff(np.log(x), prepend=np.nan); vol = np.full(n, np.nan); vd = z['vol_days']
    for i in range(vd, n): vol[i] = lr[i - vd + 1:i + 1].std(ddof=1)
    ath = np.maximum.accumulate(x); st = np.zeros(n); h = z['hist_days']
    for i in range(vd + h, n):
        thr = np.percentile(vol[i - h + 1:i + 1], z['pct'])
        st[i] = 1.0 if (vol[i] > thr or x[i] < (1 - z['dd_pct'] / 100) * ath[i]) else 0.0
    return st

def target(s, x):
    sig = [_rule(x, r) for r in s['rules']]; c = s.get('combine', 'mean')
    t = np.mean(sig, axis=0) if c == 'mean' else (np.min(sig, axis=0) if c == 'all' else np.max(sig, axis=0))
    z = s.get('sizing', {'type': 'none'})
    if z['type'] == 'stress_scale': t = t * np.where(stress_label(x, z) == 1, z['scale_pct'] / 100.0, 1.0)
    return t

def band_filter(t):
    w = np.zeros(len(t)); cur = 0.0
    for i, v in enumerate(t):
        if abs(v - cur) >= BAND - 1e-12 or ((v == 0) != (cur == 0)): cur = v
        w[i] = cur
    return w

def daily_returns(x, w, a=START, fee=FEE):
    """r_i for i in [a, n-3]: w_i is decided at close i and earns close(i+1) -> close(i+2); fee on exposure traded."""
    n = len(x); ret = x[2:] / x[1:-1] - 1            # ret[i] = x[i+2]/x[i+1]-1, i in [0, n-3]
    ww = w[:n - 2]; prev = np.concatenate([[w[a - 1]], ww[a:-1]])
    return ww[a:] * ret[a:] - fee * np.abs(ww[a:] - prev)

def stats(r):
    e = np.cumprod(1 + r); pk = np.maximum.accumulate(np.concatenate([[1.0], e]))[1:]
    sd = r.std(); return {'maxdd': float((1 - e / pk).max()), 'final': float(e[-1]), 'sharpe': float(r.mean() / sd * np.sqrt(365)) if sd else 0.0}
