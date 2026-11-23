"""Purity, measurements, outliers, holes per eta bin in the forward tests.

Usage: python3 fwd_purity.py <run dir> <label> [<label> ...]   e.g. truth_smeared seeded ele_truth_smeared
"""
import uproot,numpy as np,awkward as ak,sys
R=sys.argv[1]; LABELS=sys.argv[2:]
bins=[(2.8,3.0),(3.0,3.2),(3.2,3.5)]
for seed in LABELS:
    print("=====",seed)
    print(f"{'variant':11s} {'eta':9s} {'tracks':>6s} {'purity':>7s} {'impure%':>7s} {'nMeas':>6s} {'nOutl':>6s} {'nHoles':>6s}")
    for v in ["gen1","gen3","gen3nocalo"]:
        f=uproot.open(f"{R}/{v}/out/{seed}/tracksummary_ckf.root"); t=f[f.keys()[0]]
        a=t.arrays(["nMeasurements","nMajorityHits","nOutliers","nHoles","t_eta","trackClassification"])
        nm=ak.flatten(a.nMeasurements).to_numpy().astype(float); nmaj=ak.flatten(a.nMajorityHits).to_numpy()
        eta=ak.flatten(a.t_eta).to_numpy(); no=ak.flatten(a.nOutliers).to_numpy(); nh=ak.flatten(a.nHoles).to_numpy()
        pur=nmaj/nm
        for lo,hi in bins+[(2.8,3.5)]:
            m=(eta>=lo)&(eta<hi)&np.isfinite(pur)
            print(f"{v:11s} {lo:.1f}-{hi:.1f}  {m.sum():6d} {pur[m].mean():7.4f} {100*np.mean(pur[m]<1):7.2f} {nm[m].mean():6.2f} {no[m].mean():6.3f} {nh[m].mean():6.3f}")
