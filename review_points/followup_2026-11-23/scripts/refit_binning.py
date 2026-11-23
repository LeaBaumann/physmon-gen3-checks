"""Redo the per-pT-bin Gaussian fits of reswidth_qop_vs_pT with the ACTS procedure
(ROOT 'gaus', options SQ0, 3 iterations, refit range mean +- 3 sigma selected by bin centre,
min 10 entries) for different residual binnings.

Usage: python3 refit_binning.py <tracksummary_kf.root> <performance_kf.root>
"""
import sys
import numpy as np
import uproot, awkward as ak
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kFatal

t = uproot.open(sys.argv[1]); tr = t[t.keys()[0]]
a = tr.arrays(["t_pT", "res_eQOP_fit"])
pt = ak.flatten(a.t_pT).to_numpy(); res = ak.flatten(a.res_eQOP_fit).to_numpy()
ok = np.isfinite(res); pt, res = pt[ok], res[ok]
perf = uproot.open(sys.argv[2])["reswidth_qop_vs_pT"].values()

def fit(h, rng=None):
    r = h.Fit("gaus", "SQ0R" if rng else "SQ0", "", *(rng or (0, 0)))
    if r.Get() is None or r.Status() % 1000 != 0: return None
    return r.Parameter(1), r.Parameter(2)

def acts_fit(vals, nb, lo, hi):
    if len(vals) < 10: return None
    h = ROOT.TH1F("h", "", nb, lo, hi); h.SetDirectory(0)
    for v in vals: h.Fill(v)
    res = fit(h)
    for _ in range(2):
        if res is None: return None
        m, s = res
        # ACTS selects the range by bin centre: emulate with the edges of the selected bins
        res = fit(h, (m - 3 * abs(s), m + 3 * abs(s)))
    return res

binnings = [("100 bins, +-0.1 (as now, 0.002)", 100, -0.1, 0.1),
            ("1000 bins, +-0.1 (0.0002)", 1000, -0.1, 0.1),
            ("100 bins, +-0.01 (0.0002)", 100, -0.01, 0.01)]
edges = np.arange(0, 100.01, 2.5)
print("pT bin [GeV]   N    perf file  | " + " | ".join(b[0] for b in binnings))
nfail = {b[0]: 0 for b in binnings}
for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
    v = res[(pt >= lo) & (pt < hi)]
    row = []
    for name, nb, a_, b_ in binnings:
        r = acts_fit(v, nb, a_, b_)
        if r is None: nfail[name] += 1
        row.append("failed" if r is None else f"{abs(r[1]) * 1e3:.3f}")
    if i < 12 or i % 4 == 0:
        print(f"{lo:5.1f}-{hi:5.1f}  {len(v):4d}  {perf[i] * 1e3:8.3f}  | " + " | ".join(f"{x:>10s}" for x in row))
print("failed fits out of", len(edges) - 1, "pT bins:", nfail)
