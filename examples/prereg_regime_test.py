"""Runs prereg_regime_sizing.md exactly as written. Equity: r_i = w_i*(x[i+2]/x[i+1]-1) - fee*|dw| ; w decided at close i (lag-1).
Rebalance filter: exposure changes only if it moves >=0.2 or switches flat<->invested. Fee charged on traded fraction."""
import sys,json,math,time,random,numpy as np
sys.path.insert(0,'.'); import audit
random.seed(2026); np.random.seed(2026); FEE=.0025; DRAWS=4000
def labels(x):
    x=np.array(x); n=len(x); lr=np.diff(np.log(x),prepend=np.nan)
    vol=np.full(n,np.nan)
    for i in range(30,n): vol[i]=lr[i-29:i+1].std(ddof=1)
    ath=np.maximum.accumulate(x); st=np.full(n,np.nan)
    for i in range(30+365,n):
        h=vol[i-364:i+1]; thr=np.percentile(h,80)
        st[i]=1.0 if (vol[i]>thr or x[i]<0.7*ath[i]) else 0.0
    return st,vol
def filt(target):
    w=np.zeros(len(target)); cur=0.0
    for i,t in enumerate(target):
        if abs(t-cur)>=0.2-1e-12 or ((t==0)!=(cur==0)): cur=t
        w[i]=cur
    return w
def rets(x,w,a):
    x=np.array(x); n=len(x); r=np.zeros(n); prev=w[a-1] if a>0 else 0
    for i in range(a,n-2):
        r[i]=w[i]*(x[i+2]/x[i+1]-1)-FEE*abs(w[i]-prev); prev=w[i]
    return r[a:n-2]
def dd_eq(r):
    e=np.cumprod(1+r); pk=np.maximum.accumulate(np.concatenate([[1],e]))[1:]; return (1-e/pk).max(), e[-1]
def run_coin(asset, draws=0):
    ts,x=audit.load(asset); n=len(x); a=395
    if n-a<250: return None
    base=np.array(audit.signal(x,{'type':'breakout','n':55,'m':20}),float)
    st,vol=labels(x); y=np.array([time.gmtime(t/1000).tm_year for t in ts])[a:n-2]
    tgt=base*np.where(st==1,0.5,1.0); tgt[:a]=base[:a]
    def arm(t): return rets(x,filt(t),a)
    rb=arm(base); rt=arm(tgt)
    out={'asset':asset,'days':n-a-2,'dd_base':dd_eq(rb),'dd_tr':dd_eq(rt),'mexp_tr':float(filt(tgt)[a:].mean()),'mexp_base':float(filt(base)[a:].mean())}
    if not draws: return out
    k=out['mexp_tr']/out['mexp_base']; rc=arm(base*k)
    v=np.minimum(1,0.0)  # placeholder
    lo,hi=0.1,10
    def mexp_vt(T): return filt(base*np.minimum(1,T/np.maximum(vol,1e-9)))[a:].mean()
    for _ in range(40):
        mid=(lo+hi)/2
        if mexp_vt(mid*0.03)>out['mexp_tr']: hi=mid
        else: lo=mid
    T=lo*0.03; rv=arm(base*np.minimum(1,T/np.maximum(vol,1e-9)))
    out['dd_const']=dd_eq(rc); out['dd_vt']=dd_eq(rv); out['mexp_vt']=float(filt(base*np.minimum(1,T/np.maximum(vol,1e-9)))[a:].mean())
    m22=(y!=2022)
    out['x22']={'base':dd_eq(rb[m22]),'tr':dd_eq(rt[m22]),'const':dd_eq(rc[m22]),'vt':dd_eq(rv[m22])}
    valid=np.arange(30+365,n); sh_dd=[];sh_dd22=[]
    for _ in range(draws):
        off=random.randint(60,len(valid)-60); s2=st.copy(); s2[valid]=np.roll(st[valid],off)
        t2=base*np.where(s2==1,0.5,1.0); t2[:a]=base[:a]; r2=arm(t2)
        sh_dd.append(dd_eq(r2)[0]); sh_dd22.append(dd_eq(r2[m22])[0])
    out['share']=float(np.mean(np.array(sh_dd)>out['dd_tr'][0])); out['share22']=float(np.mean(np.array(sh_dd22)>out['x22']['tr'][0]))
    out['shift_median_dd']=float(np.median(sh_dd))
    return out
res={}
for c in ('BTC-EUR','ETH-EUR'):
    r=run_coin(c,DRAWS); res[c]=r
    d=r
    print(f"\n{c} (eval days {d['days']}, from index 395)")
    print(f"  base 55/20   maxDD {d['dd_base'][0]*100:.1f}% final x{d['dd_base'][1]:.2f} mean exposure {d['mexp_base']:.2f}")
    print(f"  treatment    maxDD {d['dd_tr'][0]*100:.1f}% final x{d['dd_tr'][1]:.2f} mean exposure {d['mexp_tr']:.2f}")
    print(f"  const-scale  maxDD {d['dd_const'][0]*100:.1f}% final x{d['dd_const'][1]:.2f}")
    print(f"  vol-target   maxDD {d['dd_vt'][0]*100:.1f}% final x{d['dd_vt'][1]:.2f} (mean exposure {d['mexp_vt']:.2f})")
    print(f"  shifted-label null: median maxDD {d['shift_median_dd']*100:.1f}%; treatment beats {d['share']*100:.1f}% of {DRAWS}")
    print(f"  ex-2022: base {d['x22']['base'][0]*100:.1f}% tr {d['x22']['tr'][0]*100:.1f}% const {d['x22']['const'][0]*100:.1f}% vt {d['x22']['vt'][0]*100:.1f}%; beats {d['share22']*100:.1f}% of shifted")
    print(f"  cost guard: final tr/base = {d['dd_tr'][1]/d['dd_base'][1]:.2f}")
    ok=[d['share']>=.95, d['dd_tr'][1]>=.8*d['dd_base'][1], d['dd_tr'][0]<d['dd_const'][0] and d['dd_tr'][0]<d['dd_vt'][0],
        d['share22']>=.95 and d['x22']['tr'][0]<d['x22']['const'][0] and d['x22']['tr'][0]<d['x22']['vt'][0] and d['dd_tr'][1]>=.8*d['dd_base'][1]]
    d['ok']=ok; print('  criteria [primary,costguard,comparators,ex2022]:',ok)
import glob
hold=[];skip=[]
for f in sorted(glob.glob('./hist_*-EUR.json')):
    a=f.split('hist_')[1][:-5]
    if a in ('BTC-EUR','ETH-EUR'): continue
    r=run_coin(a)
    if r is None: skip.append(a); continue
    better=r['dd_tr'][0]<r['dd_base'][0]; hold.append((a,better,r['dd_base'][0],r['dd_tr'][0]))
    print(f"  holdout {a:9} DD base {r['dd_base'][0]*100:5.1f}% -> tr {r['dd_tr'][0]*100:5.1f}%  {'better' if better else 'NOT better'}")
nb=sum(1 for h in hold if h[1]); print(f"\nHoldout: better on {nb} of {len(hold)} evaluable coins (need 9 of 16); skipped for short history: {skip}")
allok=all(all(res[c]['ok']) for c in res)
print('BTC+ETH all criteria:',allok,'| holdout pass:',nb>=9,'| ruling:', 'CONFIRMED' if allok and nb>=9 else ('SUGGESTIVE' if allok else 'FAILED'))
