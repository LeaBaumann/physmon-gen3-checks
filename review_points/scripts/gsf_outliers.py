"""Point 2: where the Gen1 GSF outliers are and why.
Input: trackstates_gsf.root of the Gen1 GSF run (run_gsf_with_states.py; 138 MB,
not stored here), path as first argument.
Output: results/gen1_gsf_barrel_states.csv (all measurement/outlier states on Gen1
barrel layers) and a summary on stdout."""
import sys, csv
from pathlib import Path
import uproot, numpy as np, awkward as ak

TOP = Path(__file__).resolve().parent.parent
# Gen1 outer approach cylinder (approach2) per barrel layer: radius, halfLengthZ [mm],
# from gen1_approach.py (results/gen1_barrel_approach_geometry.txt)
APP = {(17, 2): (39.4, 512.2), (17, 4): (74.8, 512.2), (17, 6): (120.6, 512.2), (17, 8): (176.5, 512.2),
       (24, 2): (289.7, 1149.0), (24, 4): (389.5, 1149.0), (24, 6): (529.2, 1149.0), (24, 8): (689.1, 1149.0),
       (29, 2): (856.9, 1150.9), (29, 4): (1056.6, 1150.9)}
NAME = {17: "Pixel barrel", 24: "ShortStrip barrel", 29: "LongStrip barrel"}

st = uproot.open(sys.argv[1])["trackstates"].arrays(
    ["stateType", "volume_id", "layer_id", "g_x_prt", "g_y_prt", "g_z_prt", "px_prt", "py_prt", "pz_prt"])
rows = []
for tr in range(len(st)):
    s = st[tr]
    t, v, l = s.stateType.to_list(), s.volume_id.to_list(), s.layer_id.to_list()
    meas = [i for i, ti in enumerate(t) if ti in (0, 1)]          # index 0 = outermost state
    for i in meas:
        if (v[i], l[i]) not in APP:
            continue
        x, y, z, px, py, pz = (float(s[k][i]) for k in ["g_x_prt", "g_y_prt", "g_z_prt", "px_prt", "py_prt", "pz_prt"])
        r, pt = np.hypot(x, y), np.hypot(px, py)
        rapp, hl = APP[(v[i], l[i])]
        # straight line in r-z from the hit to the outer approach radius
        zc = abs(z) + abs(pz / pt) * (rapp - r) * (1 if np.sign(z) == np.sign(pz) else -1)
        outer = [j for j in meas if j < i]
        rows.append(dict(track=tr, outlier=int(t[i] == 1), volume=v[i], layer=l[i], z=round(z, 2), r=round(r, 2),
                         eta=round(float(np.arcsinh(pz / pt)), 4), z_cross_outer_approach=round(zc, 2),
                         approach_halflength=hl, last_hit_in_this_barrel=int(not any(v[j] == v[i] for j in outer)),
                         next_outer_volume=v[outer[-1]] if outer else -1))
out = TOP / "results" / "gen1_gsf_barrel_states.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

o = np.array([r["outlier"] for r in rows], bool)
miss = np.array([r["z_cross_outer_approach"] > r["approach_halflength"] for r in rows])
zmax = {}
for r in rows:
    k = (r["volume"], r["layer"]); zmax[k] = max(zmax.get(k, 0), abs(r["z"]))
frac = np.array([abs(r["z"]) / zmax[(r["volume"], r["layer"])] for r in rows])
last = np.array([r["last_hit_in_this_barrel"] for r in rows], bool)
endcap = np.array([r["next_outer_volume"] not in (-1, 17, 24, 29) for r in rows])
print(f"barrel measurement/outlier states: {len(rows)}, outliers: {o.sum()}")
print("outliers per layer:")
for k in sorted(APP, key=lambda k: -np.sum(o & np.array([(r['volume'], r['layer']) == k for r in rows]))):
    n = np.sum(o & np.array([(r["volume"], r["layer"]) == k for r in rows]))
    print(f"   {NAME[k[0]]} layer {k[1]}: {n}")
print(f"outliers in the last 10 % of the layer length (|z| > 0.9 |z|max): {np.mean(frac[o] > 0.9) * 100:.1f} %")
print(f"outliers that are the last hit of the track in this barrel:        {np.mean(last[o]) * 100:.1f} %")
print(f"outliers whose next measurement further out is in an endcap:       {np.mean(endcap[o]) * 100:.1f} %")
print(f"track crosses the outer approach cylinder outside its z-range: outliers {np.mean(miss[o]) * 100:.1f} %, "
      f"regular measurements {np.mean(miss[~o]) * 100:.1f} %")
print(f"of all states with the crossing outside the range, flagged as outlier: {np.mean(o[miss]) * 100:.1f} %")
