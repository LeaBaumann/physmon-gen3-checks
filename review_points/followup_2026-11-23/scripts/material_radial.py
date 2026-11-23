"""Material (in X0) per radius for |eta| < 0.5, from material-validation output.

Usage: python3 material_radial.py <gen1>_propagated.root <gen3>_propagated.root
"""
import uproot,numpy as np,awkward as ak,sys
redges=np.array([0,30,50,90,140,200,330,450,600,720,950,1100,1300])
for tag in sys.argv[1:]:
    t=uproot.open(tag)["material_tracks"].arrays(["v_eta","mat_r","mat_step_length","mat_X0"])
    sel=abs(t.v_eta)<0.5; n=ak.sum(sel)
    r=ak.flatten(t.mat_r[sel]).to_numpy()
    x0=ak.flatten(ak.where(t.mat_X0>0,t.mat_step_length/t.mat_X0,0)[sel]).to_numpy()
    h,_=np.histogram(r,redges,weights=x0)
    print(tag.split('/')[-1], " ".join(f"{v/n:.4f}" for v in h))
print("r-bins:", " ".join(f"{a}-{b}" for a,b in zip(redges[:-1],redges[1:])))
