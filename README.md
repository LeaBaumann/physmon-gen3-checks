# Physmon simulation: Gen3 vs. Gen1 (Fatras and Geant4)

Local runs of `CI/physmon/workflows/physmon_simulation.py` (particle gun:
one muon, pion and electron per event, 1000 events, seed 42) on
`gen3-default` (`dd259a4dc`), 2026-11-06. Histograms were made with
`Examples/Scripts/generic_plotter.py` and `CI/physmon/config/simulation.yml`,
reports with `histcmp==0.12.0` and `CI/physmon/config/standard.toml`, the
same tools and settings as the physmon CI job.

`reference/` holds the Gen1 reference histograms used by the CI (sha256
`acf50e81…` for Fatras, `7ff5f21c…` for Geant4, fetched from the physmon
reference registry).

| Folder | Geometry | Material map | Geant4 kill volume | Fatras failed | Geant4 failed |
|---|---|---|---|---|---|
| `0_gen1_local` | Gen1 | official Gen1 ODD map | Gen1 `highestTrackingVolume` (r ≤ 1202 mm, \|z\| ≤ 4002 mm) | 0/20 | 0/20 |
| `1_gen3_as_in_ci` | Gen3 | provisional Gen3 map (release v1, with calorimeter collector) | Gen3 `highestTrackingVolume` (r ≤ 1245 mm, \|z\| ≤ 4020 mm) | 19/20 | 20/20 |
| `2_gen3_no_collector_material` | Gen3 | same map, collector bins set to vacuum | Gen3 | 12/20 | 20/20 |
| `3_gen3_no_collector_material_gen1_kill_volume` | Gen3 | same map, collector bins set to vacuum | Gen1 extent, set locally | 12/20 | **0/20** |

Each folder contains `particles_{gun,fatras,geant4}.root` (particle ntuples),
`particles_{fatras,geant4}_hist.root` (physmon histograms),
`report_{fatras,geant4}.html` (histcmp report against `reference/`, open in a
browser) and `simulation.log`.

## Findings

- **Local runs reproduce the CI.** `1_gen3_as_in_ci` gives exactly the particle
  counts of the Gen3 CI run (Fatras 11 646, Geant4 98 739).
- **Fatras: the calorimeter collector is the dominant cause.** The Gen3 map
  carries the calorimeter material on a thin collector surface outside the
  solenoid, which the Gen1 map does not have (Gen1 ends at the solenoid,
  ~0.45 X0). Without the collector material:
  - the particle count drops from 11 646 to 6 435 (Gen1: 6 172),
  - the `total_x0` overflow above 3 X0 drops from 4 119 to 0,
  - particles with more than 21 hits (electrons curling back into the
    tracker) disappear.

  What remains is +4.3 % secondaries and a slightly different `total_x0`
  shape (KS 0.005), i.e. the newly mapped tracker material. histcmp still
  fails, mainly on ResidualCheck and KolmogorovTest. The kill volume has no
  effect on Fatras (2 and 3 are identical).
- **Geant4: the larger kill volume is the only cause.** Geant4 does not use
  the ACTS material map (1 and 2 are identical). With a kill volume of the
  Gen1 extent, the Geant4 particles are bit-identical to `0_gen1_local` in all
  1000 events. The Gen3 `highestTrackingVolume` extends further out
  (r 1202 → 1245 mm), so Geant4 keeps tracking particles there and produces
  additional secondaries, including hadronic ones. This shifts the random
  number sequence and changes the rest of the event, which looks like
  "RNG wiggling" in the histograms. The remaining 6 particles difference to
  the CI reference (97 135 vs. 97 129) also appear in `0_gen1_local`, so they
  come from the local environment, not from Gen3.

## How the variants were produced

All variants start from `gen3-default` at `dd259a4dc`. The local changes
are stored as patches in `inputs/`:

| Variant | Patch | What it changes |
|---|---|---|
| 0 | `inputs/variant0_gen1.patch` | `physmon_common.py` builds `getOpenDataDetector(gen3=False)` with its default Gen1 map |
| 1 | none | unchanged code, downloads the provisional Gen3 map (release v1) |
| 2 | `inputs/variant2_local_changes.patch` | map URL in `physmon_common.py` points to the collector-free map |
| 3 | `inputs/variant3_local_changes.patch` | as 2, plus a kill volume with the Gen1 extent in `physmon_simulation.py`: `acts.TrackingVolume(acts.Transform3.Identity(), acts.CylinderVolumeBounds(0.0, 1202.0, 4002.0), "Gen1KillVolume")` |

