"""Track-by-track comparison of two 1muon CKF runs (same seed, one track per event).

Usage: python3 ckf_tracks_gen1_vs_gen3.py <gen1 tracksummary_ckf.root> <gen3 tracksummary_ckf.root>
Matches tracks by event number, checks that truth and number of measurements agree,
and prints the ratio Gen3/Gen1 of the fitted errors, overall and per |eta| and pT bin.
"""
import sys

import awkward as ak
import numpy as np
import uproot

ERR = ["err_eLOC0_fit", "err_eLOC1_fit", "err_ePHI_fit", "err_eTHETA_fit", "err_eQOP_fit"]
br = ["event_nr", "nMeasurements", "t_eta", "t_pT", "measurementVolume", "chi2Sum"] + ERR
d = []
for fn in sys.argv[1:3]:
    f = uproot.open(fn)
    a = f[f.keys()[0]].arrays(br)
    a = a[ak.num(a.nMeasurements) == 1]  # events with exactly one track
    d.append({k: (a[k][:, 0] if k == "measurementVolume" else
                  (a[k].to_numpy() if k == "event_nr" else ak.flatten(a[k]).to_numpy())) for k in br})
ev = np.intersect1d(d[0]["event_nr"], d[1]["event_nr"])


def sel(i, k):
    o = np.argsort(d[i]["event_nr"])
    return d[i][k][o[np.searchsorted(d[i]["event_nr"][o], ev)]]


print("matched single-track events:", len(ev))
e1, e3 = sel(0, "t_eta"), sel(1, "t_eta")
print("identical truth eta:", np.mean(abs(e1 - e3) < 1e-6))
n1, n3 = sel(0, "nMeasurements"), sel(1, "nMeasurements")
same = n1 == n3
print(f"nMeasurements equal: {same.mean():.3f}  Gen3 more: {np.mean(n3 > n1):.3f}  Gen3 fewer: {np.mean(n3 < n1):.3f}")
v1, v3 = sel(0, "measurementVolume"), sel(1, "measurementVolume")
for i in np.where((abs(e1) < 0.3) & same)[0][:2]:
    print(f"example eta {e1[i]:+.2f}: Gen1 volumes {list(map(int, v1[i]))}\n                Gen3 volumes {list(map(int, v3[i]))}")
print("\nmedian ratio Gen3/Gen1 (all / same nMeasurements):")
for k in ERR + ["chi2Sum"]:
    r = sel(1, k) / sel(0, k)
    print(f"  {k:15s} {np.nanmedian(r):.3f} / {np.nanmedian(r[same]):.3f}")
eta, pt = abs(e1), sel(0, "t_pT")
hdr = "  ".join(f"{k[4:-4]:>6s}" for k in ERR[:4])
print(f"\nmedian ratio Gen3/Gen1, same nMeasurements      {hdr}       N")
for name, x, bins in [("|eta|", eta, [(0, .5), (.5, 1), (1, 1.5), (1.5, 2), (2, 2.5), (2.5, 3)]),
                      ("pT [GeV]", pt, [(0.9, 2), (2, 4), (4, 7), (7, 11)])]:
    for lo, hi in bins:
        m = same & (x >= lo) & (x < hi)
        print(f"  {name:8s} {lo:4.1f}-{hi:4.1f}                     " +
              "  ".join(f"{np.nanmedian(sel(1, k)[m] / sel(0, k)[m]):6.3f}" for k in ERR[:4]) + f"  {m.sum():6d}")
