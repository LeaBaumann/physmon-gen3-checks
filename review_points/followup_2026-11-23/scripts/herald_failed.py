"""List the failed plots (name and anchor) of saved herald report pages.

Usage: python3 herald_failed.py <page.html> [<page.html> ...]
Pages saved from https://acts-herald.app.cern.ch/view/acts-project/acts/13004175552/html/...
"""
import re
import sys

for fn in sys.argv[1:]:
    t = open(fn).read()
    fails = re.findall(r'<article class="box plot" id="plot-(\d+)">\s*<header class="plot-header">\s*'
                       r'<span class="status-badge status-failure">.*?<h2><a[^>]*>([^<]+)</a>', t, re.S)
    print(f"{fn}: {len(fails)} failed")
    print("   " + " ".join(f"{n}#{p}" for p, n in fails))
