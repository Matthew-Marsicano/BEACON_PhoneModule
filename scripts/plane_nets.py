"""Plane nets by pours only: delete every (unlocked) track of the plane nets and connect each of their SMD pads to its
plane with its own via - GND to L2 (In1), 3V3 and VCC_SYN to their L3 (In2) areas.  The via goes in the pad when it
fits (JLC POFV fills and caps it), otherwise it overlaps the pad edge; U5 (nRF aQFN) balls get 0.3/0.15 via-in-pad.
A power pad with no room for either keeps a short stub to a via (reported).  The outer GND pours are tuned to reach
into tight spots, then dangling vias, zero-length and duplicate tracks are cleaned up.

Safe on a hand-routed board: only plane-net tracks and dangling/duplicate copper are removed.
Run:  D:/KiCAD/bin/python.exe -I scripts/plane_nets.py [NET,NET,...]
"""
import math
import os
import sys

import pcbnew
from pcbnew import FromMM, ToMM

PRJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PRJ, 'BEACON_PhoneModule.kicad_pcb')
PLANES = {'GND': pcbnew.In1_Cu, '3V3': pcbnew.In2_Cu, '/CW_Synth/VCC_SYN': pcbnew.In2_Cu}
NETS = sys.argv[1].split(',') if len(sys.argv) > 1 else list(PLANES)
VIA = (0.45, 0.25)                 # standard JLC via (the DRC minimum outside U5)
VIA_U5 = (0.3, 0.15)               # nRF via-in-pad (rule 'nRF52840 inner-ring via-in-pad')
CLR, CLR_U5, EDGE, HOLE2HOLE = 0.15, 0.08, 0.35, 0.2
STUB_W = 0.25

board = pcbnew.LoadBoard(PCB)
COPPER = [l for l in board.GetEnabledLayers().CuStack()]
graveyard = []   # removed items must stay referenced: if SWIG frees their wrappers the board's type table breaks


def remove(item):
    board.Remove(item)
    graveyard.append(item)


def zones():
    return [board.GetArea(i) for i in range(board.GetAreaCount())]


def P(x, y):
    return pcbnew.VECTOR2I(int(x), int(y))


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def xy(v):
    return (v.x, v.y)


codes = {board.FindNet(n).GetNetCode(): n for n in NETS}

# ---------------------------------------------------------------- 1) no plane-net tracks
gone = 0
for t in [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetNetCode() in codes and not t.IsLocked()]:
    remove(t)
    gone += 1
print('plane-net tracks removed:', gone)

# ---------------------------------------------------------------- 2) pour settings
for z in zones():
    if z.GetIsRuleArea() or z.GetNetname() not in PLANES:
        continue
    z.SetMinThickness(FromMM(0.15))
    z.SetThermalReliefGap(FromMM(0.2))
    z.SetThermalReliefSpokeWidth(FromMM(0.25))
    inner = not z.GetLayerSet().Contains(pcbnew.F_Cu) and not z.GetLayerSet().Contains(pcbnew.B_Cu)
    # planes: solid; outer pours: solid to SMD pads (no starved spokes on tiny pads), reliefs on PTH for soldering
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if inner else pcbnew.ZONE_CONNECTION_THT_THERMAL)

# ---------------------------------------------------------------- 3) a via for every plane-net pad
outline = pcbnew.SHAPE_POLY_SET()
board.GetBoardPolygonOutlines(outline, True)
edges = []
for k in range(outline.OutlineCount()):
    ch = outline.Outline(k)
    for i in range(ch.SegmentCount()):
        sg = ch.CSegment(i)
        edges.append((xy(sg.A), xy(sg.B)))
