"""Redo the per-bin Gaussian fits behind reswidth_<par>_vs_{eta,pT} with the ACTS procedure
(ROOT 'gaus', options SQ0, 3 iterations, refit range mean +- 3 sigma, min 10 entries),
once with the physmon residual binning (100 bins) and once 10x finer (1000 bins, same range).

Usage: python3 refit_binning_all.py <tracksummary.root> <performance.root>

The coarse result is compared bin by bin with reswidth_* in the performance file
(check that this reproduction matches ACTS). Binning in truth eta / truth pT as in ResPlotTool.
"""
import sys

import awkward as ak
import numpy as np
import ROOT
import uproot

ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kFatal

t = uproot.open(sys.argv[1])
tr = t[t.keys()[0]]
perf = uproot.open(sys.argv[2])
need = ["t_eta", "t_pT", "t_charge", "res_eLOC0_fit", "res_eLOC1_fit", "res_ePHI_fit",
        "res_eTHETA_fit", "res_eQOP_fit", "eQOP_fit", "eTHETA_fit"]
a = tr.arrays([b for b in need if b in tr.keys()])
F = {k: ak.flatten(a[k]).to_numpy().astype(float) for k in a.fields}
res = {"d0": F["res_eLOC0_fit"], "z0": F["res_eLOC1_fit"], "phi": F["res_ePHI_fit"],
       "theta": F["res_eTHETA_fit"], "qop": F["res_eQOP_fit"]}
if "eQOP_fit" in F:
    res["qopt"] = F["eQOP_fit"] / np.sin(F["eTHETA_fit"]) - F["t_charge"] / F["t_pT"]
RANGE = {"d0": 0.5, "z0": 0.5, "phi": 0.01, "theta": 0.01, "qop": 0.1, "qopt": 0.1}
AX = {"eta": ("t_eta", np.linspace(-4, 4, 41)), "pT": ("t_pT", np.linspace(0, 100, 41))}


def fit(h, rng=None):
    r = h.Fit("gaus", "SQ0R" if rng else "SQ0", "", *(rng or (0, 0)))
    try:
        if r.Status() % 1000 != 0:
            return None
    except ReferenceError:  # no fit result at all
        return None
    return r.Parameter(1), abs(r.Parameter(2))


def acts_fit(vals, nb, lim):
    if len(vals) < 10:
        return None
    h = ROOT.TH1F("h", "", nb, -lim, lim)
    h.SetDirectory(0)
    for v in vals:
        h.Fill(v)
    r = fit(h)
    for _ in range(2):
        if r is None:
            return None
        r = fit(h, (r[0] - 3 * r[1], r[0] + 3 * r[1]))
    return r


print(f"{'plot':24s} {'bins w/ tracks':>14s} {'reproduced':>10s} {'fail coarse':>11s} {'fail fine':>9s}  median width fine/coarse")
for p, r_all in res.items():
    for ax, (var, edges) in AX.items():
        name = f"reswidth_{p}_vs_{ax}"
        ref = perf[name].values() if name in perf else None
        x = F[var]
        nfill = nrep = fc = ff = 0
        ratios = []
        for i in range(len(edges) - 1):
            v = r_all[(x >= edges[i]) & (x < edges[i + 1]) & np.isfinite(r_all)]
            if len(v) < 10:
                continue
            nfill += 1
            c = acts_fit(v, 100, RANGE[p])
            f = acts_fit(v, 1000, RANGE[p])
            fc += c is None
            ff += f is None
            if ref is not None and abs((c[1] if c else 0.0) - ref[i]) <= 1e-3 * max(ref[i], 1e-12) + 1e-9:
                nrep += 1
            if c and f:
                ratios.append(f[1] / c[1])
        med = f"{np.median(ratios):.2f}" if ratios else "-"
        print(f"{name:24s} {nfill:14d} {nrep:6d}/{nfill:<3d} {fc:11d} {ff:9d}  {med}")
