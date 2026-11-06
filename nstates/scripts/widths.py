"""Width of residual/pull distributions, Gen3 vs. Gen1 (local runs, same seed)."""
from pathlib import Path
import uproot, numpy as np

D = Path(__file__).resolve().parent.parent / "data" / "axis59p5"
for alg in ["kf", "gx2f", "gsf"]:
    F1 = uproot.open(D / f"gen1/trackfitting_{alg}/performance_trackfitting.root")
    F3 = uproot.open(D / f"gen3/trackfitting_{alg}/performance_trackfitting.root")
    print(f"===== {alg.upper()}: standard deviation of 1D residual/pull histograms, Gen1 -> Gen3")
    rows = []
    for k, cl in F1.classnames().items():
        if not cl.startswith("TH1") or not (k.startswith("res_") or k.startswith("pull_")):
            continue
        x = F1[k].axes[0].centers(); v1, v3 = F1[k].values(), F3[k].values()
        if v1.sum() < 50 or v3.sum() < 50:
            continue
        sd = lambda v: np.sqrt(((x - (x * v).sum() / v.sum()) ** 2 * v).sum() / v.sum())
        rows.append((sd(v3) / sd(v1) - 1, k.split(";")[0], sd(v1), sd(v3)))
    for r in sorted(rows, reverse=True):
        print(f"  {r[1]:16s} {r[2]:.4g} -> {r[3]:.4g}  ({r[0] * 100:+5.1f} %)")
    print(f"  ratio of fitted widths Gen3/Gen1 per |eta| range (reswidth_*/pullwidth_*_vs_eta; 0/nan/inf = empty bins)")
    names = ["reswidth_d0", "reswidth_z0", "reswidth_phi", "reswidth_theta", "reswidth_qop", "pullwidth_d0", "pullwidth_phi"]
    print("              " + " ".join(f"{n.replace('width_', '_'):>9}" for n in names))
    for lo, hi in [(0, 0.5), (0.5, 1), (1, 1.5), (1.5, 2), (2, 2.5), (2.5, 3)]:
        out = []
        for n in names:
            h1, h3 = F1[n + "_vs_eta"], F3[n + "_vs_eta"]
            m = (np.abs(h1.axes[0].centers()) >= lo) & (np.abs(h1.axes[0].centers()) < hi)
            with np.errstate(all="ignore"):
                out.append(f"{np.mean(h3.values()[m]) / np.mean(h1.values()[m]):9.3f}")
        print(f"  |eta| {lo:.1f}-{hi:.1f} " + " ".join(out))
