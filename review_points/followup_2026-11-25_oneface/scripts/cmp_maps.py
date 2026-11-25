"""Compare two Gen3 material maps (.json.zst) surface by surface: binning, empty bins, mean t/X0.

Usage: python3 cmp_maps.py <map 1> <map 2>
"""
import json, subprocess, sys
import numpy as np
def load(p):
    d = json.loads(subprocess.run(["zstd", "-dc", p], capture_output=True).stdout)
    out = {}
    for s in d["surfaces"]:
        m = s["material"]
        bins = tuple(a["bins"] for a in m.get("binning", {}).get("axes", []))
        tx = []
        for v in m.get("values", []):
            mat = v["material"]
            x0 = mat.get("radiation_length")
            tx.append(v["thickness"] / x0 if mat.get("kind") != "vacuum" and x0 else 0.0)
        out[s["target"]["key"]] = (bins, np.array(tx))
    return out
a, b = load(sys.argv[1]), load(sys.argv[2])
print("surfaces:", len(a), len(b), "only in first:", sorted(set(a) - set(b))[:5], "only in second:", sorted(set(b) - set(a))[:5])
rows = []
for k in sorted(set(a) & set(b)):
    (ba, ta), (bb, tb) = a[k], b[k]
    if ba != bb:
        print("binning differs:", k, ba, bb); continue
    if len(ta) == 0: continue
    rows.append((k, ta.mean(), tb.mean(), (ta == 0).mean(), (tb == 0).mean()))
print(f"{'surface':48s} {'<t/X0> 1':>9s} {'<t/X0> 2':>9s} {'ratio':>6s} {'empty1':>6s} {'empty2':>6s}")
for k, x, y, e1, e2 in rows:
    if x > 1e-4 or y > 1e-4:
        print(f"{k:48s} {x:9.5f} {y:9.5f} {y/x if x else float('nan'):6.2f} {e1:6.2f} {e2:6.2f}")
