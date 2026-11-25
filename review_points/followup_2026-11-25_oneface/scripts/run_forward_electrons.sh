#!/bin/bash
# Map the same recording twice (both disc faces / one face) and run the
# forward electron test (3 seeds) with each map.
# Usage: run_forward_electrons.sh <work dir> <recording.root> <n events in recording> <one-face lib dir>
# <work dir>/wf/CI/physmon must hold CI/physmon with
# ../followup_2026-11-23/inputs/forward_electrons.patch and inputs/local_map_and_seed.patch applied.
# Needs: source ~/setup_acts.sh (run from the ACTS source dir for material_mapping.py)
set -u
W=$1; REC=$2; NEV=$3; LIB=$4
A=$(pwd)
for v in both oneface; do
  ( [ $v = oneface ] && export LD_LIBRARY_PATH=$LIB:$LD_LIBRARY_PATH
    mkdir -p $W/map_$v && cd $W/map_$v &&
    python3 $A/Examples/Scripts/Python/material_mapping.py -n $NEV -i $REC -o $W/map_$v/$v --threads 4 > log.txt 2>&1 )
done
export PYTHONPATH=$W/wf/CI/physmon:$PYTHONPATH
for v in both oneface; do
  for seed in 42 43 44; do
    lbl=ele_truth_smeared; [ $seed != 42 ] && lbl=ele_seed$seed
    ( [ $v = oneface ] && export LD_LIBRARY_PATH=$LIB:$LD_LIBRARY_PATH
      mkdir -p $W/ele/$v && cd $W/ele/$v &&
      MATMAP=$W/map_$v/${v}_map.json.zst SEED=$seed LABEL=$lbl \
        python3 $W/wf/CI/physmon/workflows/physmon_trackfinding_1muon.py $W/ele/$v/out > log_$seed.txt 2>&1 )
  done
done
# analysis: ../followup_2026-11-23/scripts/fwd_purity_duplicates.py expects
# variants gen3 / gen3nocalo -> link both / oneface to those names
mkdir -p $W/ele/run && ln -sfn $W/ele/both $W/ele/run/gen3 && ln -sfn $W/ele/oneface $W/ele/run/gen3nocalo
