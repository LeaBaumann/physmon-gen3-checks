"""Entries, mean and RMS of all 1D histograms in two histogram files.

Usage: python3 hist_stats.py <reference (Gen1).root> <monitored (Gen3).root>
Used for the 1muon CKF tracksummary_ckf_hist.root comparison.
"""
import uproot,numpy as np,sys
ref,mon=sys.argv[1],sys.argv[2]
a=uproot.open(ref); b=uproot.open(mon)
def st(h):
    v=h.values(); x=h.axis().centers(); n=v.sum()
    if n==0: return 0,0,0
    m=(v*x).sum()/n; s=np.sqrt((v*(x-m)**2).sum()/n); return n,m,s
print(f"{'hist':22s} {'N1':>7s} {'N3':>7s} {'mean1':>10s} {'mean3':>10s} {'rms1':>10s} {'rms3':>10s} rms3/rms1")
for k in sorted(set(k.split(';')[0] for k in a.keys())):
    if a[k].classname.startswith("TH1"):
        n1,m1,s1=st(a[k]); n3,m3,s3=st(b[k])
        r=s3/s1 if s1 else float('nan')
        print(f"{k:22s} {n1:7.0f} {n3:7.0f} {m1:10.4g} {m3:10.4g} {s1:10.4g} {s3:10.4g} {r:6.3f}")
