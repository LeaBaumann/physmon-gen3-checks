"""Make copies of physmon workflows that keep all their ROOT outputs.

The physmon workflows write into a temporary directory and copy only the
performance files to the output directory. The copies made here additionally
copy every ROOT file of the temporary directory as `all_<name>` (for example
`all_tracksummary_gx2f.root`, `all_performance_gx2f.root`), which
`refit_binning_all.py` needs.

Usage: python3 -I keep_all_outputs.py <acts>/CI/physmon/workflows <work dir> [workflow ...]

Default workflows: physmon_trackfitting_gx2f.py, physmon_trackrefitting_kf.py,
physmon_trackfitting_gsf.py, physmon_trackrefitting_gsf.py. Also copies
physmon_simulation_gsf.py unchanged (the GSF workflows read its output).
"""

import shutil
import sys
from pathlib import Path

ADD = """
    for _f in tp.glob("*.root"):
        shutil.copy(_f, setup.outdir / ("all_" + _f.name))
"""

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
workflows = sys.argv[3:] or [
    "physmon_trackfitting_gx2f.py",
    "physmon_trackrefitting_kf.py",
    "physmon_trackfitting_gsf.py",
    "physmon_trackrefitting_gsf.py",
]
dst.mkdir(parents=True, exist_ok=True)
for name in workflows:
    text = (src / name).read_text()
    assert "    s.run()\n" in text, f"no 's.run()' in {name}"
    (dst / name).write_text(text.replace("    s.run()\n", "    s.run()\n" + ADD, 1))
shutil.copy(src / "physmon_simulation_gsf.py", dst / "physmon_simulation_gsf.py")
print("wrote", ", ".join(workflows), "to", dst)
