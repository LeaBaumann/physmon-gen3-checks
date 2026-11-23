# copy of CI/physmon/workflows/physmon_trackfitting_kf.py, 10000 events, keeps tracksummary_kf.root
# (needs DIGI=<digi config> and PYTHONPATH with CI/physmon and Examples/Scripts/Python)
import tempfile, shutil
from pathlib import Path
import acts
from truth_tracking_kalman import runTruthTrackingKalman
from physmon_common import makeSetup
u = acts.UnitConstants
setup = makeSetup()
with tempfile.TemporaryDirectory() as temp:
    s = acts.examples.Sequencer(events=10000, numThreads=-1, logLevel=acts.logging.INFO)
    tp = Path(temp)
    runTruthTrackingKalman(trackingGeometry=setup.trackingGeometry, field=setup.field,
        digiConfigFile=Path(__import__("os").environ["DIGI"]), outputDir=tp,
        reverseFilteringMomThreshold=0 * u.GeV, reverseFilteringCovarianceScaling=100.0, s=s)
    s.run()
    for f in ["performance_kf.root", "tracksummary_kf.root"]:
        shutil.copy(tp / f, setup.outdir / f)
