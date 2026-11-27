"""Overlay the physmon simulation histograms of the local variants.

Usage (from the root of this repository):
    python3 scripts/overlay_simulation.py fatras
    python3 scripts/overlay_simulation.py geant4

fatras: Gen1 / Gen3 with collector material / Gen3 without collector material
        (folders 0, 1, 2) -> plots/overlay_fatras.png
geant4: Gen1 / Gen3 with the Gen3 kill volume / Gen3 with a kill volume of the
        Gen1 extent (folders 0, 1, 3; Geant4 does not use the ACTS material
        map, so 1 = 2 and 3 differs from 1 only by the kill volume)
        -> plots/overlay_geant4.png. Geant4 does not fill total_x0, so the
        first panel shows the momentum p instead.

Reads `<folder>/particles_<sim>_hist.root` (made with generic_plotter.py and
CI/physmon/config/simulation.yml). Each panel shows the histogram with
under-/overflow added to the first/last bin, and below it the ratio to Gen1.
The legend gives the number of particles of each variant. Also prints the
entries per variant and histogram as a table.
Needs uproot, numpy, matplotlib.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot

SIM = sys.argv[1]
assert SIM in ("fatras", "geant4"), "argument must be fatras or geant4"

# fixed categorical order (blue, orange, aqua), plus line style and marker as
# secondary encoding, so the curves stay apart where they lie on top of each other
STYLE = [
    dict(color="#257de0", ls="-", marker=None),
    dict(color="#f47230", ls="--", marker=None),
    dict(color="#00b894", ls=":", marker="o"),
]
if SIM == "fatras":
    VARIANTS = [
        ("0_gen1_local", "Gen1"),
        ("1_gen3_as_in_ci", "Gen3, with collector material (as in CI)"),
        ("2_gen3_no_collector_material", "Gen3, collector bins set to vacuum"),
    ]
else:
    VARIANTS = [
        ("0_gen1_local", "Gen1"),
        ("1_gen3_as_in_ci", "Gen3, Gen3 kill volume (r ≤ 1245 mm, as in CI)"),
        (
            "3_gen3_no_collector_material_gen1_kill_volume",
            "Gen3, kill volume with Gen1 extent (r ≤ 1202 mm)",
        ),
    ]
HISTS = [
    ("total_x0", "total material traversed [X0]", True),
    ("number_of_hits", "number of hits", True),
    ("eta", "η", False),
    ("e_loss", "energy loss [GeV]", True),
]
if SIM == "geant4":
    # Geant4 does not fill total_x0 (always 0), show the momentum instead
    HISTS[0] = ("p", "momentum [GeV]", True)

TEXT = "#1f1f1f"
TEXT2 = "#6b6b6b"
GRID = "#e6e6e6"


def load(folder, name):
    h = uproot.open(Path(folder) / f"particles_{SIM}_hist.root")[name]
    v = h.values(flow=True).astype(float)
    # fold under-/overflow into the first/last visible bin
    v[1] += v[0]
    v[-2] += v[-1]
    return h.axis().edges(), v[1:-1]


plt.rcParams.update(
    {
        "font.size": 9,
        "axes.edgecolor": TEXT2,
        "axes.labelcolor": TEXT,
        "xtick.color": TEXT2,
        "ytick.color": TEXT2,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)
fig = plt.figure(figsize=(11, 7.2), facecolor="white")
gs = fig.add_gridspec(2, len(HISTS), height_ratios=[3, 1.2], hspace=0.08, wspace=0.32)

counts = {}
for col, (name, xlabel, logy) in enumerate(HISTS):
    ax = fig.add_subplot(gs[0, col])
    rax = fig.add_subplot(gs[1, col], sharex=ax)
    ref = None
    for (folder, label), st in zip(VARIANTS, STYLE):
        edges, v = load(folder, name)
        counts.setdefault(folder, {})[name] = v.sum()
        ax.stairs(v, edges, color=st["color"], ls=st["ls"], lw=2, label=label)
        centres = 0.5 * (edges[1:] + edges[:-1])
        if ref is None:
            ref = v
            rax.axhline(1.0, color=st["color"], lw=2)
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(ref > 0, v / ref, np.nan)
        rax.step(centres, r, where="mid", color=st["color"], ls=st["ls"], lw=2)
        if st["marker"]:
            rax.plot(centres, r, st["marker"], color=st["color"], ms=3)
    if logy:
        ax.set_yscale("log")
    ax.set_title(name, color=TEXT, fontsize=10, loc="left")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.tick_params(labelbottom=False)
    rax.set_ylim(0, 3)
    rax.grid(axis="y", color=GRID, lw=0.8)
    rax.set_xlabel(xlabel)
    if col == 0:
        ax.set_ylabel("particles per bin")
        rax.set_ylabel("ratio to Gen1")

nPart = {f: c["eta"] for f, c in counts.items()}
handles, labels = fig.axes[0].get_legend_handles_labels()
labels = [f"{l}: {nPart[f]:.0f} particles" for (f, _), l in zip(VARIANTS, labels)]
fig.legend(handles, labels, loc="upper center", ncol=1, frameon=False,
           bbox_to_anchor=(0.5, 1.0), labelcolor=TEXT)
fig.suptitle(
    f"physmon_simulation.py, {'Fatras' if SIM == 'fatras' else 'Geant4'}: "
    "particle gun (μ, π, e per event), 1000 events, seed 42",
    y=0.86, color=TEXT2, fontsize=9,
)
fig.subplots_adjust(top=0.80, bottom=0.08, left=0.07, right=0.99)
out = Path("plots") / f"overlay_{SIM}.png"
out.parent.mkdir(exist_ok=True)
fig.savefig(out, dpi=130)

print(f"{SIM}: entries per histogram (under-/overflow included)")
print(f"{'variant':48s}" + "".join(f"{n:>16s}" for n, _, _ in HISTS))
for folder, _ in VARIANTS:
    print(f"{folder:48s}" + "".join(f"{counts[folder][n]:16.0f}" for n, _, _ in HISTS))
print("wrote", out)
