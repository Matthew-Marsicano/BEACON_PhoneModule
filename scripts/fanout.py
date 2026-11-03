"""Plane fanout: give every SMD pad on a plane net (3V3, VCC_SYN on L3; GND on L2) that is not yet connected a
short stub + via, placed where it clears all other-net copper.  Freerouting does not drop vias to planes itself.

Run after route.py (and before reroute.py / stitch.py):  D:/KiCAD/bin/python.exe -I scripts/fanout.py
"""
import math
import os

import pcbnew
from pcbnew import FromMM, ToMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
OX, OY, BW, BH = 100.0, 100.0, 55.0, 78.45
PLANE_NETS = {'3V3', '/CW_Synth/VCC_SYN', 'GND'}
VIA_D, VIA_H, CLR, STUB_W = 0.45, 0.25, 0.2, 0.25

board = pcbnew.LoadBoard(PCB)
board.BuildConnectivity()
conn = board.GetConnectivity()


def mm(v):
    return ToMM(v.x) - OX, ToMM(v.y) - OY


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def rect_dist(p, r):
    x, y = p
    return math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - y, 0, y - r[3]))


copper = []   # (net, kind, geom, halfwidth)
for t in board.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        copper.append((t.GetNetname(), 'c', mm(t.GetPosition()), ToMM(t.GetWidth()) / 2, 'all'))
    else:
        copper.append((t.GetNetname(), 's', (mm(t.GetStart()), mm(t.GetEnd())), ToMM(t.GetWidth()) / 2,
                       t.GetLayer()))
for fp in board.GetFootprints():
    for pd in fp.Pads():
        bb = pd.GetBoundingBox()
        r = (ToMM(bb.GetLeft()) - OX, ToMM(bb.GetTop()) - OY, ToMM(bb.GetRight()) - OX, ToMM(bb.GetBottom()) - OY)
        th = pd.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
        copper.append((pd.GetNetname(), 'r', r, 0, 'all' if th else (pcbnew.B_Cu if fp.IsFlipped() else pcbnew.F_Cu)))
no_via = [z for z in list(board.Zones()) + [z for fp in board.GetFootprints() for z in fp.Zones()]
          if z.GetIsRuleArea() and z.GetDoNotAllowVias()]


def via_ok(x, y, netname):
    if not (0.7 < x < BW - 0.7 and 0.7 < y < BH - 0.7):
        return False
    pt = pcbnew.VECTOR2I(FromMM(OX + x), FromMM(OY + y))
    if any(z.Outline().Contains(pt, -1, FromMM(VIA_D / 2 + 0.05)) for z in no_via):
        return False
    r = VIA_D / 2 + CLR
    for net, kind, g, hw, _layer in copper:
        same = net == netname
        if kind == 'c':
            d = math.hypot(x - g[0], y - g[1]) - hw
            if d < (VIA_D / 2 + 0.25 if same else r):           # hole-to-hole / clearance
                return False
        elif same:
            continue
        elif kind == 's' and seg_dist((x, y), g[0], g[1]) - hw < r:
            return False
        elif kind == 'r' and rect_dist((x, y), g) < r:
            return False
    return True


def stub_ok(a, b, netname, layer):
    for net, kind, g, hw, lyr in copper:
        if net == netname or (lyr != 'all' and lyr != layer):
            continue
        if kind == 'r':
            # sample the stub
            for k in range(11):
                p = (a[0] + (b[0] - a[0]) * k / 10, a[1] + (b[1] - a[1]) * k / 10)
                if rect_dist(p, g) < STUB_W / 2 + CLR:
                    return False
        elif kind == 's':
            for k in range(11):
                p = (a[0] + (b[0] - a[0]) * k / 10, a[1] + (b[1] - a[1]) * k / 10)
                if seg_dist(p, g[0], g[1]) - hw < STUB_W / 2 + CLR:
                    return False
        elif kind == 'c':
            if seg_dist(g, a, b) - hw < STUB_W / 2 + CLR:
                return False
    return True


added = failed = 0
for fp in board.GetFootprints():
    for pd in fp.Pads():
        n = pd.GetNetname()
        if n not in PLANE_NETS or pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            continue
        if conn.GetConnectedItems(pd, [pcbnew.PCB_VIA_T, pcbnew.PCB_ZONE_T]) if False else False:
            continue
        # already connected to its plane? (a via of the same net touching any copper connected to this pad)
        items = conn.GetConnectedItems(pd)
        if any(it.GetClass() == 'PCB_VIA' for it in items) or (n == 'GND' and any(it.GetClass() == 'ZONE' and
                                                                                    it.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu)
                                                                                    for it in items)):
            continue
        layer = pcbnew.B_Cu if fp.IsFlipped() else pcbnew.F_Cu
        cx, cy = mm(pd.GetPosition())
        bb = pd.GetBoundingBox()
        hw, hh = ToMM(bb.GetWidth()) / 2, ToMM(bb.GetHeight()) / 2
        fx, fy = mm(fp.GetPosition())
        cands = []
        for ang in range(0, 360, 30):
            ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            for extra in (0.35, 0.55, 0.8, 1.1):
                d = abs(ux) * hw + abs(uy) * hh + VIA_D / 2 + extra
                x, y = cx + ux * d, cy + uy * d
                # prefer pointing away from the footprint centre
                away = (x - fx) * ux + (y - fy) * uy
                cands.append((extra - 0.001 * away, x, y))
        cands.sort()
        done = False
        for _, x, y in cands:
            if via_ok(x, y, n) and stub_ok((cx, cy), (x, y), n, layer):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pd.GetPosition()); t.SetEnd(pcbnew.VECTOR2I(FromMM(OX + x), FromMM(OY + y)))
                t.SetWidth(FromMM(STUB_W)); t.SetLayer(layer); t.SetNet(pd.GetNet()); board.Add(t)
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pcbnew.VECTOR2I(FromMM(OX + x), FromMM(OY + y)))
                v.SetWidth(FromMM(VIA_D)); v.SetDrill(FromMM(VIA_H)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetNet(pd.GetNet()); board.Add(v)
                copper.append((n, 'c', (x, y), VIA_D / 2, 'all'))
                copper.append((n, 's', ((cx, cy), (x, y)), STUB_W / 2, layer))
                added += 1
                done = True
                break
        if not done:
            failed += 1
            print('no fanout spot for %s pad %s (%s)' % (fp.GetReference(), pd.GetNumber(), n))
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print('plane fanout: %d added, %d without a spot' % (added, failed))
