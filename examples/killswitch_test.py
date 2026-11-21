s=open('./search.py').read().split("fams=[")[0]; exec(s)
import numpy as np
def ens(x): return 0.5*target(x,('momens',KS))+0.5*target(x,('brkens',((20,10),(55,20),(100,50))))
tg=[ens(X[a]) for a in X]
def window(a,z,rule,cool=0):
    cur=[0.0,0.0]; v=1.0; start=1.0; halted_until=-1; fired=0; final_halt=False
    for i in range(a,z-2):
        if final_halt: break
        if i<halted_until: continue
        if halted_until>=0 and i==halted_until: start=v   # restart: new reference equity = current
        eq_sleeve=[v/2,v/2]
        # exposure per sleeve
        for j in range(2):
            want=tg[j][i]
            if abs(want-cur[j])>=BAND or (want==0)!=(cur[j]==0): v*=1-abs(want-cur[j])*FEE/2; cur[j]=want
            v*=1+ (cur[j]/2)*r[j,i+2]
        if rule!='none' and v<=0.8*start:
            fired+=1
            v*=1-sum(cur)/2*FEE; cur=[0.0,0.0]
            if rule=='final': final_halt=True
            elif rule=='cool': halted_until=i+1+cool
            elif rule=='signal': halted_until=i+1+cool   # resume at once when targets flip: handled by cool=0 plus re-entry from flat
    return v,fired
res={}
n_w=0
for rule,cool in (('none',0),('final',0),('cool',30),('cool',90),('signal',0)):
    out=[];fr=[]
    for a in range(120,n-380,7):
        v,f=window(a,a+365,rule,cool); out.append(v); fr.append(f)
    out=np.array(out); res[(rule,cool)]=out
    print(f'{rule:6} cooldown {cool:3}d: windows {len(out)}, median x{np.median(out):.2f}, mean x{out.mean():.2f}, 5th pct x{np.percentile(out,5):.2f}, worst x{out.min():.2f}, share ending <0.8: {np.mean(out<0.8)*100:.0f}%, windows with a firing: {np.mean(np.array(fr)>0)*100:.0f}%')
