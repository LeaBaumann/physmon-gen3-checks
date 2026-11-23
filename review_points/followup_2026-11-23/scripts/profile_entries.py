"""Value, spread and number of entries per bin of a TProfile, Gen1 vs Gen3.

Usage: python3 profile_entries.py <reference.root> <monitored.root> <profile name> [<|eta| min>]
e.g. performance_finding_ckf_ml_solver.root nStates_vs_eta
"""
import sys

import uproot

a, b = uproot.open(sys.argv[1])[sys.argv[3]], uproot.open(sys.argv[2])[sys.argv[3]]
etamin = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
ea, eb = a.member("fBinEntries")[1:-1], b.member("fBinEntries")[1:-1]
for x, p, q, na, nb, sa, sb in zip(a.axis().centers(), a.values(), b.values(), ea, eb,
                                   a.errors(error_mode="s"), b.errors(error_mode="s")):
    if abs(x) >= etamin and (na or nb):
        print(f"{x:+.1f}  Gen1 {p:7.3f} ± {sa:5.2f} (N={na:5.0f})   Gen3 {q:7.3f} ± {sb:5.2f} (N={nb:5.0f})")
