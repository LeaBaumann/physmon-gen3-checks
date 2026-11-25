#!/bin/bash
# Build a copy of libActsPluginDD4hep.so with material on only one face per
# endcap disc, without touching the ACTS source tree or build directory:
# compile the patched OpenDataDetectorBuilder.cpp with the exact command of the
# existing build and relink the library into <out>/lib.
# Usage: build_one_face_lib.sh <acts source dir> <acts build dir> <out dir>
# Use it with: export LD_LIBRARY_PATH=<out>/lib:$LD_LIBRARY_PATH
set -euo pipefail
A=$1; B=$2; S=$3
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p $S/src $S/obj $S/lib
cp $A/Plugins/DD4hep/src/OpenDataDetectorBuilder.cpp $S/src/
patch -s -d $S/src -p4 < $here/../inputs/odd_builder_one_disc_face.patch
O=Plugins/DD4hep/CMakeFiles/ActsPluginDD4hep.dir/src/OpenDataDetectorBuilder.cpp.o
cd $B
ninja -t commands $O | tail -1 | sed "s#-o $O#-o $S/obj/ODB.o#; s#-MF [^ ]*#-MF $S/obj/ODB.d#; s#-c $A/Plugins/DD4hep/src/OpenDataDetectorBuilder.cpp#-c $S/src/OpenDataDetectorBuilder.cpp#" > $S/compile.sh
ninja -t commands lib/libActsPluginDD4hep.so | tail -1 | sed "s#-o lib/libActsPluginDD4hep.so#-o $S/lib/libActsPluginDD4hep.so#; s# $O # $S/obj/ODB.o #; s#-Wl,--dependency-file=[^ ]*##" > $S/link.sh
bash $S/compile.sh && bash $S/link.sh
echo "built $S/lib/libActsPluginDD4hep.so"
