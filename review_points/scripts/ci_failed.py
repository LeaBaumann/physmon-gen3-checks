"""List the failed histcmp comparisons of the CI physmon reports for gen3-default
@ dd259a4dc (the reports linked in Paul's review comment). Needs internet access."""
import re, urllib.request

BASE = "https://acts-herald.app.cern.ch/view/acts-project/acts/13004175552/html/"
PAGES = [
    "trackfitting_kf/performance_trackfitting", "trackfitting_gx2f/performance_trackfitting",
    "trackfitting_gsf/performance_trackfitting", "trackrefitting_kf/performance_trackrefitting",
    "trackrefitting_gsf/performance_trackrefitting",
    "trackfinding_1muon/truth_smeared/performance_finding_ckf", "trackfinding_1muon/seeded/tracksummary_ckf",
    "trackfinding_ttbar_pu200/performance_fitting_ckf", "trackfinding_ttbar_pu200/performance_finding_ckf_ml_solver",
    "trackfinding_ttbar_pu200/tracksummary_ckf",
]
pat = r'id="plot-\d+".{0,400}?(Passed|Failed)\s*(?:<[^>]+>\s*)*([A-Za-z0-9_]+)'
for p in PAGES:
    html = urllib.request.urlopen(BASE + p + ".html", timeout=300).read().decode(errors="ignore")
    res = re.findall(pat, html, re.S)
    failed = [n for s, n in res if s == "Failed"]
    print(f"== {p}: {len(failed)}/{len(res)} failed\n   " + " ".join(failed))
