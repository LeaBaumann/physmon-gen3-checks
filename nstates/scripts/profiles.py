"""nStates_vs_eta profiles: Gen1 CI reference (axis up to 29.5) vs. local Gen1 and
Gen3 runs with the axis widened to 59.5. Prints a table and writes the plot."""
from pathlib import Path
import uproot, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TOP = Path(__file__).resolve().parent.parent
FILES = {
    "Gen1, CI reference (axis up to 29.5)": ("reference/trackfitting_{a}_performance_trackfitting.root", "k--"),
    "Gen1, local (axis up to 59.5)": ("data/axis59p5/gen1/trackfitting_{a}/performance_trackfitting.root", "C0-"),
    "Gen3, local (axis up to 59.5)": ("data/axis59p5/gen3/trackfitting_{a}/performance_trackfitting.root", "C1-"),
}

def prof(path):
    h = uproot.open(path)["nStates_vs_eta"]
    e = h.axes[0].edges()
    return e, h.values(), h.errors(), np.asarray(h.member("fBinEntries"))[1:-1]

fig, ax = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
for a, alg in zip(ax, ["kf", "gx2f", "gsf"]):
    R = {k: prof(TOP / p.format(a=alg)) for k, (p, _) in FILES.items()}
    print(f"===== {alg.upper()}  nStates_vs_eta: mean (entries)")
    print(f'{"eta":>10} ' + " ".join(f"{k[:20]:>22}" for k in R))
    e = R["Gen1, local (axis up to 59.5)"][0]
    for i in range(len(e) - 1):
        if 0 <= 0.5 * (e[i] + e[i + 1]) <= 3.0:
            print(f"{e[i]:4.1f}-{e[i + 1]:4.1f} " + " ".join(f"{R[k][1][i]:11.2f} ({int(R[k][3][i]):6d})" for k in R))
    for k in R:
        print(f"  {k}: total entries {int(R[k][3].sum())}")
    for k, (_, style) in FILES.items():
        e, v, er, _ = R[k]; x = 0.5 * (e[1:] + e[:-1]); m = v > 0
        a.errorbar(x[m], v[m], yerr=er[m], fmt=style, drawstyle="steps-mid", label=k, lw=1.5)
    a.axhline(29.5, color="gray", lw=0.8, ls=":")
    a.text(-3.9, 29.8, "old axis limit 29.5", color="gray", fontsize=8)
    a.set_title(f"{alg.upper()}: number of track states vs. $\\eta$")
    a.set_xlabel("reco $\\eta$"); a.set_xlim(-4, 4); a.grid(alpha=0.3)
ax[0].set_ylabel("mean number of states"); ax[0].legend(fontsize=8, loc="lower center")
plt.tight_layout(); plt.savefig(TOP / "nStates_vs_eta_axis59p5.png", dpi=130)
