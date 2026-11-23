"""Material (in X0) per detector region and eta bin, from material-validation output.

Usage: python3 material_regions.py <gen1>_propagated.root <gen3>_propagated.root
Input: Examples/Scripts/Python/material_validation.py -p (see README).
"""
import uproot,numpy as np,awkward as ak,sys
regions=[("BP r<30",lambda r,z: r<30),
         ("Pixel",lambda r,z:(r>=30)&(r<200)&(z<1600)),
         ("SStrip",lambda r,z:(r>=200)&(r<720)&(z<3000) | ((r<200)&(z>=1600)&(z<3000))),
         ("LStrip",lambda r,z:(r>=720)&(r<1100)&(z<3000)),
         ("aussen",lambda r,z:(r>=1100)|(z>=3000))]
edges=np.arange(-3.5,3.51,0.5)
res={}
for tag in sys.argv[1:]:
    t=uproot.open(f"{tag}")["material_tracks"].arrays(["v_eta","t_X0","mat_r","mat_z","mat_step_length","mat_X0"])
    r=t.mat_r; z=abs(t.mat_z)
    x0=ak.where(t.mat_X0>0,t.mat_step_length/t.mat_X0,0)
    eta=t.v_eta.to_numpy(); idx=np.digitize(eta,edges)-1
    out={}
    for name,f in regions:
        s=ak.sum(ak.where(f(r,z),x0,0),axis=1).to_numpy()
        out[name]=np.array([s[idx==i].mean() for i in range(len(edges)-1)])
    out["tracker"]=sum(out[n] for n,_ in regions[:4])
    out["t_X0 total"]=np.array([t.t_X0.to_numpy()[idx==i].mean() for i in range(len(edges)-1)])
    res[tag]=out
a,b=[res[k] for k in sys.argv[1:]]
cen=0.5*(edges[1:]+edges[:-1])
print("eta  | " + " | ".join(f"{n:>17s}" for n in a))
print("     | " + " | ".join(f"{'gen1   gen3':>17s}" for n in a))
for i,c in enumerate(cen):
    print(f"{c:+.2f}| "+" | ".join(f"{a[n][i]:7.4f} {b[n][i]:7.4f}" + ("  " ) for n in a))
