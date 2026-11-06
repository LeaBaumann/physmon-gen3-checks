"""Point 2: plots from results/gen1_gsf_barrel_states.csv and the GSF track summaries
(same events in Gen1 and Gen3)."""
from pathlib import Path
import csv, uproot, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TOP = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(TOP / "results" / "gen1_gsf_barrel_states.csv")))
f = lambda k: np.array([float(r[k]) for r in rows])
o = f("outlier").astype(bool); z, r = np.abs(f("z")), f("r")
d = f("z_cross_outer_approach") - f("approach_halflength")

# same events: Gen1 outliers -> Gen3 measurements
D = {}
for g in ["gen1", "gen3"]:
    s = uproot.open(TOP / f"data/gsf_local/{g}/tracksummary_gsf.root")["tracksummary"].arrays(["event_nr", "nMeasurements", "nOutliers", "t_p"])
    D[g] = {e: (nm[0], no[0], p[0]) for e, nm, no, p in zip(s.event_nr.to_list(), s.nMeasurements.to_list(),
                                                          s.nOutliers.to_list(), s.t_p.to_list()) if len(nm) == 1}
c = sorted(set(D["gen1"]) & set(D["gen3"]))
ev = [e for e in c if D["gen1"][e][1] > 0]
print(f"events with exactly one track in both: {len(c)}; identical truth momentum: "
      f"{np.mean([np.isclose(D['gen1'][e][2], D['gen3'][e][2]) for e in c]) * 100:.1f} %; identical "
      f"measurements+outliers: {np.mean([sum(D['gen1'][e][:2]) == sum(D['gen3'][e][:2]) for e in c]) * 100:.1f} %")
print(f"events with Gen1 outliers: {len(ev)}: Gen1 outliers {sum(D['gen1'][e][1] for e in ev)}, Gen3 outliers "
      f"{sum(D['gen3'][e][1] for e in ev)}, extra Gen3 measurements {sum(D['gen3'][e][0] - D['gen1'][e][0] for e in ev)}")

fig, ax = plt.subplots(1, 3, figsize=(17, 4.6))
a = ax[0]
a.scatter(z[~o], r[~o], s=1, c="lightgray", label="regular measurements", rasterized=True)
a.scatter(z[o], r[o], s=3, c="C3", label="Gen1 GSF outliers")
for zend, rr in [(507.2, (30, 180)), (1139.0, (240, 700)), (1140.9, (800, 1060))]:
    a.vlines(zend, *rr, color="k", lw=0.8, ls=":")
a.set_xlabel("|z| [mm]"); a.set_ylabel("r [mm]"); a.set_title("Gen1 barrel hits (dotted: end of the modules)")
a.legend(fontsize=8, markerscale=4)
a = ax[1]
zmax = {}
for rw in rows:
    k = (rw["volume"], rw["layer"]); zmax[k] = max(zmax.get(k, 0), abs(float(rw["z"])))
frac = np.array([abs(float(rw["z"])) / zmax[(rw["volume"], rw["layer"])] for rw in rows])
bins = np.linspace(0, 1, 21)
a.hist(frac[~o], bins, density=True, histtype="step", color="gray", label="regular measurements")
a.hist(frac[o], bins, density=True, histtype="step", color="C3", lw=1.5, label="Gen1 GSF outliers")
a.set_xlabel("|z| / |z|max of the layer"); a.set_ylabel("density"); a.set_title("Outliers sit on the last module ring")
a.legend(fontsize=8)
a = ax[2]
bins = np.linspace(-150, 150, 61)
a.hist(np.clip(d[~o], -150, 150), bins, histtype="step", color="gray", label="regular measurements", log=True)
a.hist(np.clip(d[o], -150, 150), bins, histtype="step", color="C3", lw=1.5, label="Gen1 GSF outliers", log=True)
a.axvline(0, color="k", lw=0.8)
a.set_xlabel("|z| where the track crosses the outer approach cylinder\nminus its half-length [mm]")
a.set_title("> 0: crossing outside the approach cylinder"); a.legend(fontsize=8)
plt.tight_layout(); plt.savefig(TOP / "plots" / "2b_gen1_gsf_outliers_barrel_ends.png", dpi=120); plt.close()
