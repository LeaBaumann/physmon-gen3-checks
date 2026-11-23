"""Ratio Gen3/Gen1 of the KF fitted errors per pT bin (local KF runs, same particles).

Usage: python3 kf_errors_vs_pt.py <gen1 tracksummary_kf.root> <gen3 tracksummary_kf.root>
(in this repository: nstates/data/kf_1000ev/{gen1,gen3}/tracksummary_kf.root)
"""
import sys

import awkward as ak
import numpy as np
import uproot

r = []
for fn in sys.argv[1:3]:
    t = uproot.open(fn)
    a = t[t.keys()[0]].arrays(["event_nr", "t_pT", "err_eLOC0_fit", "err_eTHETA_fit"])
    a = a[ak.num(a.t_pT) == 1]
    x = {k: ak.flatten(a[k]).to_numpy() for k in ["t_pT", "err_eLOC0_fit", "err_eTHETA_fit"]}
    x["ev"] = a.event_nr.to_numpy()
    r.append(x)
ev = np.intersect1d(r[0]["ev"], r[1]["ev"])


def s(i, k):
    o = np.argsort(r[i]["ev"])
    return r[i][k][o[np.searchsorted(r[i]["ev"][o], ev)]]


pt = s(0, "t_pT")
print(f"KF tracks {len(ev)}, median pT {np.median(pt):.1f} GeV, fraction pT < 10 GeV {np.mean(pt < 10):.3f}")
for lo, hi in [(1, 4), (4, 10), (10, 30), (30, 100)]:
    m = (pt >= lo) & (pt < hi)
    print(f"pT {lo:3d}-{hi:3d} GeV: err_d0 {np.median(s(1, 'err_eLOC0_fit')[m] / s(0, 'err_eLOC0_fit')[m]):.3f}"
          f"  err_theta {np.median(s(1, 'err_eTHETA_fit')[m] / s(0, 'err_eTHETA_fit')[m]):.3f}  N={m.sum()}")
