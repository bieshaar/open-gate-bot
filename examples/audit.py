"""Strategy audit for agents: python3 -I audit.py '{"asset":"BTC-EUR","type":"breakout","n":55,"m":20,"trials":5}'
Rule types: breakout(n,m), sma(n), momentum(k), rsi(n,lo,hi). Long/flat daily, lag-1 fills, Bitvavo EUR data (hist_*.json).
Report: net result vs hold, per-year, fee sensitivity, exposure-matched placebo (random same-exposure days), parameter-neighbour plateau, deflated-Sharpe hurdle."""
import json,sys,math,random,statistics as st
random.seed(7)
def load(a): d=json.load(open(f'./hist_{a}.json')); return [t for t,_ in d],[p for _,p in d]
def signal(x,spec):
    n=len(x); pos=[0]*n; on=False; t=spec['type']
    for i in range(max(spec.get('n',0),spec.get('k',0),spec.get('m',0),60),n):
        if t=='breakout':
            if not on and x[i]>max(x[i-spec['n']:i]): on=True
            elif on and x[i]<min(x[i-spec['m']:i]): on=False
        elif t=='sma': on=x[i]>sum(x[i-spec['n']+1:i+1])/spec['n']
        elif t=='momentum': on=x[i]>x[i-spec['k']]
        elif t=='rsi':
            d=[x[j]-x[j-1] for j in range(i-spec['n']+1,i+1)];g=sum(max(v,0) for v in d);l=sum(max(-v,0) for v in d);r=100 if l==0 else 100-100/(1+g/l)
            if not on and r<spec['lo']: on=True
            elif on and r>spec['hi']: on=False
        pos[i]=1 if on else 0
    return pos
def sim(x,pos,fee,a=0,z=None):  # pos[i] decided at close i, held from close i+1 (lag-1): earns return i+1->i+2
    z=z or len(x); v=1.0; prev=0; rets=[]
    for i in range(a,z-2):
        w=pos[i]
        if w!=prev: v*=1-fee; prev=w
        r=(x[i+2]/x[i+1]-1) if w else 0; v*=1+r; rets.append(r if w else 0)
    return v,rets
def sharpe(r): 
    if len(r)<2: return 0
    s=st.pstdev(r); return st.mean(r)/s*math.sqrt(365) if s else 0
def maxdd(x,pos,fee):
    v=1;pk=1;dd=0;prev=0
    for i in range(len(x)-2):
        w=pos[i]
        if w!=prev: v*=1-fee; prev=w
        if w: v*=x[i+2]/x[i+1]
        pk=max(pk,v); dd=max(dd,1-v/pk)
    return dd
def audit(spec):
    ts,x=load(spec['asset']); pos=signal(x,spec); fee=.0025; N=int(spec.get('trials',1))
    v,rets=sim(x,pos,fee); hold=x[-1]/x[61]; expo=sum(pos[60:])/(len(x)-60)
    v0,r0=sim(x,pos,0); out=[f"# Audit: {spec}", f"Data: Bitvavo {spec['asset']} daily, {len(x)} days. Fill lag-1, fee 0.25%/side, long/flat."]
    out.append(f"Net x{v:.2f} vs hold x{hold:.2f} | Sharpe {sharpe(rets):.2f} (hold {sharpe([x[i+1]/x[i]-1 for i in range(61,len(x)-1)]):.2f}) | maxDD {maxdd(x,pos,fee)*100:.0f}% | exposure {expo*100:.0f}% | trades {sum(1 for i in range(1,len(pos)) if pos[i]!=pos[i-1])}")
    out.append("Fee sensitivity: "+", ".join(f"{f*100:.2f}% x{sim(x,pos,f)[0]:.2f}" for f in (.0025,.005,.01)))
    # per year
    yrs={}
    import time
    for i,t in enumerate(ts): yrs.setdefault(time.gmtime(t/1000).tm_year,[]).append(i)
    row=[]
    for y,ix in sorted(yrs.items()):
        if len(ix)<200 or ix[0]<60: continue
        a,z=ix[0],min(ix[-1]+1,len(x)); row.append(f"{y}: {sim(x,pos,fee,a,z)[0]:.2f}/{x[z-1]/x[a]:.2f}")
    out.append("Per year rule/hold: "+" | ".join(row))
    # placebo: random positions with same number of in-market days, gross of fees, compare total gross return
    k=sum(pos[60:]); idx=list(range(60,len(x)-2)); sims=[]
    for _ in range(1500):
        s=set(random.sample(idx,k)); p=[1 if i in s else 0 for i in range(len(x))]; sims.append(sim(x,p,0)[0])
    pct=sum(1 for s in sims if s<v0)/len(sims)
    out.append(f"Exposure-matched placebo (gross of fees): rule x{v0:.2f} beats {pct*100:.0f}% of 1500 random same-exposure day sets (median placebo x{st.median(sims):.2f}). ~50% = no timing information; >95% suggests timing.")
    # plateau
    nb=[]
    t=spec['type']; keys={'breakout':['n','m'],'sma':['n'],'momentum':['k'],'rsi':['lo','hi']}[t]
    for key in keys:
        for f in (.7,1.3):
            s2=dict(spec); s2[key]=max(2,round(spec[key]*f)) if key not in('lo','hi') else spec[key]+(5 if f>1 else -5)
            nb.append((key,s2[key],sim(x,signal(x,s2),fee)[0]))
    out.append("Neighbours (+-30%): "+", ".join(f"{k}={v}: x{r:.2f}" for k,v,r in nb)+f" | own x{v:.2f}. A rule far above its neighbours is probably luck.")
    sr=sharpe(rets); hurdle=(math.sqrt(2*math.log(max(N,2)))-0)/math.sqrt(len(rets)/365)
    out.append(f"Trials declared: {N}. Rough Sharpe hurdle for the best of {N} zero-skill rules ~{hurdle:.2f}; rule Sharpe {sr:.2f}. Excess over hold is what to judge.")
    out.append("Limits: one asset, only coins alive today, one regime-heavy period, no slippage, no shorting. Not financial advice.")
    return "\n".join(out)
if __name__=='__main__':
    print(audit(json.loads(sys.argv[1])))
