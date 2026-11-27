# Follow-up of 2026-11-23: review points 1, 3, 4, 5

[← review points](../README.md) · [← overview](../../README.md)

| Path | Content |
|---|---|
| `inputs/physmon_common_gen1.patch` | `CI/physmon/physmon_common.py` for Gen1 (Gen1 geometry and map, Gen1 digi and seeding configs; replace the placeholders). The Gen1 configs: `git show 64a107fa3^:Examples/Configs/odd-digi-smearing-config.json`, `git show 36311fdbc^:Examples/Configs/odd-seeding-config.json` |
| `inputs/physmon_common_gen3_nocollector.patch` | Gen3 with the collector-free map (see step 1 in [SIMULATION.md](../../SIMULATION.md); adapt the path) |
| `inputs/1muon_truth_smeared_only.patch` | 1muon workflow, only `truth_smeared` (point 3) |
| `inputs/forward_muons.patch` | 1muon workflow at η 2.8–3.5, 20 000 events, `truth_smeared` and `seeded`, particle selection ≥ 6 measurements (point 4) |
| `inputs/forward_electrons.patch` | same with 10 electrons per event, 2000 events, also writes `hits.root` and `particles_simulation.root` (point 4); further seeds via `RandomNumbers(seed=43/44)` |
| `results/ttbar_ml_*.txt` | per-bin tables of the ttbar ML-solver profiles (nStates, nMeasurements, purity at the edge) |
| `results/ttbar_error_quantiles.txt`, `results/ttbar_tracksummary_stats.txt` | ttbar error quantiles and histogram statistics |
| `results/1muon_*` | 1muon CI comparison (failed plots, statistics, error quantiles) and the local track-by-track comparison |
| `results/kf_errors_vs_pt.txt` | KF error ratio per pT bin (from `nstates/data/kf_1000ev/`) |
| `results/kf_reswidth_qop_vs_pT_binning_test.txt` | first binning test: `reswidth_qop_vs_pT` of a local Gen3 KF run (10 000 events) refitted with the physmon residual binning and finer binnings (point 1) |
| `results/reswidth_binning_test_all_fitters.txt` | all `reswidth_*` plots of local Gen3 KF, GX2F, KF refit, GSF and GSF refit runs (10 000 events each), refitted with the physmon binning (100 bins) and 10× finer (1000 bins): bins with tracks, bins reproduced, failed fits per binning, median width ratio fine/coarse |
| `results/material_regions.txt`, `results/material_radial.txt` | material per region/η and per radius, Gen1 vs Gen3 map |
| `results/forward_purity.txt`, `results/forward_electrons_duplicates.txt`, `results/forward_electrons_backsplash.txt` | forward muon and electron tests |
| `scripts/` | analysis scripts producing these files (usage in each docstring) |

The 1muon CI files and references used here are in
`../data/ci_gen3/trackfinding_1muon/` and
`../reference/trackfinding_1muon/`. The local run outputs
(tracksummary files, 6–11 MB each) and the material-validation files are not
stored; regenerating them takes a few minutes each:

```bash
source ~/setup_acts.sh
# copy CI/physmon/physmon_common.py and the workflow into a work dir <w>,
# apply the patches there (Gen1 / Gen3 / Gen3 without collector), then:
cd <w> && PYTHONPATH=<w>:<acts>/Examples/Scripts/Python:$PYTHONPATH \
  python3 physmon_trackfinding_1muon.py out
# material validation (from the ACTS source directory)
python3 Examples/Scripts/Python/material_validation.py --gen1 \
  -m build/_deps/odd-src/data/odd-material-maps.root -n 200 -t 100 --eta-range -3.5 3.5 -p -o gen1
python3 Examples/Scripts/Python/material_validation.py \
  -m odd_gen3_map.json.zst -n 200 -t 100 --eta-range -3.5 3.5 -p -o gen3
```

The scripts need `uproot`, `numpy`, `awkward` (e.g. the acts-venv) and take
the file paths as arguments.

Residual binning test of the `reswidth_*` fits (Gen3, current
`physmon_common.py`; `refit_binning_all.py` also needs PyROOT):

```bash
source ~/setup_acts.sh
F=<this repo>/review_points/followup_2026-11-23/scripts
export PYTHONPATH=<acts>/CI/physmon:<acts>/Examples/Scripts/Python:$PYTHONPATH
# KF: run_kf_10k.py is a copy of physmon_trackfitting_kf.py that keeps tracksummary_kf.root
cd <w>/kf10k && DIGI=<acts>/Examples/Configs/odd-digi-smearing-config.json python3 $F/run_kf_10k.py out
# GX2F, KF refit, GSF, GSF refit: workflow copies that keep all ROOT files as all_<name>
python3 -I $F/keep_all_outputs.py <acts>/CI/physmon/workflows <w>/fitruns
cd <w>/fitruns
python3 physmon_trackfitting_gx2f.py out/trackfitting_gx2f
python3 physmon_trackrefitting_kf.py out/trackrefitting_kf
python3 physmon_simulation_gsf.py out/simulation_gsf
# the GSF fit stops on two unmasked FPEs on Gen3 (see ../ci_00c67c41f/README.md),
# so switch the FPE monitoring off for it
ACTS_SEQUENCER_DISABLE_FPEMON=1 python3 physmon_trackfitting_gsf.py out/trackfitting_gsf
python3 physmon_trackrefitting_gsf.py out/trackrefitting_gsf
# refit, e.g. GX2F (KF: <w>/kf10k/out/tracksummary_kf.root <w>/kf10k/out/performance_kf.root)
python3 $F/refit_binning_all.py out/trackfitting_gx2f/all_tracksummary_gx2f.root \
  out/trackfitting_gx2f/all_performance_gx2f.root
```

`refit_binning_all.py` replaces the earlier `refit_binning.py` (only
`reswidth_qop_vs_pT`), which produced `kf_reswidth_qop_vs_pT_binning_test.txt`.
