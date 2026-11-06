"""Points 1, 2a, 3, 4: CI Gen3 (gen3-default @ dd259a4dc) vs. Gen1 CI reference.
Prints tables and writes plots/1_*.png, plots/2a_*.png, plots/3_*.png, plots/4_*.png."""
from pathlib import Path
import uproot, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TOP = Path(__file__).resolve().parent.parent
REF, G3, OUT = TOP / "reference", TOP / "data" / "ci_gen3", TOP / "plots"
L1, L3 = "Gen1 (CI reference)", "Gen3 (CI, dd259a4dc)"
open_ = lambda base, f: uproot.open(base / f)

def prof(h):
    return h.axes[0].centers(), h.values(), h.errors(), np.asarray(h.member("fBinEntries"))[1:-1]

# ---- 1: resolution widths from per-bin Gaussian fits ----
print("1) reswidth_* histograms: value per eta bin (0 = per-bin Gaussian fit failed)")
fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
for a, (wf, hn) in zip(ax, [("trackfitting_kf", "reswidth_qopt_vs_eta"), ("trackfitting_gx2f", "reswidth_qopt_vs_eta"),
                            ("trackfitting_kf", "reswidth_theta_vs_eta")]):
    hr = open_(REF, f"{wf}/performance_trackfitting.root")[hn]; hc = open_(G3, f"{wf}/performance_trackfitting.root")[hn]
    x, vr, vc = hr.axes[0].centers(), hr.values(), hc.values()
    both = (vr > 0) & (vc > 0)
    print(f"  {wf} {hn}: bins with a value: Gen1 {np.sum(vr > 0)}, Gen3 {np.sum(vc > 0)}, both {both.sum()}, "
          f"exactly one {np.sum((vr > 0) ^ (vc > 0))}; ratio Gen3/Gen1 where both: "
          f"{np.min(vc[both] / vr[both]):.3f}-{np.max(vc[both] / vr[both]):.3f}")
    a.plot(x, vr, "ks", mfc="none", label=L1); a.plot(x, vc, "C1o", ms=4, label=L3)
    a.set_title(f"{wf.split('_')[1].upper()}: {hn}", fontsize=10); a.set_xlabel("$\\eta$"); a.grid(alpha=0.3)
ax[0].set_ylabel("fitted width (0 = fit failed)"); ax[0].legend(fontsize=8)
fig.suptitle("Point 1: 'distributions get wider' = bins switching between fitted and failed width fits")
plt.tight_layout(); plt.savefig(OUT / "1_reswidth_fit_failures.png", dpi=120); plt.close()

# ---- 2a: GSF outliers / measurements vs eta ----
print("\n2a) GSF: mean per track by |eta| (0-0.5, ..., 2.5-3)")
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
for a, hn in zip(ax, ["nOutliers_vs_eta", "nMeasurements_vs_eta"]):
    for base, lab, st in [(REF, L1, "k--"), (G3, L3, "C1-")]:
        x, v, e, n = prof(open_(base, "trackfitting_gsf/performance_trackfitting.root")[hn]); m = n > 0
        a.errorbar(x[m], v[m], yerr=e[m], fmt=st, drawstyle="steps-mid", label=lab)
        out = []
        for lo, hi in [(0, .5), (.5, 1), (1, 1.5), (1.5, 2), (2, 2.5), (2.5, 3)]:
            s = (np.abs(x) >= lo) & (np.abs(x) < hi); out.append(f"{(v[s] * n[s]).sum() / n[s].sum():.3f}")
        print(f"  {hn:22s} {lab:22s} " + " ".join(out) + f"   all {(v * n).sum() / n.sum():.3f}")
    a.set_title(f"GSF: {hn}"); a.set_xlabel("$\\eta$"); a.grid(alpha=0.3); a.legend(fontsize=8)
plt.tight_layout(); plt.savefig(OUT / "2a_gsf_outliers_measurements_vs_eta.png", dpi=120); plt.close()

# ---- 3: ttbar track errors and pulls ----
print("\n3) ttbar CKF track summary: entries, mean, std")
names = ["err_eTHETA_fit", "err_eLOC0_fit", "err_ePHI_fit", "pull_eTHETA_fit", "pull_eLOC0_fit", "pull_ePHI_fit"]
fig, ax = plt.subplots(2, 3, figsize=(15, 7.5))
for a, hn in zip(ax.flat, names):
    for base, lab, st in [(REF, L1, "k"), (G3, L3, "C1")]:
        h = open_(base, "trackfinding_ttbar_pu200/tracksummary_ckf_hist.root")[hn]
        x, v = h.axes[0].centers(), h.values(); mu = (x * v).sum() / v.sum(); sd = np.sqrt(((x - mu) ** 2 * v).sum() / v.sum())
        print(f"  {hn:16s} {lab:22s} N {v.sum():7.0f}  mean {mu:.4g}  std {sd:.4g}")
        a.step(h.axes[0].edges()[:-1], v / v.sum(), where="post", color=st, label=f"{lab}: mean {mu:.3g}")
    a.set_title(hn); a.legend(fontsize=7); a.grid(alpha=0.3)
fig.suptitle("Point 3: ttbar CKF tracks: errors change, pulls do not (normalised)")
plt.tight_layout(); plt.savefig(OUT / "3_ttbar_errors_pulls.png", dpi=120); plt.close()

# ---- 4: ttbar purity ----
print("\n4) ttbar purity / outliers vs |eta|: value (entries)")
fig, ax = plt.subplots(1, 3, figsize=(16, 4.2))
for a, (f, hn) in zip(ax, [("performance_finding_ckf_ml_solver", "purity_vs_eta"),
                           ("performance_finding_ckf_ml_solver", "nOutliers_vs_eta"),
                           ("performance_finding_ckf", "purity_vs_eta")]):
    print(f"  {f} {hn}")
    for base, lab, st in [(REF, L1, "k--"), (G3, L3, "C1-")]:
        x, v, e, n = prof(open_(base, f"trackfinding_ttbar_pu200/{f}.root")[hn]); m = n > 0
        a.errorbar(x[m], v[m], yerr=e[m], fmt=st, drawstyle="steps-mid", label=lab)
        print(f"    {lab:22s} " + " ".join(f"{abs(xi):.1f}:{vi:.3f}({int(ni)})" for xi, vi, ni in zip(x, v, n) if xi > 0 and ni > 0))
        if f.endswith("ml_solver"):
            for xi, vi, ni in zip(x, v, n):
                if abs(xi) > 3 and ni > 0:
                    a.annotate(f"{int(ni)}", (xi, vi), fontsize=7, color="k" if st.startswith("k") else "C1")
    a.set_title(f"{f.replace('performance_finding_', '')}: {hn}", fontsize=10); a.set_xlabel("$\\eta$")
    a.grid(alpha=0.3); a.legend(fontsize=8)
fig.suptitle("Point 4: ttbar purity: changes only in the last bins (|eta| > 3, numbers = tracks per bin)")
plt.tight_layout(); plt.savefig(OUT / "4_ttbar_purity.png", dpi=120); plt.close()
