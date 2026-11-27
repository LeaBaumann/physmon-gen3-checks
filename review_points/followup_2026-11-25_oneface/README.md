# Follow-up of 2026-11-25: material on one endcap disc face

[← review points](../README.md) · [← overview](../../README.md)

Material on one face per endcap disc (point 4, and the nStates question).

| Path | Content |
|---|---|
| `inputs/odd_builder_one_disc_face.patch` | `OpenDataDetectorBuilder.cpp`: endcap layers designate only their `NegativeDisc` face |
| `inputs/local_map_and_seed.patch` | on top of [`../followup_2026-11-23/inputs/forward_electrons.patch`](../followup_2026-11-23/inputs/forward_electrons.patch): material map from `$MATMAP` (local file), seed from `$SEED`, output label from `$LABEL` |
| `scripts/build_one_face_lib.sh` | builds a patched copy of `libActsPluginDD4hep.so` outside the ACTS tree (compile and link commands taken from the existing build); use it via `LD_LIBRARY_PATH` |
| `scripts/run_forward_electrons.sh` | maps one recording twice (both faces / one face) and runs the forward electron test with 3 seeds for each map |
| `scripts/cmp_maps.py` | compares two Gen3 maps surface by surface (binning, empty bins, mean t/X0) |
| `results/forward_electrons_one_face_duplicates.txt` | output of `../followup_2026-11-23/scripts/fwd_purity_duplicates.py`, `both` vs `oneface` |
| `results/forward_electrons_one_face_nstates.txt` | mean nStates / nMeasurements of matched tracks per η bin |
| `results/map_statistics_1M_vs_200k.txt` | provisional map vs a map from only 200k geantinos (same blueprint) |

Mapping statistics matter: a first attempt used a new recording with only
200 000 geantinos. Bins that no geantino crosses get no material, so that map
had far more empty bins in the endcaps (long-strip endcaps 76 % instead of
49 %) and only about half the forward material; where both maps have values
they agree. Its lower material made Gen3 look closer to Gen1, which was an
artefact. All results above therefore use the 1M recording of the provisional
map (`odd_gen3_recording.root`, 1000 events × 1000 tracks).

```bash
source ~/setup_acts.sh
F=<this repo>/review_points/followup_2026-11-25_oneface
$F/scripts/build_one_face_lib.sh <acts> <acts>/build <w>/oneface
# <w>/wf/CI/physmon: copy of CI/physmon with the two patches applied
cd <acts> && $F/scripts/run_forward_electrons.sh <w> odd_gen3_recording.root 1000 <w>/oneface/lib
python3 $F/../followup_2026-11-23/scripts/fwd_purity_duplicates.py <w>/ele/run ele_truth_smeared ele_seed43 ele_seed44
```