no_via = [z for z in zones() + [z for fp in board.GetFootprints() for z in fp.Zones()]
          if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
plane_zones = [z for z in zones() if not z.GetIsRuleArea() and (z.GetLayerSet().Contains(pcbnew.In1_Cu) or
                                                                   z.GetLayerSet().Contains(pcbnew.In2_Cu))]
pads = [pd for fp in board.GetFootprints() for pd in fp.Pads()]
tracks = [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA']
vias = [t for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
u5_cy = board.FindFootprintByReference('U5').GetCourtyard(pcbnew.F_CrtYd)


def on_plane(netname, pt):
    """the via at pt lands in this net's plane area (and not in a higher-priority other-net area on that layer)"""
    layer = PLANES[netname]
    mine = [z for z in plane_zones if z.GetLayerSet().Contains(layer) and z.GetNetname() == netname
            and z.Outline().Contains(pt)]
    if not mine:
        return False
    prio = max(z.GetAssignedPriority() for z in mine)
    return not any(z.GetLayerSet().Contains(layer) and z.GetNetname() != netname and z.GetAssignedPriority() > prio
                   and z.Outline().Contains(pt, -1, FromMM(0.4)) for z in plane_zones)


def via_fits(x, y, nc, d, h, clr):
    r = FromMM(d / 2)
    pt = P(x, y)
    if not outline.Contains(pt) or min(seg_dist((x, y), a, b) for a, b in edges) < FromMM(EDGE + d / 2):
        return False
    if any(z.Outline().Contains(pt, -1, r) for z in no_via) or not on_plane(codes[nc], pt):
        return False
    for pd in pads:
        if pd.GetNetCode() != nc and pd.HitTest(pt, r + FromMM(clr)):
            return False
        if pd.HasHole():
            hs = max(pd.GetDrillSize().x, pd.GetDrillSize().y) / 2
            if math.hypot(x - pd.GetPosition().x, y - pd.GetPosition().y) < hs + FromMM(h / 2 + HOLE2HOLE):
                return False
    for t in tracks:
        if t.GetNetCode() != nc and seg_dist((x, y), xy(t.GetStart()), xy(t.GetEnd())) < r + t.GetWidth() / 2 + FromMM(clr):
            return False
    for v in vias:
        dd = math.hypot(x - v.GetPosition().x, y - v.GetPosition().y)
        if dd < FromMM(h / 2 + HOLE2HOLE) + v.GetDrillValue() / 2 or \
                (v.GetNetCode() != nc and dd < r + v.GetWidth(pcbnew.F_Cu) / 2 + FromMM(clr)):
            return False
    return True


def add_via(x, y, net, d, h):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(P(x, y)); v.SetWidth(FromMM(d)); v.SetDrill(FromMM(h))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(net)
    board.Add(v)
    vias.append(v)


def stub_ok(a, b, nc, layer):
    for t in tracks:
        if t.GetNetCode() != nc and t.GetLayer() == layer:
            for k in range(11):
                p = (a[0] + (b[0] - a[0]) * k / 10, a[1] + (b[1] - a[1]) * k / 10)
                if seg_dist(p, xy(t.GetStart()), xy(t.GetEnd())) < t.GetWidth() / 2 + FromMM(STUB_W / 2 + CLR):
                    return False
    for pd in pads:
        if pd.GetNetCode() != nc and pd.IsOnLayer(layer):
            for k in range(11):
                p = (a[0] + (b[0] - a[0]) * k / 10, a[1] + (b[1] - a[1]) * k / 10)
                if pd.HitTest(P(*p), FromMM(STUB_W / 2 + CLR)):
                    return False
    return True


stats = {n: dict(have=0, in_pad=0, edge=0, stub=0, none=[]) for n in NETS}
for fp in board.GetFootprints():
    in_u5 = fp.GetReference() == 'U5'
    for pd in fp.Pads():
        nc = pd.GetNetCode()
        if nc not in codes or pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            continue
        st = stats[codes[nc]]
        if any(pd.HitTest(v.GetPosition(), v.GetWidth(pcbnew.F_Cu) // 2) for v in vias if v.GetNetCode() == nc):
            st['have'] += 1
            continue
        c = pd.GetPosition()
        bb = pd.GetBoundingBox()
        w, h = bb.GetWidth(), bb.GetHeight()
        done = False
        if in_u5:                                  # aQFN ball: centred 0.3/0.15 via-in-pad only
            if via_fits(c.x, c.y, nc, VIA_U5[0], VIA_U5[1], CLR_U5):
                add_via(c.x, c.y, pd.GetNet(), *VIA_U5); st['in_pad'] += 1
            else:
                st['none'].append('%s.%s' % (fp.GetReference(), pd.GetNumber()))
            continue
        d, hole = VIA
        # a) centred in the pad (also try a few offsets inside large pads)
        if min(w, h) >= FromMM(d + 0.05):
            dx, dy = max(0, (w - FromMM(d)) / 2 - FromMM(0.05)), max(0, (h - FromMM(d)) / 2 - FromMM(0.05))
            for ox, oy in ((0, 0), (dx, 0), (-dx, 0), (0, dy), (0, -dy)):
                if pd.HitTest(P(c.x + ox, c.y + oy), 0) and via_fits(c.x + ox, c.y + oy, nc, d, hole, CLR):
                    add_via(c.x + ox, c.y + oy, pd.GetNet(), d, hole); st['in_pad'] += 1; done = True
                    break
        fx, fy = fp.GetPosition().x, fp.GetPosition().y
        # b) via overlapping the pad edge (0.1 mm into the pad), pointing away from the part
        if not done:
            cands = []
            for ang in range(0, 360, 15):
                ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                reach = abs(ux) * w / 2 + abs(uy) * h / 2 + FromMM(d / 2 - 0.1)
                x, y = c.x + ux * reach, c.y + uy * reach
                cands.append((-((x - fx) * ux + (y - fy) * uy), x, y))
            for _, x, y in sorted(cands):
                if pd.HitTest(P(x, y), FromMM(d / 2 - 0.02)) and via_fits(x, y, nc, d, hole, CLR):
                    add_via(x, y, pd.GetNet(), d, hole); st['edge'] += 1; done = True
                    break
        # c) power pads only (GND has the outer pours): shortest stub to a via
        if not done and codes[nc] != 'GND':
            layer = pcbnew.B_Cu if fp.IsFlipped() else pcbnew.F_Cu
            cands = []
            for ang in range(0, 360, 15):
                ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                for extra in (0.3, 0.5, 0.8, 1.2, 1.6):
                    reach = abs(ux) * w / 2 + abs(uy) * h / 2 + FromMM(d / 2 + extra)
                    cands.append((extra, c.x + ux * reach, c.y + uy * reach))
            for _, x, y in sorted(cands):
                if via_fits(x, y, nc, d, hole, CLR) and stub_ok(xy(c), (x, y), nc, layer):
                    t = pcbnew.PCB_TRACK(board)
                    t.SetStart(c); t.SetEnd(P(x, y)); t.SetWidth(FromMM(STUB_W)); t.SetLayer(layer); t.SetNet(pd.GetNet())
                    board.Add(t); tracks.append(t)
                    add_via(x, y, pd.GetNet(), d, hole); st['stub'] += 1; done = True
                    break
        if not done:
            st['none'].append('%s.%s' % (fp.GetReference(), pd.GetNumber()))
for n, st in stats.items():
    print('%s pads: %d had a via, %d via-in-pad, %d via on pad edge, %d short stub, %d without a via%s'
          % (n, st['have'], st['in_pad'], st['edge'], st['stub'], len(st['none']),
             (' (pour only)' if n == 'GND' else ' (NOT CONNECTED)') + (': ' + ' '.join(st['none']) if st['none'] else '')))

pcbnew.ZONE_FILLER(board).Fill(board.Zones())

# ---------------------------------------------------------------- 4) cleanup


def touches(v):
    """copper layers on which something of the via's net touches it"""
    hit = set()
    p, r = v.GetPosition(), v.GetWidth(pcbnew.F_Cu) // 2
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_VIA' or t.GetNetCode() != v.GetNetCode():
            continue
        if seg_dist(xy(p), xy(t.GetStart()), xy(t.GetEnd())) <= r + t.GetWidth() / 2:
            hit.add(t.GetLayer())
    for pd in pads:
        if pd.GetNetCode() == v.GetNetCode() and pd.HitTest(p, r):
            hit.update(l for l in COPPER if pd.IsOnLayer(l))
    for z in zones():
        if z.GetIsRuleArea() or z.GetNetCode() != v.GetNetCode():
            continue
        for l in z.GetLayerSet().CuStack():
            if z.HitTestFilledArea(l, p, r):
                hit.add(l)
    return hit


dang = 0
for v in [t for t in board.GetTracks() if t.GetClass() == 'PCB_VIA' and not t.IsLocked()]:
    if len(touches(v)) < 2:
        remove(v)
        dang += 1
print('dangling vias removed:', dang)

zero = dup = 0
seen = set()
for t in [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA']:
    a, b = xy(t.GetStart()), xy(t.GetEnd())
    if a == b:
        remove(t); zero += 1
        continue
    key = (t.GetNetCode(), t.GetLayer(), t.GetWidth()) + tuple(sorted((a, b)))
    if key in seen:
        remove(t); dup += 1
    seen.add(key)
print('zero-length tracks removed: %d, duplicates removed: %d' % (zero, dup))

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print('saved', PCB)
