"""Purity, matched/duplicate tracks and CKF 'explosions' in the forward test.

Usage: python3 fwd_purity_duplicates.py <run dir> <label> [<label> ...]
<run dir>/<variant>/out/<label>/tracksummary_ckf.root, variants gen1, gen3,
gen3nocalo (missing ones are skipped).
"""
import collections
import sys

import awkward as ak
import numpy as np
import uproot

R = sys.argv[1]
BINS = [(2.8, 3.0), (3.0, 3.2), (3.2, 3.5)]
BIG = 20  # a particle with more than BIG tracks counts as a CKF 'explosion'

for label in sys.argv[2:]:
    print(f"===== {label}")
    for v in ["gen1", "gen3", "gen3nocalo"]:
        try:
            f = uproot.open(f"{R}/{v}/out/{label}/tracksummary_ckf.root")
        except FileNotFoundError:
            continue
        t = f[f.keys()[0]]
        a = t.arrays(["event_nr", "t_eta", "nMeasurements", "nMajorityHits",
                      "trackClassification", "majorityParticleId_vertex_primary",
                      "majorityParticleId_particle", "majorityParticleId_generation",
                      "majorityParticleId_sub_particle"])
        F = lambda k: ak.flatten(a[k]).to_numpy()
        ev = np.repeat(a.event_nr.to_numpy(), ak.num(a.t_eta))
        key = list(zip(ev, F("majorityParticleId_vertex_primary"), F("majorityParticleId_particle"),
                       F("majorityParticleId_generation"), F("majorityParticleId_sub_particle")))
        c = collections.Counter(key)
        mult = np.array([c[k] for k in key])
        eta = F("t_eta")
        pur = F("nMajorityHits") / F("nMeasurements").astype(float)
        cl = F("trackClassification")  # 1 = matched, 2 = duplicate
        for lo, hi in BINS:
            m = (eta >= lo) & (eta < hi)
            mm, md, ms = m & (cl == 1), m & (cl == 2), m & (mult <= BIG)
            print(f"{v:11s} eta {lo}-{hi}: tracks {m.sum():5d} purity {pur[m].mean():.4f} | "
                  f"matched {mm.sum():5d} ({pur[mm].mean():.4f}) duplicates {md.sum():5d} "
                  f"({pur[md].mean():.4f}) | without explosions: tracks {ms.sum():5d} "
                  f"purity {pur[ms].mean():.4f}, duplicates {np.sum(ms & (cl == 2)):5d}")
        m = (eta >= 3.2) & (eta < 3.5)
        top = sorted((n for k, n in c.items()), reverse=True)[:5]
        print(f"{'':11s} largest numbers of tracks per particle: {top}")
