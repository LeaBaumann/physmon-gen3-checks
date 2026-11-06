"""Point 2: Gen1 barrel layers: outer approach cylinders vs. module extent.
Needs the ACTS Python environment (Gen1 ODD)."""
import acts, collections, re, itertools
from acts.examples.odd import getOpenDataDetector
det = getOpenDataDetector(gen3=False)
tg = det.trackingGeometry()
gctx = acts.GeometryContext.dangerouslyDefaultConstruct()
info = collections.defaultdict(list)
def visit(s):
    g = s.geometryId
    if g.volume in (17, 24, 29) and g.layer in (2, 4, 6, 8):
        kind = 'approach%d' % g.approach if g.approach else ('sensitive' if g.sensitive else 'layer')
        info[(g.volume, g.layer, kind)].append(s)
tg.visitSurfaces(visit, False)
num = r'(-?[0-9.]+(?:e[-+]?\d+)?)'
for (v, l, k), ss in sorted(info.items()):
    if k == 'sensitive':
        zmax = 0; rmax = 0
        for s in ss:
            txt = s.toString(gctx)
            m = re.search(r'\(hlX, hlY\) = \(' + num + ', ' + num, txt)
            hx, hy = map(float, m.groups()); x0, y0, x1, y1 = -hx, -hy, hx, hy
            for x, y in itertools.product((x0, x1), (y0, y1)):
                p = s.localToGlobal(gctx, acts.Vector2(x, y), acts.Vector3(0, 0, 1))
                zmax = max(zmax, abs(p[2]))
        print(f'vol{v} lay{l} modules: n={len(ss)}, outer module edge |z|max = {zmax:.1f} mm')
    else:
        txt = ss[0].toString(gctx)
        m = re.search(r'\(radius, halfLengthZ[^)]*\) = \(' + num + ', ' + num, txt)
        print(f'vol{v} lay{l} {k:9s}: r = {float(m.group(1)):7.1f} mm, halfLengthZ = {float(m.group(2)):7.1f} mm')
