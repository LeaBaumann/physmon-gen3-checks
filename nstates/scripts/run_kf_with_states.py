# copy of CI/physmon/workflows/physmon_trackfitting_kf.py, 1000 events, keeps track states
import tempfile, shutil
from pathlib import Path
import acts
from truth_tracking_kalman import runTruthTrackingKalman
from physmon_common import makeSetup
u = acts.UnitConstants
setup = makeSetup()
with tempfile.TemporaryDirectory() as temp:
    s = acts.examples.Sequencer(events=1000, numThreads=-1, logLevel=acts.logging.INFO)
    tp = Path(temp)
    runTruthTrackingKalman(trackingGeometry=setup.trackingGeometry, field=setup.field,
        digiConfigFile=Path(__import__("os").environ["DIGI"]), outputDir=tp,
        reverseFilteringMomThreshold=0 * u.GeV, reverseFilteringCovarianceScaling=100.0, s=s)
    s.run()
    for f in ["performance_kf.root", "trackstates_kf.root", "tracksummary_kf.root"]:
        shutil.copy(tp / f, setup.outdir / f)