The collector-free map keeps all 105 surface entries (every designated
material key must be present); only the 14 400 bins of each of the three
`CaloMaterialCollector*` surfaces are replaced by
`{"material": {"kind": "vacuum"}, "thickness": 0.0}` using
`inputs/vacuum_collector.jq`.

## How to reproduce

### 0. Environment

Standalone ACTS build with Python bindings and the DD4hep/Geant4 plugins
(here: `~/Documents/PhD/ACTS/acts/build`, environment via
`source ~/setup_acts.sh`). All commands below run from the ACTS source
directory, checked out at `dd259a4dc`, with a clean `CI/physmon/`
(`git status` shows no changes there).

### 1. Collector-free map (variants 2 and 3 only)

Download the provisional Gen3 map and set the collector bins to vacuum.
Compress from a file, not from a pipe: ACTS needs the content size in the
zstd header.

```bash
curl -L -o odd_gen3_map.json.zst \
  https://github.com/LeaBaumann/acts/releases/download/gen3-material-map-provisional-v1/odd_gen3_map.json.zst
zstd -dc odd_gen3_map.json.zst \
  | jq --indent 4 -f <this folder>/inputs/vacuum_collector.jq > odd_gen3_map_nocalo.json
zstd -19 odd_gen3_map_nocalo.json   # -> odd_gen3_map_nocalo.json.zst
```

The patches for variants 2 and 3 contain a `file://` URL with a local path.
Adapt it in `CI/physmon/physmon_common.py` after applying the patch.

### 2. Apply the patch of the variant

```bash
git apply <this folder>/inputs/variant3_local_changes.patch   # example: variant 3
git diff CI/physmon                                          # check
```

### 3. Run the simulation

```bash
python3 CI/physmon/workflows/physmon_simulation.py <outdir> 2>&1 | tee <outdir>/simulation.log
```

This simulates 1000 particle-gun events with Fatras and Geant4 and writes
`particles_{gun,fatras,geant4}.root` to `<outdir>`. The script then fails in
its second part (ttbar) if ACTS is built without Pythia8; this is harmless,
the particle-gun outputs are already written at that point.

### 4. Make the histograms

As in `CI/physmon/phys_perf_mon.sh` (function `simulation`). `generic_plotter.py`
needs `typer`, `uproot`, `hist`, ...; with `uv` they can be pulled in ad hoc:

```bash
for s in fatras geant4; do
  uv run --no-project --python 3.13 \
    --with uproot,typer,hist,pydantic,pyyaml,matplotlib,awkward \
    python Examples/Scripts/generic_plotter.py \
      <outdir>/particles_${s}.root particles <outdir>/particles_${s}_hist.root \
      --silent --config CI/physmon/config/simulation.yml
done
```

### 5. Compare with the reference

`histcmp` needs PyROOT, so it runs with the Python of the ACTS environment.
The Gen1 references are in `reference/` (in general: the hashes are listed
in `CI/physmon/reference.sha256` and the files live in
`ghcr.io/acts-project/physmon-references`).

```bash
for s in fatras geant4; do
  uv run --no-project --python $(which python3) --with histcmp==0.12.0 \
    histcmp <outdir>/particles_${s}_hist.root <this folder>/reference/particles_${s}_hist.root \
      --config CI/physmon/config/standard.toml \
      --label-reference "Gen1 (CI reference)" --label-monitored "<variant label>" \
      --title "${s} particles: <variant label> vs. Gen1 (CI reference)" \
      -o <outdir>/report_${s}.html > <outdir>/histcmp_${s}.log 2>&1
done
```

A non-zero exit code of `histcmp` means at least one comparison failed; the
summary is at the end of `histcmp_*.log`, the plots in `report_*.html`.

### 6. Restore the code

```bash
git checkout CI/physmon/physmon_common.py CI/physmon/workflows/physmon_simulation.py
```

### Saving local changes as a patch

To record new local changes in the same way:

```bash
git diff -- CI/physmon > <this folder>/inputs/<name>.patch   # write the patch
git apply --check <this folder>/inputs/<name>.patch           # later: test if it applies
git apply <this folder>/inputs/<name>.patch                   # later: apply it
```

`git diff` only records the changes relative to the current commit, so note
the base commit (here `dd259a4dc`) next to the patch.
