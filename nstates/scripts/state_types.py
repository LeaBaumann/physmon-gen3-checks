"""Count track-state types per track (KF, 1000 events) for Gen1 and Gen3,
locate the material states along |z|, and compare the fit quality.
Input: data/kf_1000ev/{gen1,gen3}/ (output of run_kf_with_states.py)."""
from pathlib import Path
import uproot, numpy as np, awkward as ak

BASE = Path(__file__).resolve().parent.parent / "data" / "kf_1000ev"
# stateType: 0 measurement, 1 outlier, 2 hole, 3 material, 4 unknown
# (RootTrackStatesWriter::StateType)

print("1) Mean number of states per track by |eta_truth|:")
print("   nStates / nMeasurements / nOutliers / nHoles / nMaterial ; fraction with nStates >= 30")
bins = [0, 0.5, 1, 1.5, 2, 2.5, 3]
for g in ["gen1", "gen3"]:
    s = uproot.open(BASE / g / "tracksummary_kf.root")["tracksummary"].arrays(
        ["nStates", "nMeasurements", "nOutliers", "nHoles", "t_eta"])
    st = uproot.open(BASE / g / "trackstates_kf.root")["trackstates"].arrays(["stateType"])
    f = lambda k: ak.flatten(s[k]).to_numpy()
    ns, nm, no, nh, eta = f("nStates"), f("nMeasurements"), f("nOutliers"), f("nHoles"), np.abs(f("t_eta"))
    nmat = ak.sum(st.stateType == 3, axis=1).to_numpy()
    print(f" {g}: {len(ns)} tracks, unknown states: {int(ak.sum(st.stateType == 4))}")
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (eta >= lo) & (eta < hi)
        print(f"   |eta| {lo}-{hi}: {ns[m].mean():5.2f} / {nm[m].mean():5.2f} / {no[m].mean():4.2f} / "
              f"{nh[m].mean():4.2f} / {nmat[m].mean():5.2f} ; >=30: {np.mean(ns[m] >= 30) * 100:5.1f} %  (n={m.sum()})")
    print(f"   all:        {ns.mean():5.2f} / {nm.mean():5.2f} / {no.mean():4.2f} / {nh.mean():4.2f} / "
          f"{nmat.mean():5.2f} ; >=30: {np.mean(ns >= 30) * 100:5.1f} %  (max {ns.max()})")

print("\n2) Position of the states along |z| for tracks with 2.0 < |eta| < 2.5")
print("   (10 mm bins, states per track, only entries > 0.05 shown)")
for g in ["gen1", "gen3"]:
    st = uproot.open(BASE / g / "trackstates_kf.root")["trackstates"].arrays(["stateType", "g_z_smt", "eta_smt"])
    eta = np.abs(ak.mean(st.eta_smt, axis=1).to_numpy())
    s = st[(eta > 2.0) & (eta < 2.5)]
    nt = len(s)
    t = ak.flatten(s.stateType).to_numpy()
    z = np.abs(ak.flatten(s.g_z_smt).to_numpy())
    print(f" {g}: {nt} tracks")
    for name, m in [("material", t == 3), ("measurement", t == 0)]:
        u, c = np.unique(np.round(z[m] / 10) * 10, return_counts=True)
        print(f"   {name}: " + "  ".join(f"{int(a)}:{b / nt:.2f}" for a, b in zip(u, c) if b / nt > 0.05))

print("\n3) Fit quality (robust width = 1.4826 * MAD)")
rob = lambda x: 1.4826 * np.median(np.abs(x - np.median(x)))
for g in ["gen1", "gen3"]:
    s = uproot.open(BASE / g / "tracksummary_kf.root")["tracksummary"].arrays()
    f = lambda k: ak.flatten(s[k]).to_numpy()
    eta = np.abs(f("t_eta")); chi = f("chi2Sum") / f("NDF")
    for lo, hi in [(0, 1), (1.5, 3)]:
        m = (eta >= lo) & (eta < hi) & f("hasFittedParams").astype(bool)
        print(f" {g} |eta| {lo}-{hi}: pull q/p {rob(f('pull_eQOP_fit')[m]):.3f} | pull d0 {rob(f('pull_eLOC0_fit')[m]):.3f}"
              f" | res q/p {rob(f('res_eQOP_fit')[m]):.2e} | chi2/ndf {np.mean(chi[m]):.3f}")
