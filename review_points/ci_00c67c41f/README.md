# CI failures at `00c67c41f` (2026-11-25)

[← overview](../../README.md)

State of the remaining red checks of PR #6273 after the EDM4hep fix (LCG jobs
are green). Hash and physmon reference failures are expected until the
official Gen3 material map is in the ODD repository; everything else is listed
here with cause, fix and how to reproduce it.

| Check | Failure | Cause | Fix | Who |
|---|---|---|---|---|
| `linux_physmon` | reference comparisons | Gen1 references | new references after the official map | after the map |
| `linux_physmon` | `physmon_trackfitting_gsf.py` aborts (ec=1) | 2 unmasked FPEs in the sympy stepper, once each in 10 000 events, only on Gen3 (below) | `// MARK: fpeMask(...)` with a new issue at both lines, or ask Paul | Lea |
| `linux_examples_test` | 9 hash failures (`ckf_tracks` ×3, `geant4`, `strip_space_points[odd]`, `truth_tracking_kalman` ×2, `truth_tracking_gsf`, `refitting`) | Gen1 hashes | new hashes after the official map | after the map |
| `linux_examples_test` | `test_colliderml_truth_tracking[gen1]`: `ThresholdFailure` | the Gen3 seeding selection in `Examples/Configs/odd-seeding-config.json` is used on the Gen1 geometry; Gen3 volume 30 is a Gen1 long-strip volume → `SpacePointMaker` warns "Encountered non-pixel measurement" | `inputs/colliderml_seeding_fix.patch` | Lea (deferred) |
| `linux_examples_test` | `test_colliderml_truth_tracking[gen3]`: hash missing | no reference yet; the Gen3 value `856c19b5…` is identical to the Gen1 reference | same patch (adds the hash) | Lea (deferred) |
| `linux_examples_test`, `lcg_*` | `test_fit_backends_agree[gaussian_with_outliers]`: "no bin where both root and scipy succeeded" | flaky upstream test (#5848), synthetic data without geometry; fails in a different job each run | see below | upstream |
| `gnn_gpu` | `test_gnn_module_map[gpu-*]`: hash | 0 tracks: module map and model in the CI model storage are built for Gen1 module IDs | pin the test to Gen1 (needs Gen1 seeding, strip and digi configs) or a new Gen3 module map/model | Paul / maintainers |

Not seen in CI yet: nine scripts (including `CI/physmon/physmon_common.py`)
download the provisional map to the same file
`$TMPDIR/odd-material-maps-gen3-provisional.json.zst`. Two processes at the same
time (e.g. `pytest -n 3`) can read a half-written file ("zstd frame is likely
truncated"; happened locally). Fix: download to a temporary name and
`os.replace` it, or nothing once the map is in the ODD repository.

## GSF FPEs

`results/gsf_fpe_stacktraces.txt`: FLTUND at `SympyStepperStepImpl.hpp:140`
(`rk4_vacuum_jac`) and FLTOVF at `:203` (`calcStepSizeScaling`,
`stepTolerance / errorEstimate`; the result is clamped to [0.25, 4]
afterwards), both from `GaussianSumFitter` → `MultiStepperLoop::step`. Both are
harmless. The same code runs on Gen1; on Gen3 one step happens to hit this
corner case. Masks are declared in the source, e.g.
`Core/include/Acts/TrackFitting/detail/GsfComponentMerging.hpp:202`;
`CI/check_fpe_masks.py` checks that the issue number exists.

```bash
source ~/setup_acts.sh
G=<w>/gsf; mkdir -p $G/tmp
export PYTHONPATH=<acts>/CI/physmon:<acts>/Examples/Scripts/Python:$PYTHONPATH
cd <acts>
python3 CI/physmon/workflows/physmon_simulation_gsf.py $G/simulation_gsf
# as in CI: fail on unmasked FPEs; own TMPDIR so no other job shares the map download
TMPDIR=$G/tmp ACTS_SEQUENCER_FAIL_ON_UNMASKED_FPE=1 \
  python3 CI/physmon/workflows/physmon_trackfitting_gsf.py $G/trackfitting_gsf 2>&1 | tee $G/log.txt
grep -n -A9 "exceeded configured" $G/log.txt   # → "Encountered 2 unmasked FPEs"
```

## ColliderML

`inputs/colliderml_seeding_fix.patch` (applies to `gen3-default` @ `00c67c41f`
with `git apply`): `runColliderMLTruthTracking` gets a
`geoSelectionConfigFile` argument (default: `Examples/Configs`, Gen3), the
Gen1 branch of the test passes the Gen1 selection shipped with the ODD
(`config/odd-seeding-config.json`, identical to the old
`Examples/Configs` version), the Gen3 hash is added and the "left failing on
purpose" note is removed. Not run locally: the test needs the Arrow plugin.

```bash
# CI sample (3 MB, sha256 942901db…, checked by the script)
export COLLIDERML_DATA_DIR=<w>/colliderml && CI/dependencies/download_colliderml.sh
# a build with -DACTS_BUILD_PLUGIN_ARROW=ON (arrow is in the Spack environment), then
cd Python/Examples/tests && ROOT_HASH_CHECKS=on ACTS_LOG_FAILURE_THRESHOLD=WARNING \
  python3 -m pytest -rs test_colliderml_reader.py
```

Without the Arrow plugin both cases are skipped ("Arrow/Parquet bindings not built").

## `test_fit_backends_agree`

The input is fixed (seed 3, one thread). Run alone it passes every time
locally (5 of 5), also after `test_fpe.py`, `test_geometry.py`,
`test_writer.py` or `test_detectors.py` in the same process. It fails only in
some CI jobs, in a different one each run, so it depends on the state the
pytest worker is in (which tests ran before), not on the geometry. The ROOT fit
(`RootHistogramFit`, `TH1::Fit("gaus", "SQ0")`) uses ROOT's global minimizer
settings; the scipy fit has no global state. Cause not found.
