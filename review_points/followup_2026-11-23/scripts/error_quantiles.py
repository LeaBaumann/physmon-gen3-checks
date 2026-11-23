"""Quantiles (interpolated within bins, incl. overflow) of the err_* histograms, Gen1 vs Gen3,
plus the number of tracks per quarter of the axis.

Usage: python3 error_quantiles.py <reference (Gen1) tracksummary_ckf_hist.root> <monitored (Gen3) ...root>
"""
import sys

import numpy as np
import uproot

A, B = uproot.open(sys.argv[1]), uproot.open(sys.argv[2])


def q(h, p):
    v = h.values(flow=True)
    e = h.axis().edges()
    c = np.concatenate([[v[0]], v[0] + np.cumsum(v[1:-1])]) / v.sum()
    return np.nan if p > c[-1] else np.interp(p, c, e)


for k in ["err_eLOC0_fit", "err_eLOC1_fit", "err_ePHI_fit", "err_eTHETA_fit", "err_eQOP_fit"]:
    qs = "  ".join(f"q{int(p * 100)} {q(A[k], p):.3g}->{q(B[k], p):.3g} ({q(B[k], p) / q(A[k], p):.3f})"
                   for p in [0.25, 0.5, 0.75])
    va, vb = A[k].values(flow=True), B[k].values(flow=True)
    n = (len(va) - 2) // 4
    quarters = " ".join(f"{va[1 + i * n:1 + (i + 1) * n].sum():.0f}/{vb[1 + i * n:1 + (i + 1) * n].sum():.0f}"
                        for i in range(4))
    print(f"{k:15s} {qs}\n{'':15s} tracks per axis quarter Gen1/Gen3: {quarters}, overflow {va[-1]:.0f}/{vb[-1]:.0f}")
