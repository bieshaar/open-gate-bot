import sys,random,numpy as np
sys.path.insert(0,'.'); import audit
random.seed(33); FEE=.0025
def runs_of(pos,a):
    out=[];s=None
    for i in range(a,len(pos)):
        if pos[i] and s is None: s=i
        if not pos[i] and s is not None: out.append((s,i)); s=None
    if s is not None: out.append((s,len(pos)))
    return out
for asset in ('BTC-EUR','ETH-EUR'):
    ts,x=audit.load(asset); n=len(x); pos=audit.signal(x,{'type':'breakout','n':55,'m':20})
    a0=60
    v0=audit.sim(x,pos,FEE,0,n)[0]
    def path_val(p):
        v,prev=1.0,0
        pk=1.0;dd=0.0
        for i in range(a0,n-2):
            w=p[i]
            if w!=prev: v*=1-FEE;prev=w
            if w: v*=x[i+2]/x[i+1]
            pk=max(pk,v); dd=max(dd,1-v/pk)
        return v,dd
    rv,rdd=path_val(pos)
    rs=runs_of(pos,a0); k=len(rs); L=sum(e-s for s,e in rs); W=n-2-a0
    sims_v=[]; sims_dd=[]
    for _ in range(4000):
        cuts=sorted(random.randint(0,W-L) for _ in range(k)); gaps=[cuts[0]]+[cuts[i]-cuts[i-1] for i in range(1,k)]+[W-L-cuts[-1]]
        lens=[e-s for s,e in rs]; random.shuffle(lens); h=[]
        for g_,ln in zip(gaps,lens+[0]): h+=[0]*g_+[1]*ln
        h=h[:W]; full=[0]*a0+h+[0,0]
        v,dd=path_val(full); sims_v.append(v); sims_dd.append(dd)
    sims_v=np.array(sims_v); sims_dd=np.array(sims_dd)
    expo=k and L/W
    const=audit.sim(x,[1 if random.random()<0 else 0 for _ in range(n)],0,0,n)  # placeholder unused
    # constant exposure x(expo) baseline: approximate via geometric scaling of returns
    rets=np.array([x[i+1]/x[i]-1 for i in range(a0,n-1)])
    cv=np.prod(1+expo*rets)
    print(f'\n{asset}: rule x{rv:.2f} DD{rdd*100:.1f}% | exposure {expo*100:.0f}% | runs {k}')
    print(f'  whole-sample block placebo (4000 draws): median x{np.median(sims_v):.2f} DD{np.median(sims_dd)*100:.1f}% | rule beats {(sims_v<rv).mean()*100:.1f}% on return, {(sims_dd<rdd).mean()*100:.1f}% on drawdown')
    print(f'  constant {expo*100:.0f}% exposure (no rebalancing cost, simple compounding): x{cv:.2f}')
